# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# included
import asyncio
import logging
import time
from importlib.metadata import version
from typing import Any, Dict

# 3rd party
from univention.provisioning.consumer import (
    MessageHandler,
    ProvisioningConsumerClient,
)
from univention.provisioning.models import ProvisioningMessage

# internal
from config import (
    OXConsumerSettings,
    get_ox_consumer_settings,
)
from listener_trigger import KeyValueStore, TriggerObject
from univention.ox.provisioning import helpers, run

LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(module)s.%(funcName)s:%(lineno)d] %(message)s"
logger = logging.getLogger(__name__)

# FIXME: ox-connector needs to locally keep track of the previous objects
# ox-context id and uid (username). This was previously not needed since it
# was requested to OX when needed, but it slowed down the processing.
# We are using their KeyValueStore (dbm.gnu) to store the values.
ox_contexts = KeyValueStore("contexts.db")
ox_db_id = KeyValueStore("ox_db_id.db")
usernames = KeyValueStore("usernames.db")


class FakeObject:
    """
    Object to fake load of the `old` stored object.

    Args:
        attributes (dict): Attributes of the object is the only field needed
                           and used by the `univention-ox-provisioning`
                           helpers.
    """

    def __init__(self, attributes: Dict[str, str]):
        self.attributes = attributes


def safe_decode(value):
    if value is None:
        return None
    if isinstance(value, bytes):
        return value.decode("utf-8")
    return value


def _get_existing_object_ox_id(distinguished_name: str):
    """
    Get the object OX ID from the known objects, avoiding the old.db and
    storing JSON files. Used to overwrite `get_old_obj` in
    `univention-ox-provisioning/univention/ox/provisioning/helpers.py`.

    Args:
        distinguished_name (str): Distinguished name of the object

    Returns:
        FakeObject: Object with the `oxContext` in attributes, to avoid
                    loading an object from a JSON file and storing it.
    """
    object_ox_id = ox_contexts.get(distinguished_name)
    object_ox_db_id = ox_db_id.get(distinguished_name)
    object_ox_db_uid = usernames.get(distinguished_name)
    logger.info("Loading object OX ID from known objects")
    fake_obj = FakeObject(
        {
            "oxContext": safe_decode(object_ox_id),
            "oxDbId": safe_decode(object_ox_db_id),
            "username": safe_decode(object_ox_db_uid),
        },
    )
    logger.debug("old object retrieved: %s", fake_obj.attributes)
    return fake_obj


# Overwrite the `get_old_obj` function in the helpers module
helpers.get_old_obj = _get_existing_object_ox_id


class OXConsumer:
    topics = {
        "oxmail/oxcontext",
        "oxmail/accessprofile",
        "users/user",
        "oxresources/oxresources",
        "groups/group",
        "oxmail/functional_account",
    }

    def __init__(self, settings: OXConsumerSettings | None = None):
        self.settings = settings or get_ox_consumer_settings()

    async def start_listening_for_changes(
        self,
        provisioning_client: type[ProvisioningConsumerClient],
        message_handler: type[MessageHandler],
    ) -> None:
        logger.info("Listening for changes in topics: %r", self.topics)
        async with provisioning_client() as client:
            await message_handler(client, [self.handle_message]).run()

    async def handle_message(self, message: ProvisioningMessage):
        topic = message.topic
        if topic not in self.topics:
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

        new_obj = body.new
        old_obj = body.old

        if old_obj and new_obj:
            self.modify(old_obj, new_obj, new_obj.get("dn"), old_obj.get("dn"))
        elif old_obj:
            self.remove(old_obj, old_obj.get("dn"))
        else:
            self.create(new_obj, new_obj.get("dn"))

    def create(self, new: Dict[str, Any], dn: str) -> None:
        t0 = time.perf_counter()
        obj = TriggerObject(
            new['uuid'],
            new['objectType'],
            dn,
            new.get("properties"),
            ['default'],
            None,
        )
        # Emulate the listener_trigger.load_old() method
        obj.old_distinguished_name = None
        obj.old_attributes = None
        obj.old_options = None
        obj._old_loaded = True
        try:
            run(obj)
            # Store the needed values to keep track of the objects locally.
            # For more details, see KeyValueStore objects FIXME above.
            if obj.attributes.get("oxContext") is not None:
                logger.info("Storing object OX ID in known objects")
                ox_contexts.set(dn, obj.attributes['oxContext'])
            if obj.attributes.get("oxDbId") is not None:
                logger.info("Storing object OX DB ID in known objects")
                ox_db_id.set(dn, obj.attributes['oxDbId'])
            if obj.attributes.get("username") is not None:
                logger.info("Storing object username in known objects")
                usernames.set(dn, obj.attributes['username'])
        except Exception as err:
            logger.exception('Failed to handle creation')
            logger.warning(err)
            raise
        logger.debug(
            "Finished CREATE of %r %r in %.1f ms.",
            new['objectType'],
            dn,
            (time.perf_counter() - t0) * 1000,
        )

    def modify(
        self,
        old: Dict[str, Any],
        new: Dict[str, Any],
        dn: str,
        old_dn: str,
    ) -> None:
        t0 = time.perf_counter()
        obj_is_moved = dn != old_dn

        # Emulate the listener_trigger.load_old() method
        obj = TriggerObject(
            new['uuid'],
            new['objectType'],
            dn,
            new.get("properties"),
            ['default'],
            None,
        )
        obj.old_distinguished_name = old["dn"]
        obj.old_attributes = old.get("properties")
        obj.old_options = ['default']
        obj._old_loaded = True
        try:
            run(obj)
            # Store the needed values to keep track of the objects locally.
            # For more details, see KeyValueStore objects FIXME above.
            if obj.attributes:
                if obj.attributes.get("oxContext") is not None and (
                    obj.attributes.get("oxContext")
                    != obj.old_attributes.get("oxContext")
                    or obj_is_moved
                ):
                    logger.info(
                        "Updating object OX ID in known objects from %s to %s",
                        obj.old_attributes.get("oxContext"),
                        obj.attributes.get("oxContext"),
                    )
                    ox_contexts.set(dn, obj.attributes['oxContext'])
                if obj.attributes.get("oxDbId") is not None and (
                    obj.attributes.get("oxDbId")
                    != obj.old_attributes.get("oxDbId")
                    or obj_is_moved
                ):
                    logger.info(
                        "Updating object OX DB ID in known objects from %s to %s",
                        obj.old_attributes.get("oxDbId"),
                        obj.attributes.get("oxDbId"),
                    )
                    ox_db_id.set(dn, obj.attributes['oxDbId'])
                if obj.attributes.get("username") is not None and (
                    obj.attributes.get("username")
                    != obj.old_attributes.get("username")
                    or obj_is_moved
                ):
                    logger.info(
                        "Updating object username in known objects from %s to %s",
                        obj.old_attributes.get("username"),
                        obj.attributes.get("username"),
                    )
                    usernames.set(dn, obj.attributes['username'])
        except Exception as err:
            logger.exception('Failed to handle modification')
            logger.debug(err)
            raise
        logger.debug(
            "Finished MODIFY of %r %r (%r) in %.1f ms.",
            new['objectType'],
            dn,
            old_dn,
            (time.perf_counter() - t0) * 1000,
        )

    def remove(self, old: Dict[str, Any], dn: str) -> None:
        t0 = time.perf_counter()
        obj = TriggerObject(
            old['uuid'],
            old['objectType'],
            dn,
            None,  # for listener_trigger.TriggerObject.was_deleted() method
            ['default'],
            None,
        )
        obj.old_distinguished_name = old["dn"]
        obj.old_attributes = old.get("properties")
        obj.old_options = ['default']
        obj._old_loaded = True
        run(obj)
        if obj.old_attributes.get("oxContext") is not None:
            logger.info("Removing object OX ID from known objects")
            ox_contexts.set(dn, self.settings.default_context)
        # TODO: is deleting usernames and db_id from known objects needed?
        logger.debug(
            "Finished DELETE of %r %r in %.1f ms.",
            old['objectType'],
            dn,
            (time.perf_counter() - t0) * 1000,
        )


def main() -> None:
    settings = get_ox_consumer_settings()
    logging.basicConfig(format=LOG_FORMAT, level=settings.log_level)
    logger.info(
        "Using 'nubus-provisioning-consumer' library version %r.",
        version("nubus-provisioning-consumer"),
    )
    consumer = OXConsumer(settings)
    asyncio.run(
        consumer.start_listening_for_changes(
            ProvisioningConsumerClient,
            MessageHandler,
        ),
    )


if __name__ == "__main__":
    main()

# [EOF]
