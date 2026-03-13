# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import time
import os
import pytest
import logging
from contextlib import contextmanager
from pathlib import Path

from tempfile import NamedTemporaryFile
from utils import FileUtility

from univention.ox.provisioning.helpers import normalized_dn
from univention.ox.provisioning.users import User
from univention.ox.provisioning.groups import Group

log = logging.getLogger(__name__)


pytestmark = pytest.mark.skip_platform(
    'ucs',
    reason="The ucs deployment moved to sqlite DB and test needs to be adopted, currently only supports dbm",
)


class KeyValueStore(object):
    def __init__(self, name, file_utility):
        APP = "ox-connector"
        DATA_DIR = Path("/var/lib/univention-appcenter/apps", APP, "data")
        NEW_FILES_DIR = DATA_DIR / "listener"
        self.db_fname = str(NEW_FILES_DIR / name)
        self.file_utility = file_utility

    @contextmanager
    def open(self, mode="r"):
        with self.file_utility.open_dbm(self.db_fname, mode) as db:
            yield db

    def get(self, key):
        with self.open() as db:
            return db.get(key)

    def set(self, key, value):
        with self.open('c') as db:
            db[key.encode() if isinstance(key, str) else key] = str(
                value,
            ).encode()

    def commit(self):
        pass


@pytest.fixture
def ox_mapping(file_utility):
    """Provides access to OX ID mappings in both local and k8s environments"""
    return {
        'id_mapping': KeyValueStore("ox_db_id.db", file_utility),
        'non_ox_mapping': KeyValueStore("non_ox_objs.db", file_utility),
    }


@pytest.fixture
def test_db():
    # Tests can run localy no need to access file on k8s pod
    db = KeyValueStore("migrate.db", FileUtility())

    with NamedTemporaryFile() as ephermal_db:
        db.db_fname = ephermal_db.name
        yield db


def find_obj(
    context_id,
    name,
    type="user",
    assert_empty=False,
    print_obj=True,
):
    if type == "user":
        objs = User.list(context_id, pattern=name)
    elif type == "group":
        objs = Group.list(context_id, pattern=name)
    else:
        print("Unknown type {type}")
        assert False

    if assert_empty:
        if print_obj:
            print(f"Not found: {type}, pattern: {name}")
        assert len(objs) == 0
    else:
        assert len(objs) == 1
        obj = objs[0]
        if print_obj:
            print("Found", obj)
        return obj


def get_db_id(dn: str, max_retry: int = 5, db: KeyValueStore = None) -> int:
    """
    Tests existance of an old JSON file
    Returns the oxDbId (if any)
    """
    for i in range(max_retry):
        try:
            db_entry = db.get(dn)
        except Exception as e:
            log.info(
                "get_db_id: attempt %d failed with %s",
                i,
                e,
                exc_info=True,
            )
            time.sleep(1)
            if i < max_retry - 1:
                log.info("get_db_id: retrying (attempt %d)", i)
                continue
            else:
                log.info("get_db_id: final attempt %d failed, raising", i)
                raise
        break

    if db_entry is None:
        return None

    ox_id = int(db_entry.decode('utf-8'))
    return ox_id


def test_ignore_user(create_ox_user, ox_mapping):
    """
    Test a non ox-user. Should not find a DB ID in cache
    """
    dn = create_ox_user(context_id=None, enabled=False).dn
    db_id = get_db_id(dn, db=ox_mapping['id_mapping'])
    assert db_id is None


def test_add_user(
    create_ox_context,
    create_ox_user,
    new_user_name,
    ox_mapping,
):
    """
    Test a new user. Should find a DB ID in cache
    """
    new_context_id = create_ox_context()
    user = create_ox_user(new_user_name, context_id=new_context_id)
    obj = find_obj(new_context_id, new_user_name)
    db_id = get_db_id(user.dn, db=ox_mapping['id_mapping'])
    assert obj.id == db_id


def test_rename_user(
    create_ox_user,
    udm,
    wait_for_listener,
    ox_mapping,
):
    """
    Renaming a user should keep its ID
    """
    user = create_ox_user()
    db_id = get_db_id(user.dn, db=ox_mapping['id_mapping'])
    assert db_id is not None
    dn = udm.modify(
        "users/user",
        user.dn,
        {"username": "new" + user.properties["username"]},
    )
    wait_for_listener(dn)
    new_db_id = get_db_id(dn, db=ox_mapping['id_mapping'])
    assert db_id == new_db_id


def test_missing_user_cache_entry_gets_reloaded_during_group_creation(
    create_ox_user,
    create_ox_group,
    default_ox_context,
    ox_mapping,
):
    """
    Creating a group with a user not in the cache should lazy load it
    """
    user = create_ox_user()
    db_id = get_db_id(user.dn, db=ox_mapping['id_mapping'])
    assert db_id is not None

    print(f'Deleting {user.dn} from cache')
    with ox_mapping['id_mapping'].open(mode="w") as db:
        del db[user.dn.encode('utf-8')]

    create_ox_group("TestGroup01", members=[user.dn])
    assert (
        find_obj(default_ox_context, "TestGroup01", type="group") is not None
    )
    reloaded_db_id = get_db_id(user.dn, db=ox_mapping['id_mapping'])
    assert reloaded_db_id is not None
    assert reloaded_db_id == db_id


# The non_ox_mapping DB only exists in standalone mode
@pytest.mark.skip_platform('ucs')
def test_converting_non_ox_user_to_ox_user_updates_cache_correctly(
    create_ox_user,
    udm,
    wait_for_listener,
    ox_mapping,
):
    """
    Changing a non ox user to a ox user should update the non-ox-object cache accordingly
    """
    non_ox_user = create_ox_user(enabled=False)
    db_id = get_db_id(non_ox_user.dn, db=ox_mapping['id_mapping'])
    assert db_id is None
    db_id = get_db_id(non_ox_user.dn, db=ox_mapping['non_ox_mapping'])
    assert db_id is not None

    udm.modify(
        "users/user",
        non_ox_user.dn,
        {"isOxUser": True},
    )
    wait_for_listener(non_ox_user.dn)
    db_id = get_db_id(non_ox_user.dn, db=ox_mapping['id_mapping'])
    assert db_id is not None
    db_id = get_db_id(non_ox_user.dn, db=ox_mapping['non_ox_mapping'])
    assert db_id is None


# The non_ox_mapping DB only exists in standalone mode
@pytest.mark.skip_platform('ucs')
def test_converting_ox_user_to_non_ox_user_updates_cache_correctly(
    create_ox_user,
    udm,
    wait_for_listener,
    ox_mapping,
):
    """
    Changing an ox user to a non ox user should update the non-ox-object cache accordingly
    """
    user = create_ox_user()
    db_id = get_db_id(user.dn, db=ox_mapping['id_mapping'])
    assert db_id is not None
    db_id = get_db_id(user.dn, db=ox_mapping['non_ox_mapping'])
    assert db_id is None

    udm.modify(
        "users/user",
        user.dn,
        {"isOxUser": False},
    )
    wait_for_listener(user.dn)
    db_id = get_db_id(user.dn, db=ox_mapping['id_mapping'])
    assert db_id is None

    db_id = get_db_id(user.dn, db=ox_mapping['non_ox_mapping'])
    assert db_id is None


def test_change_context(
    create_ox_user,
    create_ox_context,
    udm,
    wait_for_listener,
    ox_mapping,
):
    """
    Changing context should create new IDs in database
    """
    new_context_id = create_ox_context()
    create_ox_user()  # create one more user so that we have two users -> higher DB IDs in the first context
    dn = create_ox_user().dn
    db_id = get_db_id(dn, db=ox_mapping['id_mapping'])
    assert db_id is not None
    udm.modify(
        "users/user",
        dn,
        {"oxContext": new_context_id},
    )
    wait_for_listener(dn)
    new_db_id = get_db_id(dn, db=ox_mapping['id_mapping'])
    assert new_db_id is not None
    assert db_id != new_db_id


def test_remove_user(
    create_ox_user,
    create_ox_context,
    udm,
    wait_for_listener,
    ox_mapping,
):
    """
    Test a new user. Should find a DB ID in cache
    """
    new_context_id = create_ox_context()
    dn = create_ox_user(context_id=new_context_id).dn
    udm.modify(
        "users/user",
        dn,
        {"isOxUser": False},
    )
    wait_for_listener(dn)
    db_id = get_db_id(dn, db=ox_mapping['id_mapping'])
    assert db_id is None


def test_non_normalized_dn(
    create_ox_user,
    create_ox_group,
    default_ox_context,
    ox_mapping,
):
    """
    Make sure, normalized DNs are stored in the DB
    """
    create_ox_group("TEST+1")

    user = create_ox_user(ldap_path="cn=TEST\+1,cn=groups")

    # When searching for unnormalized DN it will return None
    db_id = get_db_id(user.dn, db=ox_mapping['id_mapping'])
    assert db_id is None

    # When searching for normalized DN it will return the DB entry
    db_id = get_db_id(normalized_dn(user.dn), db=ox_mapping['id_mapping'])
    obj = find_obj(default_ox_context, user.properties["username"])
    assert obj.id == db_id


# DB Migration only used in standalone mode
@pytest.mark.skip_platform('ucs')
def test_migrate_db_v1(test_db, new_user_name_generator):
    migrate_lib = pytest.importorskip("migrate")

    with test_db.open("cs") as data:
        for i in range(100):
            if (i % 6) == 0:
                name = new_user_name_generator().upper()
            else:
                name = new_user_name_generator()

            if (i % 3) == 0:
                dn = f"uid={name},ou=Sales+cn=users,dc=swp-ldap,dc=internal"
            else:
                dn = f"uid={name},cn=users,dc=swp-ldap,dc=internal"
            data[dn] = str(i)

    assert migrate_lib.migrate_db(test_db)

    with test_db.open() as data:
        for k in data.keys():
            if k.decode("UTF-8").lower() == migrate_lib.db_version_key.lower():
                continue

            assert k.decode("UTF-8") == normalized_dn(k)

    # DB is migrated so don't do it again
    assert not migrate_lib.migrate_db(test_db)


# DB Migration only used in standalone mode
@pytest.mark.skip_platform('ucs')
@pytest.mark.skipif(
    os.environ.get("PERFORMANCE_TESTS") is None,
    reason="Performance tests are disabled by default, if you want to run them add the env var PERFORMANCE_TESTS",
)
def test_migrate_performance(test_db, new_user_name_generator):
    migrate_lib = pytest.importorskip("migrate")

    num_useres = 100000
    start = time.perf_counter()
    with test_db.open("cs") as data:
        for i in range(num_useres):
            dn = f"uid=TEST-USER-{i},ou=Sales+cn=users,dc=swp-ldap,dc=internal"
            data[dn] = str(i)

    end = time.perf_counter()
    print(f"Time: Adding {num_useres} users to DB - {end - start:.2f}s")

    migrate_start = time.perf_counter()
    assert migrate_lib.migrate_db(test_db)
    end = time.perf_counter()
    print(
        f"Time: Migrating DB with {num_useres} entries - {end - migrate_start:.2f}s",
    )

    check_results_start = time.perf_counter()
    with test_db.open() as data:
        for k in data.keys():
            if k.decode("UTF-8").lower() == migrate_lib.db_version_key.lower():
                continue

            assert k.decode("UTF-8") == normalized_dn(k)

    end = time.perf_counter()
    print(
        f"Time: Checking results after migration  - {end - check_results_start:.2f}s",
    )

    # DB is migrated so don't do it again
    assert not migrate_lib.migrate_db(test_db)
    end = time.perf_counter()
    print(f"Time: Overall - {end - start:.2f}s")
