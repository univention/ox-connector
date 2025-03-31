# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import dbm.gnu
import json
import time
from contextlib import contextmanager
from pathlib import Path

from univention.ox.provisioning.users import User


# copied from app/listener_trigger to test the cache dbs
class KeyValueStore(object):
    def __init__(self, name):
        APP = "ox-connector"
        DATA_DIR = Path("/var/lib/univention-appcenter/apps", APP, "data")
        NEW_FILES_DIR = DATA_DIR / "listener"
        self.db_fname = str(NEW_FILES_DIR / name)

    @contextmanager
    def open(self):
        with dbm.gnu.open(self.db_fname, "r") as db:
            yield db

    def get(self, key):
        with self.open() as db:
            return db.get(key)


mapping = KeyValueStore("old.db")  # stores dn -> path to last json file


def find_obj(context_id, name, assert_empty=False, print_obj=True):
    objs = User.list(context_id, pattern=name)
    if assert_empty:
        assert len(objs) == 0
    else:
        assert len(objs) == 1
        obj = objs[0]
        if print_obj:
            print("Found", obj)
        return obj


def get_db_id(dn: str, max_retry: int=5) -> str:
    """
    Tests existance of an old JSON file
    Returns the oxDbId (if any)
    """
    for i in range(max_retry):
        try:
            old_file_path = mapping.get(dn)
        except Exception as e:
            time.sleep(1)
            if i < max_retry - 1: continue
            else: raise e
        break
    if old_file_path is None:
        return None
    with open(old_file_path) as fd:
        obj = json.load(fd)
    return obj["object"].get("oxDbId")


def test_ignore_user(create_ox_user):
    """
    Test a non ox-user. Should not find a DB ID in cache
    """
    dn = create_ox_user(context_id=None, enabled=False).dn
    db_id = get_db_id(dn)
    assert db_id is None


def test_add_user(
    create_ox_context, create_ox_user, new_user_name
):
    """
    Test a new user. Should find a DB ID in cache
    """
    new_context_id = create_ox_context()
    user = create_ox_user(new_user_name, context_id=new_context_id)
    obj = find_obj(new_context_id, new_user_name)
    db_id = get_db_id(user.dn)
    assert obj.id == db_id


def test_rename_user(
    create_ox_user, udm, wait_for_listener,
):
    """
    Renaming a user should keep its ID
    """
    user = create_ox_user()
    db_id = get_db_id(user.dn)
    assert db_id is not None
    dn = udm.modify(
        "users/user",
        user.dn,
        {"username": "new" + user.properties["username"]},
    )
    wait_for_listener(dn)
    new_db_id = get_db_id(dn)
    assert db_id == new_db_id


def test_change_context(
    create_ox_user, create_ox_context, udm, wait_for_listener,
):
    """
    Changing context should create new IDs in database
    """
    new_context_id = create_ox_context()
    create_ox_user()  # create one more user so that we have two users -> higher DB IDs in the first context
    dn = create_ox_user().dn
    db_id = get_db_id(dn)
    assert db_id is not None
    udm.modify(
        "users/user",
        dn,
        {"oxContext": new_context_id},
    )
    wait_for_listener(dn)
    new_db_id = get_db_id(dn)
    assert new_db_id is not None
    assert db_id != new_db_id


def test_remove_user(
    create_ox_user, create_ox_context, udm, wait_for_listener,
):
    """
    Test a new user. Should find a DB ID in cache
    """
    new_context_id = create_ox_context()
    dn = create_ox_user(new_context_id).dn
    udm.modify(
        "users/user",
        dn,
        {"isOxUser": False},
    )
    wait_for_listener(dn)
    db_id = get_db_id(dn)
    assert db_id is None
