# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

import logging
from typing import Final

from univention.ox.provisioning.key_value_store import KeyValueStore
from univention.ox.provisioning.helpers import normalized_dn

db_version_key: Final[str] = "__DB_VERSION__"
current_db_version: Final[int] = 2

logger = logging.getLogger(__name__)


def migrate_db(db: KeyValueStore) -> bool:
    """
    Migrate given KeyValueStore to latest DB schema

    Args:
        db (KeyValueStore): KeyValueStore to be migrated

    Returns:
        bool: Returns true if migration was done otherwise false
    """
    logger.info(f"Migration check DB: {db.db_fname}")
    db_version = db.get(db_version_key)
    if not db_version:
        db_version = 1
        empty_db_entries = 0
    else:
        db_version = int(db_version)
        empty_db_entries = 1

    if db_version == current_db_version:
        logger.info(f"No migration needed, DB version is {db_version}")
        return False

    with db.open("cs") as data:
        if len(data.keys()) == empty_db_entries:
            logger.info("No migration needed, DB is empty")

            data[db_version_key] = str(current_db_version)
            return False

    logger.info(
        f"Migrating DB version from {db_version} to {current_db_version}",
    )
    updated_entries = 0
    with db.open("cs") as data:
        for k in data.keys():
            if k.decode("UTF-8").lower() == db_version_key.lower():
                continue

            normalized = normalized_dn(k)
            if normalized == k.decode("UTF-8"):
                continue

            updated_entries += 1
            data[normalized] = data[k]
            del data[k]

    db.set(db_version_key, current_db_version)
    db.commit()

    logger.info(
        f"Migration succesfully, updated {updated_entries} entries. Setting DB version to {current_db_version}.",
    )

    return True


def main() -> None:
    from config import get_ox_consumer_settings

    settings = get_ox_consumer_settings()
    LOG_FORMAT = "%(asctime)s %(levelname)-5s [%(module)s.%(funcName)s:%(lineno)d] %(message)s"
    logging.basicConfig(format=LOG_FORMAT, level=settings.log_level)

    dbs = ["ox_contexts", "ox_db_id", "non_ox_objs", "usernames"]
    for db_name in dbs:
        try:
            db = getattr(__import__("consumer", fromlist=[db_name]), db_name)

            migrate_db(db)
        except OSError:
            logger.info(
                f"No migration needed, DB not created yet: {db_name}",
            )


if __name__ == "__main__":
    main()
