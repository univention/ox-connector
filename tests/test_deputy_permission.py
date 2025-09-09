# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

import itertools

import pytest
from univention.ox.provisioning.deputy_permissions import (
    is_enabled,
    DeputyPermission,
)
from univention.ox.provisioning.users import User

from univention.ox.soap.backend_base import ActiveDeputyPermission
from univention.ox.soap.types import Types
from udm_rest import UnprocessableEntity


# this should set is_enabled() correctly for the test suite
Types()


def get_user_id_from_udm_obj(obj) -> User:
    context_id, name = obj.properties["oxContext"], obj.properties["username"]
    objs = User.list(context_id, pattern=name)
    assert len(objs) == 1
    obj = objs[0]
    return obj.id


def find_obj(context_id, manager, deputy) -> ActiveDeputyPermission:
    objs = list_objs(context_id, manager, deputy)
    if objs:
        return objs[0]


def list_objs(
    context_id,
    manager=None,
    deputy=None,
) -> [ActiveDeputyPermission]:
    ret = []
    for permission in DeputyPermission.service(context_id).list():
        if deputy is not None and permission.userId == deputy:
            if manager is not None and permission.grantorId == manager:
                ret.append(permission)
            elif manager is None:
                ret.append(permission)
        elif manager is not None and permission.grantorId == manager:
            ret.append(permission)
    if manager and deputy:
        assert len(ret) <= 1
    return ret


@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_disallow_deputy_myself(create_ox_user, udm):
    manager = create_ox_user()
    with pytest.raises(UnprocessableEntity):
        udm.modify(
            "users/user",
            manager.dn,
            {
                "oxDeputyPermissionGivenTo": [
                    [manager.dn, "08444", "08444", True],
                ],
            },
        )


@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_disallow_two_permissions_between_same_users(create_ox_user, udm):
    manager = create_ox_user()
    deputy = create_ox_user()
    with pytest.raises(UnprocessableEntity):
        udm.modify(
            "users/user",
            manager.dn,
            {
                "oxDeputyPermissionGivenTo": [
                    [deputy.dn, "08444", "08444", True],
                    [deputy.dn, "08444", "08444", False],
                ],
            },
        )


@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_disallow_permissions_with_different_contexts(
    create_ox_user,
    create_ox_context,
    udm,
):
    manager = create_ox_user()
    new_context = create_ox_context()
    deputy = create_ox_user(context_id=new_context)
    with pytest.raises(UnprocessableEntity):
        udm.modify(
            "users/user",
            manager.dn,
            {
                "oxDeputyPermissionGivenTo": [
                    [deputy.dn, "08444", "08444", True],
                ],
            },
        )


@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_create_deputy_with_user_create(create_ox_user, get_udm_user):
    deputy = create_ox_user()
    permission = [deputy.dn, "00000", "08444", True]
    manager = create_ox_user(
        further_udm_attrs={"oxDeputyPermissionGivenTo": [permission]},
    )
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == [permission]


# FIXME -> [] == [[XY]] assert udm_obj.properties["oxDeputyPermissionGivenTo"] == [permission]


@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_remove_permission_after_context_change_of_deputy(
    create_ox_user,
    create_ox_context,
    get_udm_user,
    udm,
    wait_for_listener,
):
    manager = create_ox_user()
    deputy = create_ox_user()
    new_context = create_ox_context()
    permission = [deputy.dn, "08444", "08444", True]
    udm.modify(
        "users/user",
        manager.dn,
        {"oxDeputyPermissionGivenTo": [permission]},
    )
    wait_for_listener(manager.dn)
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == [permission]
    udm.modify("users/user", deputy.dn, {"oxContext": new_context})
    wait_for_listener(deputy.dn)
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == []


# FIXME -> udm_rest.UnprocessableEntity


@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_remove_permission_after_context_change_of_manager(
    create_ox_user,
    create_ox_context,
    get_udm_user,
    udm,
    wait_for_listener,
):
    deputy = create_ox_user()
    permission = [deputy.dn, "08444", "08444", True]
    manager = create_ox_user(
        further_udm_attrs={"oxDeputyPermissionGivenTo": [permission]},
    )
    udm_obj = get_udm_user(manager.properties['username'])
    new_context = create_ox_context()
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == [permission]
    with pytest.raises(UnprocessableEntity):
        udm.modify("users/user", manager.dn, {"oxContext": new_context})
    udm.modify(
        "users/user",
        manager.dn,
        {"oxContext": new_context, "oxDeputyPermissionGivenTo": []},
    )
    wait_for_listener(manager.dn)
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == []


@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_remove_permission_after_disable_manager_for_ox(
    create_ox_user,
    get_udm_user,
    udm,
    wait_for_listener,
):
    deputy = create_ox_user()
    permission = [deputy.dn, "08444", "08444", True]
    manager = create_ox_user(
        further_udm_attrs={"oxDeputyPermissionGivenTo": [permission]},
    )
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == [permission]
    udm.modify("users/user", manager.dn, {"isOxUser": False})
    wait_for_listener(manager.dn)
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == []


@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_remove_permission_after_disable_deputy_for_ox(
    create_ox_user,
    get_udm_user,
    udm,
    wait_for_listener,
):
    deputy = create_ox_user()
    permission = [deputy.dn, "00000", "08444", True]
    manager = create_ox_user(
        further_udm_attrs={"oxDeputyPermissionGivenTo": [permission]},
    )
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == [permission]
    udm.modify("users/user", deputy.dn, {"isOxUser": False})
    wait_for_listener(deputy.dn)
    # we changed deputy, but this change modifies manager by Hook
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == []


@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_remove_deputy_permission_after_delete(
    create_ox_user,
    udm,
    get_udm_user,
    wait_for_listener,
):
    deputy = create_ox_user()
    permission = [deputy.dn, "00000", "08444", True]
    manager = create_ox_user(
        further_udm_attrs={"oxDeputyPermissionGivenTo": [permission]},
    )
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == [permission]
    udm.remove("users/user", deputy.dn)
    wait_for_listener(deputy.dn)
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == []


# FIXME: [] == [[XY]]
@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_modify_deputy_permission_after_rename(
    create_ox_user,
    udm,
    get_udm_user,
    wait_for_listener,
):
    deputy = create_ox_user()
    permission = [deputy.dn, "08444", "08444", True]
    manager = create_ox_user(
        further_udm_attrs={"oxDeputyPermissionGivenTo": [permission]},
    )
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == [permission]
    new_deputy_name = "new_" + deputy.properties["username"]
    new_deputy_dn = udm.modify(
        "users/user",
        deputy.dn,
        {"username": new_deputy_name},
    )
    wait_for_listener(new_deputy_dn)
    # FIXME: udm_obj is
    udm_obj = get_udm_user(manager.properties['username'])
    assert udm_obj.properties["oxDeputyPermissionGivenTo"] == [
        [new_deputy_dn] + permission[1:],
    ]


@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
@pytest.mark.parametrize(
    "perm1,perm2,send_as",
    itertools.product(
        ["00000", "02400", "02440", "08444"],
        ["00000", "02400", "02440", "08444"],
        [True, False],
    ),
)
# FIXME: AttributeError: 'NoneType' object has no attribute 'userId'
def test_create_deputy_permission(
    create_ox_user,
    udm,
    wait_for_listener,
    perm1,
    perm2,
    send_as,
):
    manager = create_ox_user()
    deputy = create_ox_user()
    permission = [deputy.dn, perm1, perm2, send_as]
    udm.modify(
        "users/user",
        manager.dn,
        {"oxDeputyPermissionGivenTo": [permission]},
    )
    wait_for_listener(manager.dn)
    context_id = manager.properties["oxContext"]
    manager_id = get_user_id_from_udm_obj(manager)
    deputy_id = get_user_id_from_udm_obj(deputy)
    deputy_permission = find_obj(context_id, manager_id, deputy_id)
    if perm1 == "00000" and perm2 == "00000":
        # correct: this means no permissions granted!
        assert deputy_permission is None
        return
    assert deputy_permission.userId == deputy_id
    assert deputy_permission.grantorId == manager_id
    assert deputy_permission.sendOnBehalfOf == send_as
    if perm1 == "00000" or perm2 == "00000":
        assert len(deputy_permission.modulePermissions) == 1
    else:
        assert len(deputy_permission.modulePermissions) == 2
    for db_perm in deputy_permission.modulePermissions:
        if db_perm['moduleId'] == 'mail':
            assert db_perm['folderPermission'] == int(perm1[1])
            assert db_perm['readPermission'] == int(perm1[2])
            assert db_perm['writePermission'] == int(perm1[3])
            assert db_perm['deletePermission'] == int(perm1[4])
        elif db_perm['moduleId'] == 'calendar':
            assert db_perm['folderPermission'] == int(perm2[1])
            assert db_perm['readPermission'] == int(perm2[2])
            assert db_perm['writePermission'] == int(perm2[3])
            assert db_perm['deletePermission'] == int(perm2[4])
        else:
            raise ValueError("Unclear permission in DB: %r" % (db_perm,))


# FIXME: Assert None is not None
@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_removed_deputy_permission_on_manager_deletion(
    create_ox_user,
    udm,
    wait_for_listener,
):
    manager = create_ox_user()
    deputy = create_ox_user()
    permission = [deputy.dn, "08444", "08444", True]
    udm.modify(
        "users/user",
        manager.dn,
        {"oxDeputyPermissionGivenTo": [permission]},
    )
    wait_for_listener(manager.dn)
    context_id = manager.properties["oxContext"]
    manager_id = get_user_id_from_udm_obj(manager)
    deputy_id = get_user_id_from_udm_obj(deputy)
    deputy_permission = find_obj(context_id, manager_id, deputy_id)
    assert deputy_permission is not None
    udm.remove("users/user", manager.dn)
    wait_for_listener(manager.dn)
    deputy_permission = find_obj(context_id, manager_id, deputy_id)
    assert deputy_permission is None


# FIXME: None is not None
@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_removed_deputy_permission_on_deputy_deletion(
    create_ox_user,
    udm,
    wait_for_listener,
):
    manager = create_ox_user()
    deputy = create_ox_user()
    permission = [deputy.dn, "08444", "08444", True]
    udm.modify(
        "users/user",
        manager.dn,
        {"oxDeputyPermissionGivenTo": [permission]},
    )
    wait_for_listener(manager.dn)
    context_id = manager.properties["oxContext"]
    manager_id = get_user_id_from_udm_obj(manager)
    deputy_id = get_user_id_from_udm_obj(deputy)
    deputy_permission = find_obj(context_id, manager_id, deputy_id)
    assert deputy_permission is not None
    udm.remove("users/user", deputy.dn)
    wait_for_listener(deputy.dn)
    deputy_permission = find_obj(context_id, manager_id, deputy_id)
    assert deputy_permission is None


@pytest.mark.skip(
    reason="user_service.get_user_capabilities always gives 'There are no capabilities set'",
)
def test_block_and_unblock(
    create_ox_user,
    udm,
    wait_for_listener,
    default_ox_context,
):
    user_service = User.service(default_ox_context)
    manager = create_ox_user()
    manager_id = get_user_id_from_udm_obj(manager)
    capabilities = user_service.get_user_capabilities({"id": manager_id})
    print(capabilities)
    deputy = create_ox_user()
    permission = [deputy.dn, "08444", "08444", True]
    udm.modify(
        "users/user",
        manager.dn,
        {"oxDeputyPermissionGivenTo": [permission]},
    )
    wait_for_listener(manager.dn)
    capabilities = user_service.get_user_capabilities({"id": manager_id})
    print(capabilities)
    udm.modify("users/user", manager.dn, {"oxDeputyPermissionGivenTo": []})
    wait_for_listener(manager.dn)
    capabilities = user_service.get_user_capabilities({"id": manager_id})
    print(capabilities)


# FIXME: AssertionError: assert 2 == 1
@pytest.mark.skipif(not is_enabled(), reason="deputy permission not enabled")
def test_create_deputy_permission_when_it_already_exists(
    create_ox_user,
    default_ox_context,
    udm,
    wait_for_listener,
):
    deputy1 = create_ox_user()
    deputy2 = create_ox_user()
    permission = [deputy2.dn, "08444", "08444", True]  # udm
    deputy_permission = {
        "sendOnBehalfOf": True,
        "modulePermissions": [
            {
                "moduleId": "mail",
                "admin": False,
                "folderPermission": 2,
                "readPermission": 4,
                "writePermission": 4,
                "deletePermission": 0,
            },
            {
                "moduleId": "calendar",
                "admin": False,
                "folderPermission": 2,
                "readPermission": 4,
                "writePermission": 4,
                "deletePermission": 0,
            },
        ],
    }
    manager = create_ox_user()
    service = DeputyPermission.service(default_ox_context)
    manager_id = get_user_id_from_udm_obj(manager)
    deputy1_id = get_user_id_from_udm_obj(deputy1)
    deputy2_id = get_user_id_from_udm_obj(deputy2)
    service.grant(
        user=manager_id,
        deputy_permission={"userId": deputy1_id} | deputy_permission,
    )
    service.grant(
        user=manager_id,
        deputy_permission={"userId": deputy2_id} | deputy_permission,
    )
    permissions = list_objs(default_ox_context, manager=manager_id)
    assert len(permissions) == 2
    udm.modify(
        "users/user",
        manager.dn,
        {"oxDeputyPermissionGivenTo": [permission]},
    )
    wait_for_listener(manager.dn)
    permissions = list_objs(default_ox_context, manager=manager_id)
    assert len(permissions) == 1
    db_permission = permissions[0]
    assert db_permission.grantorId == manager_id
    assert db_permission.userId == deputy2_id
    assert db_permission.sendOnBehalfOf == permission[3]
    assert db_permission["modulePermissions"][0]["moduleId"] == "mail"
    assert db_permission["modulePermissions"][0]["admin"] == (
        permission[1][0] == "1"
    )
    assert db_permission["modulePermissions"][0]["folderPermission"] == int(
        permission[1][1],
    )
    assert db_permission["modulePermissions"][0]["readPermission"] == int(
        permission[1][2],
    )
    assert db_permission["modulePermissions"][0]["writePermission"] == int(
        permission[1][3],
    )
    assert db_permission["modulePermissions"][0]["deletePermission"] == int(
        permission[1][4],
    )
    assert db_permission["modulePermissions"][1]["moduleId"] == "calendar"
    assert db_permission["modulePermissions"][1]["admin"] == (
        permission[2][0] == "1"
    )
    assert db_permission["modulePermissions"][1]["folderPermission"] == int(
        permission[2][1],
    )
    assert db_permission["modulePermissions"][1]["readPermission"] == int(
        permission[2][2],
    )
    assert db_permission["modulePermissions"][1]["writePermission"] == int(
        permission[2][3],
    )
    assert db_permission["modulePermissions"][1]["deletePermission"] == int(
        permission[2][4],
    )
