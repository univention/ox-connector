# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# included
import asyncio
import json
import logging
import traceback
from importlib.metadata import version
from requests.exceptions import ConnectionError, HTTPError, Timeout

# 3rd party
from univention.provisioning.consumer.api import (
    MessageHandler,
    ProvisioningConsumerClient,
)
from univention.provisioning.models.message import ProvisioningMessage

# internal
from config import (
    OXConsumerSettings,
    get_ox_consumer_settings,
)
from univention.ox.provisioning.models import TriggerObject
from univention.ox.provisioning import helpers, run
from univention.ox.provisioning.db import (
    get_old,
    get_task,
    create_task_from_old,
    get_tasks,
    increment_error_count,
    move_task_to_old,
    move_task_to_morgue,
    remove_task,
    remove_old,
    enqueue_task,
    store_relation,
    remove_relation,
    get_relation_src,
    initialize_db,
)

LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(module)s.%(funcName)s:%(lineno)d] %(message)s"
logger = logging.getLogger(__name__)


def obj_from_row(row):
    """Create a TriggerObject from a DB task row."""
    obj = TriggerObject(
        row.obj_id,
        row.udm_module,
        row.dn,
        json.loads(row.attrs) if row.attrs else None,
        [],
        None,
    )

    def load_old():
        old = get_old(None, row.obj_id)
        if old:
            obj.old_distinguished_name = old.dn
            obj.old_attributes = json.loads(old.attrs)
            obj.old_options = []
        obj._old_loaded = True

    obj.load_old = load_old
    return obj


def _update_group_queue(entry_uuid):
    """Update group queue by creating a task from old data. Standalone implementation."""
    if get_task(entry_uuid):
        logger.info(
            "Asked to add %s to the task queue. But it already exists. Doing nothing.",
            entry_uuid,
        )
    else:
        create_task_from_old(entry_uuid)
        logger.info("Added %s to the task queue", entry_uuid)


def _get_old_object(distinguished_name, obj_id=None):
    logger.info("Loading old object for %s", obj_id or distinguished_name)
    old = get_old(distinguished_name, obj_id)
    if old:
        return obj_from_row(old)

    return None


helpers.get_old_obj = _get_old_object
helpers.update_group_queue = _update_group_queue
helpers.add_relation = store_relation
helpers.remove_complete_relation = remove_relation
helpers.search_src_of_relation = get_relation_src


# Task processing order (same as listener_trigger)
# Format: (udm_module, empty_attributes_filter)
# Derive listener topics from this list using: {m for m, _ in TASK_PROCESSING_ORDER}
TASK_PROCESSING_ORDER = [
    ("oxmail/oxcontext", False),
    ("oxmail/accessprofile", None),
    ("users/user", None),
    ("groups/group", None),
    ("oxmail/functional_account", None),
    ("oxmail/shared_account_permission", None),
    ("oxmail/shared_account", None),
    ("oxresources/oxresources", None),
    ("oxmail/oxcontext", True),
]

# Topics are derived from TASK_PROCESSING_ORDER — unique UDM module names
TOPICS = {module for module, _ in TASK_PROCESSING_ORDER}


class OXConsumer:
    def __init__(self, settings: OXConsumerSettings | None = None):
        self.settings = settings or get_ox_consumer_settings()

    async def start_listening_for_changes(
        self,
        provisioning_client: type[ProvisioningConsumerClient],
        message_handler: type[MessageHandler],
    ) -> None:
        logger.info("Listening for changes in topics: %r", TOPICS)
        async with provisioning_client() as client:
            await message_handler(client, [self.handle_message]).run()

    async def handle_message(self, message: ProvisioningMessage):
        """
        The MessageHandler calls this method for every provisioning message that the consumer receives.
        If this method returns, the message will be acknowledged and this function will be called with the next message.
        If this method throws an exception, the message won't be acknowledged and the same message will be redelivered.

        Exceptions are not caught by the MessageHandler; they are re-raised instead.
        This stops the process, and the consumer relies on the platform (Kubernetes, Docker) to restart it.
        This allows the consumer to restart with a clean state and re-establish its network connections.
        It also clearly communicates the failure to the Administrator.
        """
        topic = message.topic
        if topic not in TOPICS:
            logger.warning(
                "Ignoring a message in the queue with the wrong topic: %r",
                topic,
            )
            return

        body = message.body
        logger.info(
            "Received message with topic: %s, sequence_number: %d, num_delivered: %d",
            topic,
            message.sequence_number,
            message.num_delivered,
        )
        logger.debug("Message body: %r", body)

        # We ignore body.old because it is read from the DB when processing the task
        # having attributes None in case of delete is required for task to behave correctly
        obj_attrs = None
        if body.new:
            obj_id = body.new["properties"]["univentionObjectIdentifier"]
            obj_dn = helpers.normalized_dn(body.new.get("dn"))
            udm_module = body.new["objectType"]
            obj_attrs = body.new.get("properties")
        elif body.old:
            obj_id = body.old["properties"]["univentionObjectIdentifier"]
            obj_dn = helpers.normalized_dn(body.old.get("dn"))
            udm_module = body.old["objectType"]

        logger.info("Enqueuing task for %s (%s)", obj_id, udm_module)
        enqueue_task(
            obj_id=obj_id,
            udm_module=udm_module,
            dn=obj_dn,
            attrs=obj_attrs,
        )

        # Drain all pending tasks after enqueuing the new one
        self.process_all_tasks(self.settings.ox_connector_stop_on_error)

    def process_all_tasks(self, stop_on_error: bool) -> None:
        """
        Process all pending tasks from the queue in priority order.

        Stops on error unless the task is an oxcontext (which always stops processing)
        or stop_on_error is False (in which case errors go to morgue and processing continues).
        """
        for udm_module, empty_attributes in TASK_PROCESSING_ORDER:
            for task in get_tasks(udm_module, empty_attributes):
                try:
                    logger.info("Processing Task %s", task)
                    obj = obj_from_row(task)
                    obj.load_old()
                    logger.info("... %r", obj)
                    run(obj)
                except (HTTPError, ConnectionError, Timeout) as exc:
                    logger.error("Error while handling %s", task)
                    increment_error_count(task.id)
                    logger.exception(exc)
                    # Connection errors always stop processing
                    return
                except Exception as exc:
                    increment_error_count(task.id)
                    logger.error("Error while handling %s", task)
                    logger.exception(exc)
                    if stop_on_error or task.udm_module == "oxmail/oxcontext":
                        # oxcontext failures always stop; others respect stop_on_error
                        return
                    move_task_to_morgue(task.id, traceback.format_exc())
                    # Continue to next task after morgue
                    continue
                else:
                    if obj.was_deleted():
                        remove_old(obj.old_distinguished_name)
                        remove_task(task.id)
                    else:
                        move_task_to_old(task.id, obj.attributes)

    async def run(self) -> None:
        """Run the message listener. Tasks are drained synchronously after each message."""
        await self.start_listening_for_changes(
            ProvisioningConsumerClient,
            MessageHandler,
        )


def main() -> None:
    settings = get_ox_consumer_settings()
    logging.basicConfig(format=LOG_FORMAT, level=settings.log_level)
    logger.info(
        "Using 'nubus-provisioning-consumer' library version %r.",
        version("nubus-provisioning-consumer"),
    )

    # Initialize the SQL database
    logger.info(
        "Initializing SQL database at %r",
        settings.db_path,
    )
    try:
        initialize_db()
    except Exception:
        logger.error("Failed to initialize database. Shutting down.")
        raise

    consumer = OXConsumer(settings)

    try:
        asyncio.run(consumer.run())
    except KeyboardInterrupt:
        logger.info("Program interrupted by user (Ctrl+C). Shutting down...")


if __name__ == "__main__":
    main()

# [EOF]
