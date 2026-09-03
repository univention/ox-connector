#!/usr/bin/env python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# included
import argparse
import asyncio
import json
import socket
import sys
import traceback
import time
from importlib.metadata import version

# internal
from config import (
    OXConsumerSettings,
    get_ox_consumer_settings,
)

# 3rd party
from lancelog import logger, setup_logging
from univention.provisioning.consumer.api import (
    MessageHandler,
    ProvisioningConsumerClient,
)
from univention.provisioning.models.message import ProvisioningMessage

from logging_context import get_job_id, set_job_id
from requests.exceptions import ConnectionError, HTTPError, Timeout
from univention.ox.provisioning.models import TriggerObject
from univention.ox.provisioning import helpers, run

# Abstract unix domain socket path (null-prefixed = abstract namespace)
SOCKET_PATH = "\0ox-connector-consumer"

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


def build_arg_parser() -> argparse.ArgumentParser:
    """Build and return the argument parser for this module."""
    parser = argparse.ArgumentParser(
        prog="consumer.py",
        description="OX Connector — Nubus provisioning consumer",
    )
    parser.add_argument(
        "--process-all-tasks",
        action="store_true",
        help="Drain the entire task queue then exit (no listener). "
        "Ignored when run as primary; forwarded to primary instead.",
    )
    return parser


class SocketGuard:
    """Abstract unix domain socket guard — ensures only one consumer runs.

    Primary instance binds the socket and starts an asyncio task to accept
    forwarded CLI args from secondary instances.  Commands are executed
    directly inside the accept loop so the primary can act while waiting
    for provisioning messages.

    Secondary instances try to bind, receive ``Address in use``, connect to
    the socket, forward their parsed args, and exit.
    """

    def __init__(self):
        self.sock = None
        self._primary = False

    # ── primary (bind + listen) ──────────────────────────────────────

    def create_socket(self):
        """Bind the abstract socket and return *True* when this process
        becomes the primary instance."""
        self.sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        self.sock.bind(SOCKET_PATH)
        self.sock.listen(5)
        self.sock.setblocking(False)
        self._primary = True
        logger.info("SocketGuard: primary instance (abstract socket bound)")
        return True

    async def start_server(
        self,
        consumer: "OXConsumer",
        settings: OXConsumerSettings,
    ):
        """Set consumer and start the server async task."""
        self._consumer = consumer
        self._settings = settings
        loop = asyncio.get_running_loop()
        loop.create_task(self._accept_loop())
        logger.info("SocketGuard: primary instance (abstract socket bound)")
        return True

    async def _accept_loop(self):
        """Accept forwarded-arg connections from secondary instances
        and execute commands directly."""

        async def _handle(reader, writer):
            # db class check availability of some ebv vars at import time. This
            # is not required for the secondary
            from univention.ox.provisioning.db import DBSession

            try:
                raw = await reader.read(65536)
                msg = json.loads(raw)
                logger.info(
                    "Received forwarded CLI args from secondary: %s",
                    msg,
                )
                if msg.get("process_all_tasks"):
                    logger.info("Executing process-all-tasks from secondary")
                    with DBSession() as db:
                        self._consumer._process_all_tasks_with_db(
                            db,
                            self._settings.ox_connector_stop_on_error,
                        )
            except (json.JSONDecodeError, OSError, TypeError):
                pass
            finally:
                writer.close()
                await writer.wait_closed()

        try:
            server = await asyncio.start_unix_server(_handle, sock=self.sock)
            async with server:
                await server.serve_forever()
        except (OSError, ConnectionError):
            pass

    @property
    def is_primary(self):
        return self._primary

    # ── secondary (connect + forward) ────────────────────────────────

    async def forward_args(self, parsed_args: argparse.Namespace):
        """Connect to the primary, send parsed args as JSON, and return True
        if the forward succeeded."""
        try:
            sock = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
            sock.settimeout(5)
            sock.connect(SOCKET_PATH)
            sock.sendall(json.dumps(vars(parsed_args)).encode())
            sock.close()
            logger.info(
                "Secondary consumer: forwarded CLI args to primary, exiting",
            )
            return True
        except (OSError, ConnectionError):
            logger.warning(
                "Secondary consumer: could not connect to primary, "
                "proceeding as standalone",
            )
            return False


# ── OXConsumer ────────────────────────────────────────────────────────


class OXConsumer:
    def __init__(self, settings: OXConsumerSettings | None = None):
        self.settings = settings or get_ox_consumer_settings()

    async def start_listening_for_changes(
        self,
        provisioning_client: type[ProvisioningConsumerClient],
        message_handler: type[MessageHandler],
    ) -> None:
        logger.info("Listening for changes in topics", topics=TOPICS)
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
        set_job_id(message.sequence_number)
        if topic not in TOPICS:
            logger.warning(
                "Ignoring a message in the queue with the wrong topic",
                topic=topic,
            )
            return

        body = message.body
        logger.info(
            "Received message",
            topic=topic,
            sequence_number=message.sequence_number,
            num_delivered=message.num_delivered,
        )
        logger.debug("Message body", body=body)

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
        else:
            logger.warning("Message has neither new nor old body, skipping")
            return

        # db class check availability of some ebv vars at import time. This
        # is not required for the secondary
        from univention.ox.provisioning.db import DBSession

        # Use single session for enqueuing and processing
        with DBSession() as db:
            logger.info("Enqueuing task", obj=obj_id, module=udm_module)
            db.enqueue_task(
                obj_id=obj_id,
                udm_module=udm_module,
                dn=obj_dn,
                attrs=obj_attrs,
            )

            # commit new task so we can process it
            db.commit()

            # Drain all pending tasks after enqueuing the new one
            self._process_all_tasks_with_db(
                db,
                self.settings.ox_connector_stop_on_error,
            )
            set_job_id(None)

    def _obj_from_row(self, row, db):
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
            old = db.get_old(None, row.obj_id)
            if old:
                obj.old_distinguished_name = old.dn
                obj.old_attributes = (
                    json.loads(old.attrs) if old.attrs else None
                )
                obj.old_options = []
            obj._old_loaded = True

        obj.load_old = load_old
        return obj

    def _process_all_tasks_with_db(
        self,
        db,
        stop_on_error: bool,
    ) -> None:
        """
        Process all pending tasks from the queue using the provided DBSession.

        Stops on error when stop_on_error is True or when the failing task is an oxcontext task;
        otherwise the task is moved to the morgue and processing continues.
        """
        log_level = get_ox_consumer_settings().log_level
        while db.contain_tasks():
            for udm_module, empty_attributes in TASK_PROCESSING_ORDER:
                for task in db.get_tasks(udm_module, empty_attributes):
                    try:
                        logger.info("Processing Task", task=task)
                        obj = self._obj_from_row(task, db)
                        obj.load_old()
                        logger.info("Load old object from db", obj=obj)

                        def _update_group_queue(entry_uuid):
                            """Update group queue by creating a task from old data."""
                            if db.get_task(entry_uuid):
                                logger.info(
                                    "Asked to add %s to the task queue. But it already exists. Doing nothing.",
                                    entry_uuid,
                                )
                                return

                            db.create_task_from_old(entry_uuid)
                            logger.info(
                                "Added entry to the task queue",
                                entry=entry_uuid,
                            )

                        def _get_old_object(distinguished_name, obj_id=None):
                            logger.info(
                                "Loading old object for id/dn",
                                id=obj_id,
                                dn=distinguished_name,
                            )
                            old = db.get_old(distinguished_name, obj_id)
                            if old:
                                return self._obj_from_row(old, db)

                            return None

                        helpers.get_old_obj = _get_old_object
                        helpers.update_group_queue = _update_group_queue
                        helpers.add_relation = db.add_relation
                        helpers.remove_complete_relation = db.remove_relation
                        helpers.search_src_of_relation = db.get_relation_src

                        run(obj)
                    except (HTTPError, ConnectionError, Timeout) as exc:
                        logger.error("Error while handling", task=task)
                        error_count = db.increment_error_count(task.id)
                        logger.exception(exc)
                        # Connection errors always stop processing
                        # sleep for increments
                        delay = error_count * 5 if error_count < 240 else 1200
                        if log_level == 'DEBUG':
                            logger.debug("Skipping sleep for faster debugging")
                        else:
                            logger.info(
                                "Waiting for retry. In case you want to retry now, restart the connector",
                                delay=delay,
                            )
                            db.commit()
                            time.sleep(delay)
                        break
                    except Exception as exc:
                        error_count = db.increment_error_count(task.id)
                        logger.error("Error while handling", task=task)
                        logger.exception(exc)
                        if (
                            stop_on_error
                            or task.udm_module == "oxmail/oxcontext"
                        ):
                            # oxcontext failures always stop; others respect stop_on_error
                            # sleep for increments
                            delay = (
                                error_count * 5 if error_count < 240 else 1200
                            )
                            if log_level == 'DEBUG':
                                logger.debug(
                                    "Skipping sleep for faster debugging",
                                )
                            else:
                                logger.info(
                                    "Waiting for retry. In case you want to retry now, restart the connector",
                                    delay=delay,
                                )
                                db.commit()
                                time.sleep(delay)
                            break
                        db.move_task_to_morgue(task.id, traceback.format_exc())
                        # Continue to next task after morgue
                        continue
                    else:
                        if obj.was_deleted():
                            db.delete_old(dn=obj.old_distinguished_name)
                            db.remove_task(task.id)
                        else:
                            db.move_task_to_old(task.id, obj.attributes)

                # manual commit here, so new tasks are created
                db.commit()

    async def run(self, provisioning_consumer_client=None) -> None:
        # db class check availability of some ebv vars at import time. This
        # is not required for the secondary
        from univention.ox.provisioning.db import DBSession

        # Drain all pending tasks for example from initializing
        with DBSession() as db:
            self._process_all_tasks_with_db(
                db,
                self.settings.ox_connector_stop_on_error,
            )

        """Run the message listener. Tasks are drained synchronously after each message."""
        await self.start_listening_for_changes(
            (
                provisioning_consumer_client
                if provisioning_consumer_client
                else ProvisioningConsumerClient
            ),
            MessageHandler,
        )


async def _run_consumer_with_guard(provisioning_consumer_client=None):
    """Try to become primary (bind socket).  If that fails, forward args
    to the existing primary and exit."""
    parser = build_arg_parser()
    parsed_args = parser.parse_args()

    guard = SocketGuard()

    try:
        guard.create_socket()
    except OSError as exc:
        if exc.errno == 98:  # EADDRINUSE — socket already bound
            logger.info(
                "Socket already bound — another consumer instance is running",
            )
            # Try to forward our parsed CLI args to the primary
            forwarded = await guard.forward_args(parsed_args)
            if not forwarded:
                # Primary is unreachable — fall through and run standalone
                logger.warning(
                    "Could not reach primary; running as standalone",
                )
            else:
                # Forwarded successfully — exit
                sys.exit(0)
        else:
            raise

    # ── Primary path ────────────────────────────────────────────────

    # db class check availability of some ebv vars at import time. This
    # is not required for the secondary
    from univention.ox.provisioning.db import (
        DB_URL,
        initialize_db,
    )

    logger.info(
        "Using 'nubus-provisioning-consumer' library",
        version=version("nubus-provisioning-consumer"),
    )

    settings = get_ox_consumer_settings()
    setup_logging(level=settings.log_level, request_id_func=get_job_id)

    if settings.log_level == "DEBUG":
        import logging

        logging.getLogger("zeep").setLevel(logging.DEBUG)
        logging.getLogger("zeep.transports").setLevel(logging.DEBUG)

    # Initialize the SQL database
    logger.info(
        "Initializing SQL database",
        url=DB_URL,
    )
    try:
        initialize_db()
    except Exception:
        logger.error("Failed to initialize database. Shutting down.")
        raise

    consumer = OXConsumer(settings)
    await guard.start_server(consumer, settings)

    try:
        await consumer.run(provisioning_consumer_client)
    except KeyboardInterrupt:
        logger.info("Program interrupted by user (Ctrl+C). Shutting down...")
        sys.exit(0)


def main() -> None:
    asyncio.run(_run_consumer_with_guard())


if __name__ == "__main__":
    main()

# [EOF]
