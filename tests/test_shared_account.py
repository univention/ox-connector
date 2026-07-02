# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import pytest
from urllib.parse import urlparse

from univention.ox.soap.config import (
    DEFAULT_IMAP_SERVER,
    DEFAULT_LANGUAGE,
    DEFAULT_SMTP_SERVER,
    LOCAL_TIMEZONE,
)
from univention.ox.soap.types import Types

from udm_rest import UnprocessableEntity


@pytest.fixture(scope="session")
def check_shared_account_support(k8s_enabled):
    enabled = False
    # On k8s deployment we can not ask the local deployment, because tests are
    # run locally against a remote ox connector
    if k8s_enabled:
        # TODO: Look at the corresponding configmap, or env var in the pod
        from univention.ox.provisioning.shared_account import is_enabled

        # this should set is_enabled() correctly for the test suite
        Types()
        enabled = is_enabled()
    else:
        from univention.ox.provisioning.shared_account import is_enabled

        # this should set is_enabled() correctly for the test suite
        Types()
        enabled = is_enabled()

    if not enabled:
        pytest.skip(
            "SharedAccount not enabled, likely due to an OX version too old (or explicitly set via OX_ENABLE_SHARED_ACCOUNT).",
        )


def get_shared_account_display_name(name: str) -> str:
    return name.title().replace("_", " ")


def create_shared_account(
    udm,
    context_id,
    name,
    domainname,
    users=None,
    groups=None,
):
    dn = udm.create(
        "oxmail/shared_account",
        "cn=shared_accounts,cn=open-xchange",
        {
            "oxContext": context_id,
            "name": name,
            "displayName": get_shared_account_display_name(name),
            "mailPrimaryAddress": "{}@{}".format(name, domainname),
            "users": users,
            "groups": groups,
        },
    )
    print("Created account", dn, "in UDM")
    return dn


def create_shared_account_permission(
    udm,
    name,
    mail="none",
    calendar="none",
    sendAs=False,
    sendOnBehalf=False,
    snippets=False,
    writeSnippets=False,
    manageSieve=False,
    writeJSlob=False,
):
    dn = udm.create(
        "oxmail/shared_account_permission",
        "cn=shared_account_permissions,cn=open-xchange",
        {
            "name": name,
            "displayName": get_shared_account_display_name(name),
            "mail": mail,
            "calendar": calendar,
            "sendAs": sendAs,
            "sendOnBehalf": sendOnBehalf,
            "snippets": snippets,
            "writeSnippets": writeSnippets,
            "manageSieve": manageSieve,
            "writeJSlob": writeJSlob,
        },
    )
    print("Created account permission", dn, "in UDM")
    obj = udm.obj_by_dn(dn)
    return obj.properties["univentionObjectIdentifier"]


def assert_permission(permission, shared_account, ox_obj, calendar, mail, cap):
    assert permission.sharedAccountId == shared_account.id
    assert permission.entity == ox_obj.id
    assert permission.contextId == ox_obj.context_id
    assert permission.isGroup is hasattr(ox_obj, "members")
    assert permission.calendarConfig.permissionLevel == calendar
    assert permission.mailConfig.permissionLevel == mail
    if cap:
        assert set(permission.capabilities.grantedCapability) == set(cap)
    else:
        assert permission.capabilities is None


def test_create_shared_account(
    check_shared_account_support,
    udm,
    domainname,
    create_ox_user,
    default_ox_context,
    wait_for_listener,
    find_ox_object,
    new_account_name,
):
    user = create_ox_user()
    permission_uuid = create_shared_account_permission(
        udm,
        "shared_account_permission_1",
        mail="editor",
        sendOnBehalf=True,
        writeSnippets=True,
    )

    users = [[user.properties["univentionObjectIdentifier"], permission_uuid]]
    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )

    assert shared_account.name == new_account_name
    assert shared_account.display_name == get_shared_account_display_name(
        new_account_name,
    )
    assert shared_account.primaryEmail == f"{new_account_name}@{domainname}"

    assert shared_account.language == DEFAULT_LANGUAGE
    assert shared_account.timezone == LOCAL_TIMEZONE

    imap_url = urlparse(DEFAULT_IMAP_SERVER)
    assert shared_account.imap_port == imap_url.port  # 143
    assert shared_account.imap_schema == imap_url.scheme + "://"  # "imap://"
    assert shared_account.imap_server == imap_url.hostname

    smtp_url = urlparse(DEFAULT_SMTP_SERVER)
    assert shared_account.smtp_port == smtp_url.port  # 587
    assert shared_account.smtp_schema == smtp_url.scheme + "://"  # "smtp://"
    assert shared_account.smtp_server == smtp_url.hostname

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        user.properties["username"],
    )

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "none",
        "editor",
        ["sendOnBehalf", "writeSnippets"],
    )


def test_modify_shared_account(
    check_shared_account_support,
    udm,
    domainname,
    default_ox_context,
    create_ox_user,
    wait_for_listener,
    find_ox_object,
    new_account_name,
):
    user = create_ox_user()
    user_uoid = user.properties["univentionObjectIdentifier"]

    permission_uoid = create_shared_account_permission(
        udm,
        new_account_name,
        calendar="editor",
        mail="editor",
    )

    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users=[[user_uoid, permission_uoid]],
    )
    wait_for_listener(dn)

    # Prepare new properties by modifying all of them
    modified_account_name = f"{new_account_name}_mod"
    new_properties = {
        "name": modified_account_name,
        "displayName": get_shared_account_display_name(modified_account_name),
        "mailPrimaryAddress": f"{modified_account_name}@{domainname}",
    }

    dn = udm.modify("oxmail/shared_account", dn, new_properties)
    wait_for_listener(dn)

    # Since we modified 'name', we need to find the object by its new name
    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        modified_account_name,
    )

    assert shared_account.name == modified_account_name
    assert shared_account.display_name == get_shared_account_display_name(
        modified_account_name,
    )
    assert (
        shared_account.primaryEmail == f"{modified_account_name}@{domainname}"
    )


def test_delete_shared_account(
    check_shared_account_support,
    udm,
    domainname,
    default_ox_context,
    wait_for_listener,
    find_ox_object,
    new_account_name,
):
    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
    )
    wait_for_listener(dn)

    find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
        assert_empty=False,
    )

    udm.remove("oxmail/shared_account", dn)
    wait_for_listener(dn)

    find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
        assert_empty=True,
    )


def test_shared_account_add_user(
    check_shared_account_support,
    udm,
    default_ox_context,
    new_account_name,
    domainname,
    find_ox_object,
    create_ox_user,
    wait_for_listener,
):
    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
    )
    wait_for_listener(dn)

    user = create_ox_user()
    user_uoid = user.properties["univentionObjectIdentifier"]

    permission_uoid = create_shared_account_permission(
        udm,
        new_account_name,
        calendar="editor",
        mail="editor",
    )

    users = [[user_uoid, permission_uoid]]
    udm.modify("oxmail/shared_account", dn, {"users": users})
    wait_for_listener(dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )
    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        user.properties["username"],
    )

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "editor",
        "editor",
        [],
    )


def test_shared_account_add_user_and_rename_it(
    check_shared_account_support,
    udm,
    default_ox_context,
    new_account_name,
    domainname,
    find_ox_object,
    create_ox_user,
    wait_for_listener,
):
    user = create_ox_user()
    user_uoid = user.properties["univentionObjectIdentifier"]
    username = user.properties["username"]

    permission_uoid = create_shared_account_permission(
        udm,
        new_account_name,
        calendar="editor",
        mail="editor",
        sendOnBehalf=True,
    )

    users = [[user_uoid, permission_uoid]]

    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
    )
    wait_for_listener(dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )
    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(default_ox_context, "User", username)

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "editor",
        "editor",
        ["sendOnBehalf"],
    )

    username = username + "_2"
    dn = udm.modify("users/user", user.dn, {"username": username})
    wait_for_listener(dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(default_ox_context, "User", username)

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "editor",
        "editor",
        ["sendOnBehalf"],
    )


@pytest.mark.xfail(
    reason='This requires a new version of OX to work, see: https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/-/work_items/198',
)
def test_shared_account_add_user_in_another_context(
    check_shared_account_support,
    udm,
    domainname,
    new_account_name,
    create_ox_user,
    create_ox_context,
    wait_for_listener,
    find_ox_object,
):
    # (mail_level, calendar_level)
    configs = [
        ("editor", "editor"),
        ("editor", "none"),
        ("none", "editor"),
    ]

    user_data = []
    for mail, calendar in configs:
        ctx_id = create_ox_context()
        user = create_ox_user(context_id=ctx_id)
        perm_uuid = create_shared_account_permission(
            udm,
            f"perm_{mail}_{calendar}",
            mail=mail,
            calendar=calendar,
        )
        user_data.append(
            {
                "uoid": user.properties["univentionObjectIdentifier"],
                "username": user.properties["username"],
                "context_id": ctx_id,
                "perm_uuid": perm_uuid,
                "mail": mail,
                "calendar": calendar,
            },
        )

    users_list = [[d["uoid"], d["perm_uuid"]] for d in user_data]

    shared_ctx_id = create_ox_context()
    dn = create_shared_account(
        udm,
        shared_ctx_id,
        new_account_name,
        domainname,
        users_list,
        [],
    )
    wait_for_listener(dn)

    shared_account = find_ox_object(
        shared_ctx_id,
        "SharedAccount",
        new_account_name,
    )
    assert shared_account.name == new_account_name
    assert shared_account.display_name == get_shared_account_display_name(
        new_account_name,
    )
    assert shared_account.primaryEmail == f"{new_account_name}@{domainname}"

    permissions = shared_account.list_permissions()
    assert len(permissions) == len(user_data)

    for data in user_data:
        ox_user = find_ox_object(data["context_id"], "User", data["username"])
        permission = next(
            p
            for p in permissions
            if p.entity == ox_user.id and p.contextId == data["context_id"]
        )

        assert_permission(
            permission,
            shared_account,
            ox_user,
            data["calendar"],
            data["mail"],
            [],
        )


@pytest.mark.k8s_skip(
    reason="Shared account groups are currently not supported in provisioning backend",
)
def test_shared_account_add_group(
    check_shared_account_support,
    udm,
    default_ox_context,
    new_account_name,
    new_group_name,
    domainname,
    find_ox_object,
    create_ox_group,
    create_ox_user,
    wait_for_listener,
):
    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
    )
    wait_for_listener(dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )

    permission_uoid = create_shared_account_permission(
        udm,
        new_account_name,
        calendar="editor",
        mail="editor",
    )

    user = create_ox_user()

    # group with the user as member from the start
    group_dn = create_ox_group(new_group_name, members=[user.dn])
    group = udm.obj_by_dn(group_dn)
    group_uoid = group.properties["univentionObjectIdentifier"]

    groups = [[group_uoid, permission_uoid]]
    udm.modify("oxmail/shared_account", dn, {"groups": groups})
    wait_for_listener(dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_group = find_ox_object(default_ox_context, "Group", new_group_name)

    assert_permission(
        permission,
        shared_account,
        ox_group,
        "editor",
        "editor",
        [],
    )

    # group with the user as member after a while
    new_group_name = new_group_name + "_2"
    group_dn = create_ox_group(new_group_name)
    group = udm.obj_by_dn(group_dn)
    group_uoid = group.properties["univentionObjectIdentifier"]

    groups = [[group_uoid, permission_uoid]]
    udm.modify("oxmail/shared_account", dn, {"groups": groups})
    wait_for_listener(dn)

    # no permissions! group does not exist in OX (it is empty)
    permissions = shared_account.list_permissions()
    assert len(permissions) == 0

    udm.modify("groups/group", group_dn, {"users": [user.dn]})
    wait_for_listener(dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_group = find_ox_object(default_ox_context, "Group", new_group_name)

    assert_permission(
        permission,
        shared_account,
        ox_group,
        "editor",
        "editor",
        [],
    )


@pytest.mark.xfail(
    reason='This requires a new version of OX to work, see: https://git.knut.univention.de/univention/dev/projects/open-xchange/connector/-/work_items/198',
)
def test_shared_account_add_group_with_users_across_multiple_ox_contexts(
    check_shared_account_support,
    udm,
    domainname,
    new_group_name,
    create_ox_context,
    create_ox_user,
    create_ox_group,
    default_ox_context,
    new_account_name,
    find_ox_object,
    wait_for_listener,
):
    new_context_id = create_ox_context()
    user1 = create_ox_user()
    user2 = create_ox_user(context_id=new_context_id)
    group_dn = create_ox_group(new_group_name, members=[user1.dn, user2.dn])
    group = udm.obj_by_dn(group_dn)
    group_uoid = group.properties["univentionObjectIdentifier"]

    perm_uuid = create_shared_account_permission(
        udm,
        new_account_name + "_permission",
        mail="editor",
        snippets=True,
        writeSnippets=True,
    )
    groups = [
        [group_uoid, perm_uuid],
    ]

    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        [],
        groups,
    )
    wait_for_listener(dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 2


def test_shared_account_remove_user(
    check_shared_account_support,
    udm,
    domainname,
    create_ox_user,
    default_ox_context,
    new_account_name,
    find_ox_object,
    wait_for_listener,
):
    user1 = create_ox_user()
    user2 = create_ox_user()
    perm1_uuid = create_shared_account_permission(
        udm,
        new_account_name + "_permission_1",
        mail="editor",
    )
    perm2_uuid = create_shared_account_permission(
        udm,
        new_account_name + "_permission_2",
        mail="author",
        snippets=True,
        writeSnippets=True,
    )
    users = [
        [user1.properties["univentionObjectIdentifier"], perm1_uuid],
        [user2.properties["univentionObjectIdentifier"], perm2_uuid],
    ]

    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 2

    users = [[user2.properties["univentionObjectIdentifier"], perm2_uuid]]
    udm.modify("oxmail/shared_account", dn, {"users": users})
    wait_for_listener(dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        user2.properties["username"],
    )

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "none",
        "author",
        ["snippets", "writeSnippets"],
    )


@pytest.mark.k8s_skip(
    reason="Shared account groups are currently not supported in provisioning backend",
)
def test_shared_account_remove_group(
    check_shared_account_support,
    udm,
    domainname,
    new_group_name,
    create_ox_user,
    default_ox_context,
    new_account_name,
    find_ox_object,
    create_ox_group,
    wait_for_listener,
):
    user = create_ox_user()
    group1_dn = create_ox_group(new_group_name + "_1", members=[user.dn])
    group2_dn = create_ox_group(new_group_name + "_2", members=[user.dn])
    group1 = udm.obj_by_dn(group1_dn)
    group1_uoid = group1.properties["univentionObjectIdentifier"]
    group2 = udm.obj_by_dn(group2_dn)
    group2_uoid = group2.properties["univentionObjectIdentifier"]
    perm1_uuid = create_shared_account_permission(
        udm,
        new_account_name + "_permission_1",
        mail="editor",
        manageSieve=True,
        writeJSlob=True,
    )
    perm2_uuid = create_shared_account_permission(
        udm,
        new_account_name + "_permission_2",
        mail="author",
    )
    groups = [[group1_uoid, perm1_uuid], [group2_uoid, perm2_uuid]]

    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        [],
        groups,
    )
    wait_for_listener(dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 2

    groups = [[group1_uoid, perm1_uuid]]
    udm.modify("oxmail/shared_account", dn, {"groups": groups})
    wait_for_listener(dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_group = find_ox_object(
        default_ox_context,
        "Group",
        new_group_name + "_1",
    )

    assert_permission(
        permission,
        shared_account,
        ox_group,
        "none",
        "editor",
        ["manageSieve", "writeJSlob"],
    )


def test_shared_account_change_user(
    check_shared_account_support,
    udm,
    domainname,
    create_ox_user,
    default_ox_context,
    new_account_name,
    find_ox_object,
    wait_for_listener,
):
    user = create_ox_user()
    perm1_uuid = create_shared_account_permission(
        udm,
        new_account_name + "_permission_1",
        mail="editor",
        sendOnBehalf=True,
    )
    perm2_uuid = create_shared_account_permission(
        udm,
        new_account_name + "_permission_2",
        mail="author",
    )
    users = [[user.properties["univentionObjectIdentifier"], perm1_uuid]]

    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        user.properties["username"],
    )

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "none",
        "editor",
        ["sendOnBehalf"],
    )

    users = [[user.properties["univentionObjectIdentifier"], perm2_uuid]]
    udm.modify("oxmail/shared_account", dn, {"users": users})
    wait_for_listener(dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "none",
        "author",
        [],
    )


def test_shared_account_replace_user(
    check_shared_account_support,
    udm,
    domainname,
    create_ox_user,
    default_ox_context,
    new_account_name,
    find_ox_object,
    wait_for_listener,
):
    user1 = create_ox_user()
    user2 = create_ox_user()
    perm_uuid = create_shared_account_permission(
        udm,
        new_account_name + "_permission",
        mail="viewer",
        sendOnBehalf=True,
    )
    users = [[user1.properties["univentionObjectIdentifier"], perm_uuid]]

    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        user1.properties["username"],
    )

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "none",
        "viewer",
        ["sendOnBehalf"],
    )

    users = [[user2.properties["univentionObjectIdentifier"], perm_uuid]]
    udm.modify("oxmail/shared_account", dn, {"users": users})
    wait_for_listener(dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        user2.properties["username"],
    )

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "none",
        "viewer",
        ["sendOnBehalf"],
    )


@pytest.mark.k8s_skip(
    reason="Shared account groups are currently not supported in provisioning backend",
)
def test_shared_account_change_group(
    check_shared_account_support,
    udm,
    domainname,
    new_group_name,
    create_ox_user,
    create_ox_group,
    default_ox_context,
    new_account_name,
    find_ox_object,
    wait_for_listener,
):
    user = create_ox_user()
    group_dn = create_ox_group(new_group_name, members=[user.dn])
    group = udm.obj_by_dn(group_dn)
    group_uoid = group.properties["univentionObjectIdentifier"]
    perm1_uuid = create_shared_account_permission(
        udm,
        new_account_name + "_permission_1",
        mail="editor",
        sendOnBehalf=True,
    )
    perm2_uuid = create_shared_account_permission(
        udm,
        new_account_name + "_permission_2",
        mail="author",
        sendAs=True,
    )
    groups = [[group_uoid, perm1_uuid]]

    dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        [],
        groups,
    )
    wait_for_listener(dn)
    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_group = find_ox_object(default_ox_context, "Group", new_group_name)

    assert_permission(
        permission,
        shared_account,
        ox_group,
        "none",
        "editor",
        ["sendOnBehalf"],
    )

    groups = [[group_uoid, perm2_uuid]]
    udm.modify("oxmail/shared_account", dn, {"groups": groups})
    wait_for_listener(dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]

    assert_permission(
        permission,
        shared_account,
        ox_group,
        "none",
        "author",
        ["sendAs"],
    )


def test_shared_account_add_user_twice(
    check_shared_account_support,
    udm,
    domainname,
    create_ox_user,
    default_ox_context,
    wait_for_listener,
):
    user = create_ox_user()
    perm1_uuid = create_shared_account_permission(
        udm,
        "shared_account_permission_1",
        mail="editor",
    )
    perm2_uuid = create_shared_account_permission(
        udm,
        "shared_account_permission_2",
        mail="admin",
    )
    users = [
        [user.properties["univentionObjectIdentifier"], perm1_uuid],
        [user.properties["univentionObjectIdentifier"], perm2_uuid],
    ]
    with pytest.raises(UnprocessableEntity):
        create_shared_account(
            udm,
            default_ox_context,
            "shared_account_1",
            domainname,
            users,
            [],
        )


def test_shared_account_add_group_twice(
    check_shared_account_support,
    udm,
    domainname,
    new_group_name,
    create_ox_group,
    default_ox_context,
    wait_for_listener,
):
    group_dn = create_ox_group(new_group_name)
    group = udm.obj_by_dn(group_dn)
    group_uoid = group.properties["univentionObjectIdentifier"]
    perm1_uuid = create_shared_account_permission(
        udm,
        "shared_account_permission_1",
        mail="editor",
    )
    perm2_uuid = create_shared_account_permission(
        udm,
        "shared_account_permission_2",
        mail="admin",
    )
    groups = [[group_uoid, perm1_uuid], [group_uoid, perm2_uuid]]
    with pytest.raises(UnprocessableEntity):
        create_shared_account(
            udm,
            default_ox_context,
            "shared_account_1",
            domainname,
            [],
            groups,
        )


def test_create_shared_account_permission(
    check_shared_account_support,
    udm,
    wait_for_listener,
    new_account_name,
):
    dn = udm.create(
        "oxmail/shared_account_permission",
        "cn=shared_account_permissions,cn=open-xchange",
        {
            "name": new_account_name + "_permission",
            "displayName": get_shared_account_display_name(
                new_account_name + "_permission",
            ),
            "mail": "author",
            "calendar": "author",
            "sendAs": True,
            "sendOnBehalf": True,
            "snippets": True,
            "writeSnippets": True,
            "manageSieve": True,
            "writeJSlob": True,
        },
    )
    wait_for_listener(dn)


def test_modify_shared_account_permission(
    check_shared_account_support,
    udm,
    create_ox_user,
    wait_for_listener,
    new_account_name,
    default_ox_context,
    find_ox_object,
    domainname,
):
    dn = udm.create(
        "oxmail/shared_account_permission",
        "cn=shared_account_permissions,cn=open-xchange",
        {
            "name": new_account_name + "_permission",
            "displayName": get_shared_account_display_name(
                new_account_name + "_permission",
            ),
            "mail": "viewer",
            "calendar": "viewer",
            "sendAs": False,
            "sendOnBehalf": False,
            "snippets": False,
            "writeSnippets": False,
            "manageSieve": False,
            "writeJSlob": False,
        },
    )
    wait_for_listener(dn)
    permission = udm.obj_by_dn(dn)

    user = create_ox_user()
    users = [
        [
            user.properties["univentionObjectIdentifier"],
            permission.properties["univentionObjectIdentifier"],
        ],
    ]

    shared_account_dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(shared_account_dn)

    udm.modify("oxmail/shared_account_permission", dn, {"sendAs": True})
    wait_for_listener(shared_account_dn)

    ox_user = find_ox_object(
        default_ox_context,
        "User",
        user.properties["username"],
    )
    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        new_account_name,
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "viewer",
        "viewer",
        ["sendAs"],
    )


def test_delete_shared_account_permission(
    check_shared_account_support,
    udm,
    wait_for_listener,
    new_account_name,
):
    dn = udm.create(
        "oxmail/shared_account_permission",
        "cn=shared_account_permissions,cn=open-xchange",
        {
            "name": new_account_name + "_permission",
            "displayName": get_shared_account_display_name(
                new_account_name + "_permission",
            ),
            "mail": "viewer",
            "calendar": "viewer",
            "sendAs": False,
            "sendOnBehalf": True,
            "snippets": False,
            "writeSnippets": True,
            "manageSieve": False,
            "writeJSlob": True,
        },
    )
    wait_for_listener(dn)

    udm.remove("oxmail/shared_account_permission", dn)


def test_delete_shared_account_permission_if_user_is_linked_to_shared_account_with_that_permission(
    check_shared_account_support,
    udm,
    wait_for_listener,
    new_account_name,
    create_ox_user,
    default_ox_context,
    domainname,
):
    dn = udm.create(
        "oxmail/shared_account_permission",
        "cn=shared_account_permissions,cn=open-xchange",
        {
            "name": new_account_name + "_permission",
            "displayName": get_shared_account_display_name(
                new_account_name + "_permission",
            ),
            "mail": "none",
            "calendar": "none",
            "sendAs": True,
            "sendOnBehalf": False,
            "snippets": True,
            "writeSnippets": False,
            "manageSieve": True,
            "writeJSlob": False,
        },
    )
    wait_for_listener(dn)
    permission = udm.obj_by_dn(dn)

    user = create_ox_user()
    users = [
        [
            user.properties["univentionObjectIdentifier"],
            permission.properties["univentionObjectIdentifier"],
        ],
    ]

    shared_account_dn = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(shared_account_dn)

    with pytest.raises(UnprocessableEntity):
        # oxmail/shared_account_permission cannot be removed as long as they are referenced
        udm.remove("oxmail/shared_account_permission", dn)
