import dbm.gnu
from contextlib import contextmanager
from pathlib import Path
import json

from univention.ox.backend_base import User, get_ox_integration_class


# copied from app/listener_trigger to test the cache dbs
class KeyValueStore(object):
    def __init__(self, name):
        APP = "ox-connector"
        DATA_DIR = Path("/var/lib/univention-appcenter/apps", APP, "data")
        NEW_FILES_DIR = DATA_DIR / "listener"
        self.db_fname = str(NEW_FILES_DIR / name)

    @contextmanager
    def open(self):
        with dbm.gnu.open(self.db_fname, "cs") as db:
            yield db

    def set(self, dn, path):
        if dn is None:
            return
        with self.open() as db:
            if path is None:
                if dn in db:
                    del db[dn]
            else:
                db[dn] = str(path)

    def get(self, key):
        with self.open() as db:
            return db.get(key)


mapping = KeyValueStore("old.db")  # stores dn -> path to last json file


def create_context(udm, ox_host, context_id, wait_for_listener) -> str:
    dn = udm.create(
        "oxmail/oxcontext",
        "cn=open-xchange",
        {
            "oxQuota": 1000,
            "contextid": context_id,
            "name": "context{}".format(context_id),
        },
    )
    wait_for_listener(dn)
    return dn


def create_user(udm, name, domainname, context_id, enabled=True) -> str:
    _attrs = {
        "username": name,
        "firstname": "Emil",
        "lastname": name.title(),
        "password": "univention",
        "mailPrimaryAddress": "{}@{}".format(name, domainname),
        "isOxUser": enabled,
        "oxAccess": "premium",
        "oxContext": context_id,
    }
    dn = udm.create(
        "users/user",
        "cn=users",
        _attrs,
    )
    return dn


def find_obj(context_id, name, assert_empty=False, print_obj=True) -> User:
    User = get_ox_integration_class("SOAP", "User")
    objs = User.list(context_id, pattern=name)
    if assert_empty:
        assert len(objs) == 0
    else:
        assert len(objs) == 1
        obj = objs[0]
        if print_obj:
            print("Found", obj)
        return obj


def get_db_id(dn: str) -> str:
    """
    Tests existance of an old JSON file
    Returns the oxDbId (if any)
    """
    old_file_path = mapping.get(dn)
    if old_file_path is None:
        return None
    with open(old_file_path) as fd:
        obj = json.load(fd)
    return obj["object"].get("oxDbId")


def test_ignore_user(
    default_ox_context, new_user_name, udm, domainname, wait_for_listener
):
    """
    Test a non ox-user. Should not find a DB ID in cache
    """
    dn = create_user(udm, new_user_name, domainname, None, enabled=False)
    wait_for_listener(dn)
    db_id = get_db_id(dn)
    assert db_id is None


def test_add_user(
    new_context_id, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    """
    Test a new user. Should find a DB ID in cache
    """
    create_context(udm, ox_host, new_context_id, wait_for_listener)
    dn = create_user(udm, new_user_name, domainname, new_context_id)
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    db_id = get_db_id(dn)
    assert obj.id == db_id


def test_rename_user(
    default_ox_context, new_user_name, udm, domainname, wait_for_listener
):
    """
    Renaming a user should keep its ID
    """
    dn = create_user(udm, new_user_name, domainname, default_ox_context)
    wait_for_listener(dn)
    db_id = get_db_id(dn)
    assert db_id is not None
    dn = udm.modify(
        "users/user",
        dn,
        {"username": "new" + new_user_name},
    )
    wait_for_listener(dn)
    new_db_id = get_db_id(dn)
    assert db_id == new_db_id


def test_change_context(
    default_ox_context,
    new_context_id,
    new_user_name_generator,
    udm,
    ox_host,
    domainname,
    wait_for_listener,
):
    """
    Changing context should create new IDs in database
    """
    create_context(udm, ox_host, new_context_id, wait_for_listener)
    create_user(udm, new_user_name_generator(), domainname, default_ox_context)
    dn = create_user(udm, new_user_name_generator(), domainname, default_ox_context)
    wait_for_listener(dn)
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
    new_context_id, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    """
    Test a new user. Should find a DB ID in cache
    """
    create_context(udm, ox_host, new_context_id, wait_for_listener)
    dn = create_user(udm, new_user_name, domainname, new_context_id)
    wait_for_listener(dn)
    udm.modify(
        "users/user",
        dn,
        {"isOxUser": False},
    )
    wait_for_listener(dn)
    db_id = get_db_id(dn)
    assert db_id is None
