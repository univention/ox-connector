# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

# included
import asyncio
import logging
import time
import os
from importlib.metadata import version
from typing import Any, Dict
from pathlib import Path

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
from listener_trigger import TriggerObject

from univention.ox.provisioning import helpers, run
from univention.ox.provisioning.contexts import Context
from univention.ox.provisioning.key_value_store import KeyValueStore
from univention.ox.provisioning.users import User

LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(module)s.%(funcName)s:%(lineno)d] %(message)s"
logger = logging.getLogger(__name__)

DATA_DIR = Path("/var/lib/univention-appcenter/apps/ox-connector/data")
NEW_FILES_DIR = DATA_DIR / "listener"

# FIXME: ox-connector needs to locally keep track of the previous objects
# ox-context id and uid (username). This was previously not needed since it
# was requested to OX when needed, but it slowed down the processing.
# We are using their KeyValueStore (dbm.gnu) to store the values.
ox_contexts = KeyValueStore(str(NEW_FILES_DIR / "contexts.db"))
ox_db_id = KeyValueStore(str(NEW_FILES_DIR / "ox_db_id.db"))
non_ox_objs = KeyValueStore(str(NEW_FILES_DIR / "non_ox_objs.db"))
usernames = KeyValueStore(str(NEW_FILES_DIR / "usernames.db"))


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


def _search_ox_context_for_user(distinguished_name: str):
    # The first part of the DN is the user name, extract it and use it to find the user in OX
    username = None
    key_value_pairs = distinguished_name.split(',')
    for key_value_pair in key_value_pairs:
        key, value = key_value_pair.split('=')
        if key != "uid":
            continue

        username = value

    if username is None:
        return None, None, None

    logger.info(f"Search user {username} in all ox contexts")
    available_ox_contexts = Context.list()
    for context in available_ox_contexts:
        objs = User.list(context.id, pattern=username)
        if len(objs) != 1:
            continue

        logger.info(
            f"Found user: context={context.id}, id={objs[0].id}, username={username}",
        )
        return context.id, objs[0].id, username

    logger.info("User not found in any context")
    return None, None, None


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
    global ox_contexts, ox_db_id, usernames, non_ox_objs

    # Allow manipulating the cache from outside for debugging and testing
    if os.environ.get("DEBUG_RELOAD_OX_DB_ID"):
        ox_db_id = KeyValueStore(str(NEW_FILES_DIR / "ox_db_id.db"))

    object_ox_id = ox_contexts.get(distinguished_name)
    object_ox_db_id = ox_db_id.get(distinguished_name)
    object_ox_db_uid = usernames.get(distinguished_name)
    is_ox_object = non_ox_objs.get(distinguished_name) is None

    if (
        object_ox_db_id is None
        or object_ox_id is None
        or object_ox_db_uid is None
    ):
        if is_ox_object:
            logger.info(
                f"User {distinguished_name} not found in cache, searching it now",
            )
            object_ox_id, object_ox_db_id, object_ox_db_uid = (
                _search_ox_context_for_user(distinguished_name)
            )

            if (
                object_ox_id is not None
                and object_ox_db_id is not None
                and object_ox_db_uid is not None
            ):
                ox_contexts.set(distinguished_name, object_ox_id)
                ox_db_id.set(distinguished_name, object_ox_db_id)
                usernames.set(distinguished_name, object_ox_db_uid)
                non_ox_objs.unset(distinguished_name)

                ox_contexts.commit()
                ox_db_id.commit()
                usernames.commit()
            else:
                logger.info(
                    "User not found in OX, assuming it is a non OX-User",
                )
                non_ox_objs.set(distinguished_name, 1)

            non_ox_objs.commit()
        else:
            logger.info(
                f"User {distinguished_name} is a non OX user, ignoring it",
            )

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
        """
        The MessageHandler calls this method for every provisioning message that the consumer receives.
        If this method returns, the message will be acknowledged and this function will be called with the next message.
        If this method throws an exception, the message won't be acknowledged and the same message will be redelivered.

        Exceptions are not caught by the MessageHandler; they are re-raised instead.
        This stops the process, and the consumer relies on the platform (Kubernetes, Docker) to restart it.
        This allows the consumer to restart with a clean state and re-establish its network connections.
        It also clearly communicates the failure to the Administrator.
        """
        global ox_contexts, ox_db_id, usernames, non_ox_objs

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
            if old_obj.get("properties").get("isOxUser") != new_obj.get(
                "properties",
            ).get("isOxUser") or old_obj.get("properties").get(
                "isOxGroup",
            ) != new_obj.get(
                "properties",
            ).get(
                "isOxGroup",
            ):
                if new_obj.get("properties").get("isOxUser") or new_obj.get(
                    "properties",
                ).get("isOxGroup"):
                    logger.info(
                        "Is ox user/group changed, create object instead of modify",
                    )
                    self.create(new_obj, new_obj.get("dn"))
                else:
                    logger.info(
                        "Is ox user/group changed, delete object instead of modify",
                    )
                    self.remove(old_obj, old_obj.get("dn"))
            else:
                self.modify(
                    old_obj,
                    new_obj,
                    new_obj.get("dn"),
                    old_obj.get("dn"),
                )
        elif old_obj:
            self.remove(old_obj, old_obj.get("dn"))
        else:
            self.create(new_obj, new_obj.get("dn"))

        # Commit database changes after handling the message.
        logger.info("Committing database entries")
        ox_contexts.commit()
        ox_db_id.commit()
        usernames.commit()
        non_ox_objs.commit()

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

            if obj.attributes.get("isOxUser") or obj.attributes.get(
                "isOxGroup",
            ):
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

                non_ox_objs.unset(dn)
            else:
                logger.info(
                    "Non OX object created, only update non-ox-object DB",
                )
                non_ox_objs.set(dn, 1)

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

        logger.info("Removing object OX ID from known objects")
        ox_contexts.unset(dn)
        logger.info("Removing object OX DB ID from known objects")
        ox_db_id.unset(dn)
        logger.info("Removing object username from known objects")
        usernames.unset(dn)
        logger.info("Removing object from non ox objects")
        non_ox_objs.unset(dn)

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
