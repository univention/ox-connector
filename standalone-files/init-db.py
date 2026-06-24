# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import asyncio
import os
import sys
import logging
from univention.provisioning.consumer.api import (
    ProvisioningConsumerClient,
    ProvisioningConsumerClientSettings,
)
from univention.provisioning.models.subscription import (
    RealmTopic,
)
from univention.ox.provisioning.db import DBSession, initialize_db

log_level_str = os.environ.get("LOG_LEVEL", "INFO")
log_level = getattr(logging, log_level_str, logging.INFO)
logging.basicConfig(
    format='%(asctime)s %(levelname)s: %(message)s',
    level=log_level,
)
logger = logging.getLogger('init-db')


TOPICS = [
    RealmTopic(realm="udm", topic="oxmail/oxcontext"),
    RealmTopic(realm="udm", topic="oxmail/accessprofile"),
    RealmTopic(realm="udm", topic="users/user"),
    RealmTopic(realm="udm", topic="groups/group"),
    RealmTopic(realm="udm", topic="oxmail/functional_account"),
    RealmTopic(realm="udm", topic="oxmail/shared_account"),
    RealmTopic(realm="udm", topic="oxmail/shared_account_permission"),
    RealmTopic(realm="udm", topic="oxresources/oxresources"),
]


def _check_tables_empty(db):
    """Return True if the old and task table has no rows."""
    return not db.contain_old() and not db.contain_tasks()


async def _recreate_subscription():
    """
    Delete and recreate the existing subscription with request_prefill=True.

    Uses only an admin client that has permissions to create and delete
    subscriptions. The prefill messages are drained by the consumer in the
    main container.
    """
    base_url = os.environ.get("PROVISIONING_API_BASE_URL")
    admin_user = os.environ.get("PROVISIONING_API_ADMIN_USERNAME")
    admin_password = os.environ.get("PROVISIONING_API_ADMIN_PASSWORD")
    subscriber_name = os.environ.get("PROVISIONING_API_USERNAME")
    subscriber_password = os.environ.get("PROVISIONING_API_PASSWORD")

    if not all([base_url, admin_user, admin_password, subscriber_name]):
        logger.warning(
            "PROVISIONING_API_BASE_URL, PROVISIONING_API_ADMIN_USERNAME, "
            "PROVISIONING_API_ADMIN_PASSWORD, PROVISIONING_API_USERNAME and "
            "PROVISIONING_API_PASSWORD "
            "must be set for prefill. Skipping prefill.",
        )
        return

    admin_client_settings = ProvisioningConsumerClientSettings(
        provisioning_api_base_url=base_url,
        provisioning_api_username=admin_user,
        provisioning_api_password=admin_password,
        log_level="WARNING",
    )

    async with ProvisioningConsumerClient(
        admin_client_settings,
    ) as admin_client:
        logger.info(
            "Deleting subscription '%s'",
            subscriber_name,
        )
        await admin_client.cancel_subscription(subscriber_name)

        logger.info(
            "Recreating subscription '%s' with request_prefill=True",
            subscriber_name,
        )
        await admin_client.create_subscription(
            name=subscriber_name,
            password=subscriber_password,
            realms_topics=TOPICS,
            request_prefill=True,
        )

    logger.info(
        "Subscription recreated. Waiting for consumer to drain prefill.",
    )


async def main_async():
    logger.info("Initializing SQL database ...")
    try:
        initialize_db(create_parent_directory=True)
    except Exception:
        logger.exception("Database initialization failed")
        return False

    with DBSession() as db:
        if not _check_tables_empty(db):
            logger.info("Tables are not empty. Skipping prefill.")
            return True

    resync_enabled = os.environ.get(
        "PROVISIONING_API_RESYNC_ENABLED",
        "true",
    ).lower() in ("true", "1", "yes")
    if not resync_enabled:
        logger.info("Resync is disabled. Skipping prefill.")
        return True

    logger.info("Tables are empty. Running prefill ...")
    try:
        await _recreate_subscription()
    except Exception:
        logger.exception("Prefill failed")
        return False

    return True


def main():
    success = asyncio.run(main_async())
    if success:
        logger.info('Initialization completed successfully')
        sys.exit(0)
    else:
        logger.exception('Initialization failed')
        sys.exit(1)


if __name__ == "__main__":
    main()
