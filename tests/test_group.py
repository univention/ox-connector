# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

from univention.ox.soap.backend_base import get_ox_integration_class


def create_obj(udm, name, members, enabled=True):
    dn = udm.create(
        "groups/group",
        "cn=groups",
        {"name": name, "users": members, "isOxGroup": enabled},
    )
    return dn


def find_obj(context_id, name, assert_empty=False):
    Group = get_ox_integration_class("SOAP", "Group")
    objs = Group.list(context_id, pattern=name)
    if assert_empty:
        assert len(objs) == 0
    else:
        assert len(objs) == 1
        obj = objs[0]
        print("Found", obj)
        return obj


def test_ignore_group(
        create_ox_user,
        default_ox_context,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    isOxGroup = Not should not create a group
    """
    user_dn = create_ox_user().dn
    dn = create_obj(udm, new_group_name, [user_dn], enabled=False)
    wait_for_listener(dn)
    find_obj(default_ox_context, new_group_name, assert_empty=True)


def test_enable_and_disable_group(
        create_ox_context,
        create_ox_user,
        new_group_name,
        ox_host,
        udm,
        wait_for_listener,
):
    """
    Changing isOxGroup from Not to OK should create a group
    Changing isOxGroup from OK to Not should delete a group
    """
    new_context_id = create_ox_context()
    user_dn1 = create_ox_user(context_id=new_context_id).dn
    new_context_id2 = create_ox_context()
    user_dn2 = create_ox_user(context_id=new_context_id2).dn
    user_dn3 = create_ox_user(context_id=new_context_id2).dn
    dn = create_obj(udm, new_group_name, [user_dn1, user_dn2, user_dn3], enabled=False)
    wait_for_listener(dn)
    find_obj(new_context_id, new_group_name, assert_empty=True)
    find_obj(new_context_id2, new_group_name, assert_empty=True)
    udm.modify("groups/group", dn, {"isOxGroup": True})
    wait_for_listener(dn)
    find_obj(new_context_id, new_group_name)
    find_obj(new_context_id2, new_group_name)
    udm.modify("groups/group", dn, {"isOxGroup": False})
    wait_for_listener(dn)
    find_obj(new_context_id, new_group_name, assert_empty=True)
    find_obj(new_context_id2, new_group_name, assert_empty=True)


def test_add_group_with_one_user(
        create_ox_user,
        default_ox_context,
        new_user_name,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    isOxGroup = OK should create a group
    UDM attributes should be reflected in OX
    """
    user_dn = create_ox_user().dn
    group_dn = create_obj(udm, new_group_name, [user_dn])
    wait_for_listener(group_dn)
    obj = find_obj(default_ox_context, new_group_name)
    assert obj.name == new_group_name
    assert len(obj.members) == 1


def test_add_group_with_one_enabled_user_and_one_disabled(
        create_ox_context,
        create_ox_user,
        ox_host,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    isOxGroup = OK should create a group
    UDM attributes should be reflected in OX
    """
    new_context_id = create_ox_context()
    user_dn1 = create_ox_user(context_id=new_context_id).dn
    user_dn2 = create_ox_user(enabled=False).dn
    group_dn = create_obj(udm, new_group_name, [user_dn1, user_dn2])
    wait_for_listener(group_dn)
    obj = find_obj(new_context_id, new_group_name)
    assert obj.name == new_group_name
    assert len(obj.members) == 1


def test_change_context_for_group_multi_user(
        create_ox_context,
        create_ox_user,
        ox_host,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    If a user changes the oxContext, the group needs to update its members
    in the old and in the new context
    """
    context_id = create_ox_context()
    new_context_id = create_ox_context()
    user_dn = create_ox_user(context_id=context_id).dn
    user_dn1 = create_ox_user(context_id=context_id).dn
    user_dn2 = create_ox_user(context_id=new_context_id).dn
    group_dn = create_obj(udm, new_group_name, [user_dn, user_dn1, user_dn2])
    wait_for_listener(group_dn)
    find_obj(context_id, new_group_name)
    udm.modify("users/user", user_dn, {"oxContext": new_context_id})
    wait_for_listener(group_dn)
    assert len(find_obj(context_id, new_group_name).members) == 1
    assert len(find_obj(new_context_id, new_group_name).members) == 2


def test_change_context_for_group_user(
        create_ox_context,
        create_ox_user,
        ox_host,
        new_user_name,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    If a user changes the oxContext, the group should be removed from the old
    context and created in the new context
    """
    context_id = create_ox_context()
    user_dn = create_ox_user(context_id=context_id).dn
    group_dn = create_obj(udm, new_group_name, [user_dn])
    wait_for_listener(group_dn)
    find_obj(context_id, new_group_name)
    new_context_id = create_ox_context()
    udm.modify("users/user", user_dn, {"oxContext": new_context_id})
    wait_for_listener(group_dn)
    find_obj(context_id, new_group_name, assert_empty=True)
    find_obj(new_context_id, new_group_name)


def test_rename_group(
        create_ox_user,
        default_ox_context,
        new_user_name,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    Renaming a group should keep ID
    """
    user_dn = create_ox_user().dn
    dn = create_obj(udm, new_group_name, [user_dn])
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, new_group_name)
    old_id = obj.id
    udm.modify("groups/group", dn, {"name": "new" + new_group_name})
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, "new" + new_group_name)
    assert obj.id == old_id


def test_add_group_with_multiple_users_and_contexts(
        create_ox_context,
        create_ox_user,
        new_group_name,
        ox_host,
        udm,
        wait_for_listener,
):
    """
    Adding users from different OX contexts to a group should add the group to
    each of those contexts with the correct members
    """
    new_context_id = create_ox_context()
    user_dn1 = create_ox_user(context_id=new_context_id).dn
    new_context_id2 = create_ox_context()
    user_dn2 = create_ox_user(context_id=new_context_id2).dn
    user_dn3 = create_ox_user(context_id=new_context_id2).dn
    group_dn = create_obj(udm, new_group_name, [user_dn1, user_dn2, user_dn3])
    wait_for_listener(group_dn)
    obj = find_obj(new_context_id, new_group_name)
    assert obj.name == new_group_name
    assert len(obj.members) == 1
    obj2 = find_obj(new_context_id2, new_group_name)
    assert obj2.name == new_group_name
    assert len(obj2.members) == 2


def test_modify_group(
        create_ox_user,
        default_ox_context,
        new_user_name,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    Modifications in UDM should be reflected in OX
    """
    user_dn = create_ox_user().dn
    dn = create_obj(udm, new_group_name, [user_dn])
    udm.modify("groups/group", dn, {"name": "x" + new_group_name + "x"})
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, "x" + new_group_name + "x")
    assert obj.name == "x" + new_group_name + "x"
    assert len(obj.members) == 1


def test_rename_user(
        create_ox_user,
        default_ox_context,
        new_user_name,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    Renaming user should keep User ID in groups member list
    """
    user_dn = create_ox_user().dn
    group_dn = create_obj(udm, new_group_name, [user_dn])
    wait_for_listener(group_dn)
    obj = find_obj(default_ox_context, new_group_name)
    old_members = obj.members
    udm.modify("users/user", user_dn, {"username": "new" + new_user_name})
    wait_for_listener(group_dn)
    obj = find_obj(default_ox_context, new_group_name)
    assert old_members == obj.members


def test_remove_user(
        create_ox_user,
        default_ox_context,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    Deleting one user from group should remove him from groups member list
    Deleting last user from group should delete group
    """
    user_dn1 = create_ox_user().dn
    user_dn2 = create_ox_user().dn
    group_dn = create_obj(udm, new_group_name, [user_dn1, user_dn2])
    wait_for_listener(group_dn)
    obj = find_obj(default_ox_context, new_group_name)
    assert len(obj.members) == 2
    udm.remove("users/user", user_dn1)
    wait_for_listener(group_dn)
    obj = find_obj(default_ox_context, new_group_name)
    assert len(obj.members) == 1
    udm.remove("users/user", user_dn2)
    wait_for_listener(group_dn)
    find_obj(default_ox_context, new_group_name, assert_empty=True)


def test_remove_group(
        create_ox_context,
        create_ox_user,
        default_ox_context,
        new_group_name,
        udm,
        ox_host,
        wait_for_listener,
):
    """
    Deleting a group should delete it from all contexts
    """
    new_context_id = create_ox_context()
    user_dn1 = create_ox_user().dn
    user_dn2 = create_ox_user(context_id=new_context_id).dn
    dn = create_obj(udm, new_group_name, [user_dn1, user_dn2])
    wait_for_listener(dn)
    find_obj(new_context_id, new_group_name)
    udm.remove("groups/group", dn)
    wait_for_listener(dn)
    find_obj(default_ox_context, new_group_name, assert_empty=True)
    find_obj(new_context_id, new_group_name, assert_empty=True)


def test_remove_last_member_of_group_two_members(
        create_ox_user,
        default_ox_context,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    Removing the last member of a group should remove the group from the context,
    with two members
    Ticket: https://git.knut.univention.de/univention/open-xchange/provisioning
    /-/issues/29
    """
    # Create a group with two users
    user_dn1 = create_ox_user().dn
    user_dn2 = create_ox_user().dn
    group_dn = create_obj(udm, new_group_name, [user_dn1, user_dn2])
    wait_for_listener(group_dn)
    group = find_obj(default_ox_context, new_group_name)
    assert len(group.members) == 2

    # Remove a user
    udm.remove("users/user", user_dn1)
    wait_for_listener(group_dn)
    updated_group = find_obj(default_ox_context, new_group_name)
    assert len(updated_group.members) == 1

    # Remove another user, this should as well remove the group
    udm.remove("users/user", user_dn2)
    wait_for_listener(group_dn)
    find_obj(default_ox_context, new_group_name, assert_empty=True)


def test_remove_last_member_of_group_one_member(
        create_ox_user,
        default_ox_context,
        new_group_name,
        udm,
        wait_for_listener,
):
    """
    Removing the last member of a group should remove the group from the context,
    with one member
    Ticket: https://git.knut.univention.de/univention/open-xchange/provisioning
    /-/issues/29
    """
    # Create a group with one user
    user_dn1 = create_ox_user().dn
    group_dn = create_obj(udm, new_group_name, [user_dn1])
    wait_for_listener(group_dn)
    group = find_obj(default_ox_context, new_group_name)
    assert len(group.members) == 1

    # Remove the user, this should as well remove the group
    udm.remove("users/user", user_dn1)
    wait_for_listener(group_dn)
    find_obj(default_ox_context, new_group_name, assert_empty=True)
