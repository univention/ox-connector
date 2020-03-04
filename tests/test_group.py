from univention.ox.backend_base import get_ox_integration_class


def create_context(udm, ox_host, context_id):
    dn = udm.create(
        "oxmail/oxcontext",
        "cn=open-xchange",
        {
            "oxQuota": 1000,
            "contextid": context_id,
            "name": "context{}".format(context_id),
        },
    )
    return dn


def create_user(udm, name, domainname, context_id, enabled=True):
    dn = udm.create(
        "users/user",
        "cn=users",
        {
            "username": name,
            "firstname": "Emil",
            "lastname": name.title(),
            "password": "univention",
            "mailPrimaryAddress": "{}@{}".format(name, domainname),
            "isOxUser": enabled,
            "oxAccess": "premium",
            "oxContext": context_id,
        },
    )
    return dn


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
    default_ox_context,
    new_user_name,
    new_group_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    isOxGroup = Not should not create a group
    """
    user_dn = create_user(udm, new_user_name, domainname, default_ox_context)
    create_obj(udm, new_group_name, [user_dn], enabled=False)
    wait_for_listener(user_dn)
    find_obj(default_ox_context, new_user_name, assert_empty=True)


def test_enable_and_disable_group(
    new_context_id_generator,
    new_user_name_generator,
    new_group_name,
    ox_host,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Changing isOxGroup from Not to OK should create a group
    Changing isOxGroup from OK to Not should delete a group
    """
    new_context_id = new_context_id_generator()
    create_context(udm, ox_host, new_context_id)
    user_dn1 = create_user(udm, new_user_name_generator(), domainname, new_context_id)
    new_context_id2 = new_context_id_generator()
    create_context(udm, ox_host, new_context_id2)
    user_dn2 = create_user(udm, new_user_name_generator(), domainname, new_context_id2)
    user_dn3 = create_user(udm, new_user_name_generator(), domainname, new_context_id2)
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
    default_ox_context,
    new_user_name,
    new_group_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    isOxGroup = OK should create a group
    UDM attributes should be reflected in OX
    """
    user_dn = create_user(udm, new_user_name, domainname, default_ox_context)
    group_dn = create_obj(udm, new_group_name, [user_dn])
    wait_for_listener(group_dn)
    obj = find_obj(default_ox_context, new_group_name)
    assert obj.name == new_group_name
    assert len(obj.members) == 1


def test_add_group_with_one_enabled_user_and_one_disabled(
    new_context_id,
    ox_host,
    new_user_name_generator,
    new_group_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    isOxGroup = OK should create a group
    UDM attributes should be reflected in OX
    """
    create_context(udm, ox_host, new_context_id)
    user_dn1 = create_user(udm, new_user_name_generator(), domainname, new_context_id)
    user_dn2 = create_user(udm, new_user_name_generator(), domainname, None, enabled=False)
    group_dn = create_obj(udm, new_group_name, [user_dn1, user_dn2])
    wait_for_listener(group_dn)
    obj = find_obj(new_context_id, new_group_name)
    assert obj.name == new_group_name
    assert len(obj.members) == 1


def test_rename_group(
    default_ox_context,
    new_user_name,
    new_group_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Renaming a group should keep ID
    """
    user_dn = create_user(udm, new_user_name, domainname, default_ox_context)
    dn = create_obj(udm, new_group_name, [user_dn])
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, new_group_name)
    old_id = obj.id
    udm.modify("groups/group", dn, {"name": "new" + new_group_name})
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, "new" + new_group_name)
    assert obj.id == old_id


def test_add_group_with_multiple_users_and_contexts(
    new_context_id_generator,
    new_user_name_generator,
    new_group_name,
    ox_host,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Adding users from different OX contexts to a group should add the group to
    each of those contexts with the correct members
    """
    new_context_id = new_context_id_generator()
    create_context(udm, ox_host, new_context_id)
    user_dn1 = create_user(udm, new_user_name_generator(), domainname, new_context_id)
    new_context_id2 = new_context_id_generator()
    create_context(udm, ox_host, new_context_id2)
    user_dn2 = create_user(udm, new_user_name_generator(), domainname, new_context_id2)
    user_dn3 = create_user(udm, new_user_name_generator(), domainname, new_context_id2)
    group_dn = create_obj(udm, new_group_name, [user_dn1, user_dn2, user_dn3])
    wait_for_listener(group_dn)
    obj = find_obj(new_context_id, new_group_name)
    assert obj.name == new_group_name
    assert len(obj.members) == 1
    obj2 = find_obj(new_context_id2, new_group_name)
    assert obj2.name == new_group_name
    assert len(obj2.members) == 2


def test_modify_group(
    default_ox_context,
    new_user_name,
    new_group_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Modifications in UDM should be reflected in OX
    """
    user_dn = create_user(udm, new_user_name, domainname, default_ox_context)
    dn = create_obj(udm, new_group_name, [user_dn])
    udm.modify("groups/group", dn, {"name": "x" + new_group_name + "x"})
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, "x" + new_group_name + "x")
    assert obj.name == "x" + new_group_name + "x"
    assert len(obj.members) == 1


def test_rename_user(
    default_ox_context,
    new_user_name,
    new_group_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Renaming user should keep User ID in groups member list
    """
    user_dn = create_user(udm, new_user_name, domainname, default_ox_context)
    group_dn = create_obj(udm, new_group_name, [user_dn])
    wait_for_listener(group_dn)
    obj = find_obj(default_ox_context, new_group_name)
    old_members = obj.members
    udm.modify("users/user", user_dn, {"username": "new" + new_user_name})
    wait_for_listener(group_dn)
    obj = find_obj(default_ox_context, new_group_name)
    assert old_members == obj.members


def test_remove_user(
    default_ox_context,
    new_user_name_generator,
    new_group_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Deleting one user from group should remove him from groups member list
    Deleting last user from group should delete group
    """
    user_dn1 = create_user(udm, new_user_name_generator(), domainname, default_ox_context)
    user_dn2 = create_user(udm, new_user_name_generator(), domainname, default_ox_context)
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
    default_ox_context,
    new_context_id,
    new_group_name,
    new_user_name_generator,
    udm,
    ox_host,
    domainname,
    wait_for_listener,
):
    """
    Deleting a group should delete it from all contexts
    """
    create_context(udm, ox_host, new_context_id)
    user_dn1 = create_user(udm, new_user_name_generator(), domainname, default_ox_context)
    user_dn2 = create_user(udm, new_user_name_generator(), domainname, new_context_id)
    dn = create_obj(udm, new_group_name, [user_dn1, user_dn2])
    wait_for_listener(dn)
    find_obj(new_context_id, new_group_name)
    udm.remove("groups/group", dn)
    wait_for_listener(dn)
    find_obj(default_ox_context, new_group_name, assert_empty=True)
    find_obj(new_context_id, new_group_name, assert_empty=True)
