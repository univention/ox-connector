# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import os
import pytest
from urllib.parse import urlparse

from univention.ox.provisioning.shared_account import (
    _get_name as _get_name_shared_accounts,
)
from univention.ox.provisioning.users import _get_name as _get_name_users
from univention.ox.provisioning.groups import _get_name as _get_name_groups
from univention.ox.soap.config import (
    DEFAULT_IMAP_SERVER,
    DEFAULT_LANGUAGE,
    DEFAULT_SMTP_SERVER,
    LOCAL_TIMEZONE,
)
from univention.ox.soap.types import Types

from udm_rest import UnprocessableEntity


def get_identifier_shared_account(udm_object):
    return _get_name_shared_accounts(udm_object.properties)


def get_identifier_user(udm_object):
    return _get_name_users(udm_object.properties)


def get_identifier_group(udm_object):
    return _get_name_groups(udm_object.properties)


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
    obj = udm.create(
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
    print("Created account", obj.dn, "in UDM")
    return obj


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
    obj = udm.create(
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
    print("Created account permission", obj.dn, "in UDM")
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
    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(sa_obj.dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
    )

    assert shared_account.name == get_identifier_shared_account(sa_obj)
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
        get_identifier_user(user),
    )

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "none",
        "editor",
        ["sendOnBehalf", "writeSnippets"],
    )


@pytest.mark.skipif(
    os.getenv("OX_SHARED_ACCOUNT_IDENTIFIER") != "name",
    reason="""
Modifying the shared account seems to not work properly when using a different identifier.
If remove modifying of the name it works, but when modifying the name the display name is not modified
but no errors from UDM or OX. Needs investigation.""",
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

    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users=[[user_uoid, permission_uoid]],
    )
    wait_for_listener(sa_obj.dn)

    # Prepare new properties by modifying all of them
    modified_account_name = f"{new_account_name}_mod"
    new_properties = {
        "name": modified_account_name,
        "displayName": get_shared_account_display_name(modified_account_name),
        "mailPrimaryAddress": f"{modified_account_name}@{domainname}",
    }

    new_obj = udm.modify("oxmail/shared_account", sa_obj.dn, new_properties)
    wait_for_listener(new_obj.dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(new_obj),
    )

    assert shared_account.name == get_identifier_shared_account(new_obj)
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
    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
    )
    wait_for_listener(sa_obj.dn)

    find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
        assert_empty=False,
    )

    udm.remove("oxmail/shared_account", sa_obj.dn)
    wait_for_listener(sa_obj.dn)

    find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
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
    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
    )
    wait_for_listener(sa_obj.dn)

    user = create_ox_user()
    user_uoid = user.properties["univentionObjectIdentifier"]

    permission_uoid = create_shared_account_permission(
        udm,
        new_account_name,
        calendar="editor",
        mail="editor",
    )

    users = [[user_uoid, permission_uoid]]
    udm.modify("oxmail/shared_account", sa_obj.dn, {"users": users})
    wait_for_listener(sa_obj.dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
    )
    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        get_identifier_user(user),
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

    permission_uoid = create_shared_account_permission(
        udm,
        new_account_name,
        calendar="editor",
        mail="editor",
        sendOnBehalf=True,
    )

    users = [[user_uoid, permission_uoid]]

    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
    )
    wait_for_listener(sa_obj.dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
    )
    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        get_identifier_user(user),
    )

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "editor",
        "editor",
        ["sendOnBehalf"],
    )

    new_username = user.properties["username"] + "_2"
    new_obj = udm.modify("users/user", user.dn, {"username": new_username})
    wait_for_listener(new_obj.dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        get_identifier_user(new_obj),
    )

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
                "user": user,
                "context_id": ctx_id,
                "perm_uuid": perm_uuid,
                "mail": mail,
                "calendar": calendar,
            },
        )

    users_list = [[d["uoid"], d["perm_uuid"]] for d in user_data]

    shared_ctx_id = create_ox_context()
    sa_obj = create_shared_account(
        udm,
        shared_ctx_id,
        new_account_name,
        domainname,
        users_list,
        [],
    )
    wait_for_listener(sa_obj.dn)

    shared_account = find_ox_object(
        shared_ctx_id,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
    )
    assert shared_account.name == get_identifier_shared_account(sa_obj)
    assert shared_account.display_name == get_shared_account_display_name(
        new_account_name,
    )
    assert shared_account.primaryEmail == f"{new_account_name}@{domainname}"

    permissions = shared_account.list_permissions()
    assert len(permissions) == len(user_data)

    for data in user_data:
        ox_user = find_ox_object(
            data["context_id"],
            "User",
            get_identifier_user(data["user"]),
        )
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
    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
    )
    wait_for_listener(sa_obj.dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
    )

    permission_uoid = create_shared_account_permission(
        udm,
        new_account_name,
        calendar="editor",
        mail="editor",
    )

    user = create_ox_user()

    # group with the user as member from the start
    group = create_ox_group(new_group_name, members=[user.dn])
    group_uoid = group.properties["univentionObjectIdentifier"]

    groups = [[group_uoid, permission_uoid]]
    udm.modify("oxmail/shared_account", sa_obj.dn, {"groups": groups})
    wait_for_listener(sa_obj.dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_group = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier_group(group),
    )

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
    group = create_ox_group(new_group_name)
    group_uoid = group.properties["univentionObjectIdentifier"]

    groups = [[group_uoid, permission_uoid]]
    udm.modify("oxmail/shared_account", sa_obj.dn, {"groups": groups})
    wait_for_listener(sa_obj.dn)

    # no permissions! group does not exist in OX (it is empty)
    permissions = shared_account.list_permissions()
    assert len(permissions) == 0

    udm.modify("groups/group", group.dn, {"users": [user.dn]})
    wait_for_listener(sa_obj.dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_group = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier_group(group),
    )

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
    group = create_ox_group(new_group_name, members=[user1.dn, user2.dn])
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

    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        [],
        groups,
    )
    wait_for_listener(sa_obj.dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
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

    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(sa_obj.dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 2

    users = [[user2.properties["univentionObjectIdentifier"], perm2_uuid]]
    udm.modify("oxmail/shared_account", sa_obj.dn, {"users": users})
    wait_for_listener(sa_obj.dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        get_identifier_user(user2),
    )

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "none",
        "author",
        ["snippets", "writeSnippets"],
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
    group1 = create_ox_group(new_group_name + "_1", members=[user.dn])
    group2 = create_ox_group(new_group_name + "_2", members=[user.dn])
    group1_uoid = group1.properties["univentionObjectIdentifier"]
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

    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        [],
        groups,
    )
    wait_for_listener(sa_obj.dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 2

    groups = [[group1_uoid, perm1_uuid]]
    udm.modify("oxmail/shared_account", sa_obj.dn, {"groups": groups})
    wait_for_listener(sa_obj.dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_group = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier_group(group1),
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

    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(sa_obj.dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        get_identifier_user(user),
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
    udm.modify("oxmail/shared_account", sa_obj.dn, {"users": users})
    wait_for_listener(sa_obj.dn)

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

    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(sa_obj.dn)

    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        get_identifier_user(user1),
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
    udm.modify("oxmail/shared_account", sa_obj.dn, {"users": users})
    wait_for_listener(sa_obj.dn)

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_user = find_ox_object(
        default_ox_context,
        "User",
        get_identifier_user(user2),
    )

    assert_permission(
        permission,
        shared_account,
        ox_user,
        "none",
        "viewer",
        ["sendOnBehalf"],
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
    group = create_ox_group(new_group_name, members=[user.dn])
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

    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        [],
        groups,
    )
    wait_for_listener(sa_obj.dn)
    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
    )

    permissions = shared_account.list_permissions()
    assert len(permissions) == 1
    permission = permissions[0]
    ox_group = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier_group(group),
    )

    assert_permission(
        permission,
        shared_account,
        ox_group,
        "none",
        "editor",
        ["sendOnBehalf"],
    )

    groups = [[group_uoid, perm2_uuid]]
    udm.modify("oxmail/shared_account", sa_obj.dn, {"groups": groups})
    wait_for_listener(sa_obj.dn)

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
    group = create_ox_group(new_group_name)
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
    obj = udm.create(
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
    wait_for_listener(obj.dn)


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
    permission = udm.create(
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
    wait_for_listener(permission.dn)

    user = create_ox_user()
    users = [
        [
            user.properties["univentionObjectIdentifier"],
            permission.properties["univentionObjectIdentifier"],
        ],
    ]

    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(sa_obj.dn)

    udm.modify(
        "oxmail/shared_account_permission",
        permission.dn,
        {"sendAs": True},
    )
    wait_for_listener(sa_obj.dn)

    ox_user = find_ox_object(
        default_ox_context,
        "User",
        get_identifier_user(user),
    )
    shared_account = find_ox_object(
        default_ox_context,
        "SharedAccount",
        get_identifier_shared_account(sa_obj),
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
    obj = udm.create(
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
    wait_for_listener(obj.dn)

    udm.remove("oxmail/shared_account_permission", obj.dn)


def test_delete_shared_account_permission_if_user_is_linked_to_shared_account_with_that_permission(
    check_shared_account_support,
    udm,
    wait_for_listener,
    new_account_name,
    create_ox_user,
    default_ox_context,
    domainname,
):
    permission = udm.create(
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
    wait_for_listener(permission.dn)

    user = create_ox_user()
    users = [
        [
            user.properties["univentionObjectIdentifier"],
            permission.properties["univentionObjectIdentifier"],
        ],
    ]

    sa_obj = create_shared_account(
        udm,
        default_ox_context,
        new_account_name,
        domainname,
        users,
        [],
    )
    wait_for_listener(sa_obj.dn)

    with pytest.raises(UnprocessableEntity):
        # oxmail/shared_account_permission cannot be removed as long as they are referenced
        udm.remove("oxmail/shared_account_permission", permission.dn)
