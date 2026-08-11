# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

from univention.ox.provisioning.groups import _get_name


def get_identifier(udm_object):
    return _get_name(udm_object.properties)


def test_ignore_group(
    find_ox_object,
    create_ox_user,
    create_ox_group,
    default_ox_context,
    new_group_name,
    udm,
    wait_for_listener,
):
    """
    isOxGroup = False (Not) should not create a group
    """
    user_dn = create_ox_user().dn
    create_ox_group(new_group_name, members=[user_dn], enabled=False)
    find_ox_object(
        default_ox_context,
        "Group",
        new_group_name,
        assert_empty=True,
    )


def test_enable_and_disable_group(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    create_ox_group,
    new_group_name,
    ox_host,
    udm,
    wait_for_listener,
):
    """
    Changing isOxGroup from False (Not) to True (OK) should create a group
    Changing isOxGroup from True (OK) to False (Not) should delete a group
    """
    new_context_id = create_ox_context()
    user_dn1 = create_ox_user(context_id=new_context_id).dn
    new_context_id2 = create_ox_context()
    user_dn2 = create_ox_user(context_id=new_context_id2).dn
    user_dn3 = create_ox_user(context_id=new_context_id2).dn
    group_obj = create_ox_group(
        new_group_name,
        members=[user_dn1, user_dn2, user_dn3],
        enabled=False,
    )
    find_ox_object(
        new_context_id,
        "Group",
        get_identifier(group_obj),
        assert_empty=True,
    )
    find_ox_object(
        new_context_id2,
        "Group",
        get_identifier(group_obj),
        assert_empty=True,
    )
    udm.modify("groups/group", group_obj.dn, {"isOxGroup": True})
    wait_for_listener(group_obj.dn)
    find_ox_object(new_context_id, "Group", get_identifier(group_obj))
    find_ox_object(new_context_id2, "Group", get_identifier(group_obj))
    udm.modify("groups/group", group_obj.dn, {"isOxGroup": False})
    wait_for_listener(group_obj.dn)
    find_ox_object(
        new_context_id,
        "Group",
        get_identifier(group_obj),
        assert_empty=True,
    )
    find_ox_object(
        new_context_id2,
        "Group",
        get_identifier(group_obj),
        assert_empty=True,
    )


def test_add_group_with_one_user(
    find_ox_object,
    create_ox_user,
    create_ox_group,
    default_ox_context,
    new_user_name,
    new_group_name,
    udm,
    wait_for_listener,
):
    """
    isOxGroup = True (OK) should create a group
    UDM attributes should be reflected in OX
    """
    user_dn = create_ox_user().dn
    group_obj = create_ox_group(new_group_name, members=[user_dn])
    obj = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
    )
    assert obj.name == get_identifier(group_obj)
    assert obj.display_name == group_obj.properties.get("name")
    assert len(obj.members) == 1


def test_add_group_with_one_enabled_user_and_one_disabled(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    create_ox_group,
    ox_host,
    new_group_name,
    udm,
    wait_for_listener,
):
    """
    isOxGroup = True (OK) should create a group
    UDM attributes should be reflected in OX
    """
    new_context_id = create_ox_context()
    user_dn1 = create_ox_user(context_id=new_context_id).dn
    user_dn2 = create_ox_user(enabled=False).dn
    group_obj = create_ox_group(new_group_name, members=[user_dn1, user_dn2])
    obj = find_ox_object(new_context_id, "Group", get_identifier(group_obj))
    assert obj.name == get_identifier(group_obj)
    assert len(obj.members) == 1


def test_change_context_for_group_multi_user(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    create_ox_group,
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
    group_obj = create_ox_group(
        new_group_name,
        members=[user_dn, user_dn1, user_dn2],
    )
    assert (
        len(
            find_ox_object(
                context_id,
                "Group",
                get_identifier(group_obj),
            ).members,
        )
        == 2
    )
    assert (
        len(
            find_ox_object(
                new_context_id,
                "Group",
                get_identifier(group_obj),
            ).members,
        )
        == 1
    )

    udm.modify("users/user", user_dn, {"oxContext": new_context_id})
    wait_for_listener(group_obj.dn)
    assert (
        len(
            find_ox_object(
                context_id,
                "Group",
                get_identifier(group_obj),
            ).members,
        )
        == 1
    )
    assert (
        len(
            find_ox_object(
                new_context_id,
                "Group",
                get_identifier(group_obj),
            ).members,
        )
        == 2
    )


def test_change_context_for_group_user(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    create_ox_group,
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
    group_obj = create_ox_group(new_group_name, members=[user_dn])
    find_ox_object(context_id, "Group", get_identifier(group_obj))
    new_context_id = create_ox_context()
    udm.modify("users/user", user_dn, {"oxContext": new_context_id})
    wait_for_listener(group_obj.dn)
    find_ox_object(
        context_id,
        "Group",
        get_identifier(group_obj),
        assert_empty=True,
    )
    find_ox_object(new_context_id, "Group", get_identifier(group_obj))


def test_rename_group(
    find_ox_object,
    create_ox_user,
    create_ox_group,
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
    group_obj = create_ox_group(new_group_name, members=[user_dn])
    obj = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
    )
    old_id = obj.id
    new_obj = udm.modify(
        "groups/group",
        group_obj.dn,
        {"name": f"new{new_group_name}"},
    )
    wait_for_listener(new_obj.dn)
    obj = find_ox_object(default_ox_context, "Group", get_identifier(new_obj))
    assert obj.id == old_id
    assert obj.display_name == new_obj.properties.get("name")


def test_add_group_with_multiple_users_and_contexts(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    create_ox_group,
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
    group_obj = create_ox_group(
        new_group_name,
        members=[user_dn1, user_dn2, user_dn3],
    )
    obj = find_ox_object(new_context_id, "Group", get_identifier(group_obj))
    assert obj.name == get_identifier(group_obj)
    assert len(obj.members) == 1
    obj2 = find_ox_object(new_context_id2, "Group", get_identifier(group_obj))
    assert obj2.name == get_identifier(group_obj)
    assert len(obj2.members) == 2


def test_modify_group(
    find_ox_object,
    create_ox_user,
    create_ox_group,
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
    group_obj = create_ox_group(new_group_name, members=[user_dn])
    new_obj = udm.modify(
        "groups/group",
        group_obj.dn,
        {"name": f"x{new_group_name}x"},
    )
    wait_for_listener(new_obj.dn)
    obj = find_ox_object(default_ox_context, "Group", get_identifier(new_obj))
    assert obj.name == get_identifier(new_obj)
    assert obj.display_name == new_obj.properties.get("name")
    assert len(obj.members) == 1


def test_rename_user(
    find_ox_object,
    create_ox_user,
    create_ox_group,
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
    group_obj = create_ox_group(new_group_name, members=[user_dn])
    obj = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
    )
    old_members = obj.members
    udm.modify("users/user", user_dn, {"username": "new" + new_user_name})
    wait_for_listener(group_obj.dn)
    obj = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
    )
    assert old_members == obj.members


def test_remove_user(
    find_ox_object,
    create_ox_user,
    create_ox_group,
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
    group_obj = create_ox_group(new_group_name, members=[user_dn1, user_dn2])
    obj = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
    )
    assert len(obj.members) == 2
    udm.remove("users/user", user_dn1)
    wait_for_listener(group_obj.dn)
    obj = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
    )
    assert len(obj.members) == 1
    udm.remove("users/user", user_dn2)
    wait_for_listener(group_obj.dn)
    find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
        assert_empty=True,
    )


def test_remove_group(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    create_ox_group,
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
    group_obj = create_ox_group(new_group_name, members=[user_dn1, user_dn2])
    find_ox_object(new_context_id, "Group", get_identifier(group_obj))
    udm.remove("groups/group", group_obj.dn)
    wait_for_listener(group_obj.dn)
    find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
        assert_empty=True,
    )
    find_ox_object(
        new_context_id,
        "Group",
        get_identifier(group_obj),
        assert_empty=True,
    )


def test_remove_last_member_of_group_two_members(
    find_ox_object,
    create_ox_user,
    create_ox_group,
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
    group_obj = create_ox_group(new_group_name, members=[user_dn1, user_dn2])
    group = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
    )
    assert len(group.members) == 2

    # Remove a user
    udm.remove("users/user", user_dn1)
    wait_for_listener(group_obj.dn)
    updated_group = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
    )
    assert len(updated_group.members) == 1

    # Remove another user, this should as well remove the group
    udm.remove("users/user", user_dn2)
    wait_for_listener(group_obj.dn)
    find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
        assert_empty=True,
    )


def test_remove_last_member_of_group_one_member(
    find_ox_object,
    create_ox_user,
    create_ox_group,
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
    group_obj = create_ox_group(new_group_name, members=[user_dn1])
    group = find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
    )
    assert len(group.members) == 1

    # Remove the user, this should as well remove the group
    udm.remove("users/user", user_dn1)
    wait_for_listener(group_obj.dn)
    find_ox_object(
        default_ox_context,
        "Group",
        get_identifier(group_obj),
        assert_empty=True,
    )
