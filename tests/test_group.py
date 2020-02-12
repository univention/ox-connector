#!/usr/bin/py.test

from univention.ox.backend_base import get_ox_integration_class


def create_context(udm, ox_host, context_id):
    dn = udm.create(
        "oxmail/oxcontext",
        "cn=open-xchange",
        {
            "hostname": ox_host,
            "oxQuota": 1000,
            "oxDBServer": ox_host,
            "oxintegrationversion": "11.0.0-32A~4.4.0.201911191756",
            "contextid": context_id,
            "name": "context{}".format(context_id),
        },
        wait_for_listener=False,
    )
    return dn


def create_user(udm, name, domainname, context_id):
    dn = udm.create(
        "users/user",
        "cn=users",
        {
            "username": name,
            "firstname": "Emil",
            "lastname": name.title(),
            "password": "univention",
            "mailPrimaryAddress": "{}@{}".format(name, domainname),
            "isOxUser": True,
            "oxAccess": "premium",
            "oxContext": context_id,
        },
        wait_for_listener=False,
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
    default_ox_context, new_user_name, new_group_name, udm, domainname
):
    user_dn = create_user(udm, new_user_name, domainname, None)
    create_obj(udm, new_group_name, [user_dn], enabled=False)
    find_obj(default_ox_context, new_user_name, assert_empty=True)


def test_enable_and_disable_group(
    new_context_id_generator,
    new_user_name_generator,
    new_group_name,
    ox_host,
    udm,
    domainname,
):
    new_context_id = new_context_id_generator()
    create_context(udm, ox_host, new_context_id)
    user_dn1 = create_user(udm, new_user_name_generator(), domainname, new_context_id)
    new_context_id2 = new_context_id_generator()
    create_context(udm, ox_host, new_context_id2)
    user_dn2 = create_user(udm, new_user_name_generator(), domainname, new_context_id2)
    user_dn3 = create_user(udm, new_user_name_generator(), domainname, new_context_id2)
    dn = create_obj(udm, new_group_name, [user_dn1, user_dn2, user_dn3], enabled=False)
    find_obj(new_context_id, new_group_name, assert_empty=True)
    find_obj(new_context_id2, new_group_name, assert_empty=True)
    udm.modify("groups/group", dn, {"isOxGroup": True})
    find_obj(new_context_id, new_group_name)
    find_obj(new_context_id2, new_group_name)
    udm.modify("groups/group", dn, {"isOxGroup": False})
    find_obj(new_context_id, new_group_name, assert_empty=True)
    find_obj(new_context_id2, new_group_name, assert_empty=True)


def test_add_group_with_one_user(
    default_ox_context, new_user_name, new_group_name, udm, domainname
):
    user_dn = create_user(udm, new_user_name, domainname, None)
    create_obj(udm, new_group_name, [user_dn])
    obj = find_obj(default_ox_context, new_group_name)
    assert obj.name == new_group_name
    assert len(obj.members) == 1


def test_rename_group(
    default_ox_context, new_user_name, new_group_name, udm, domainname
):
    user_dn = create_user(udm, new_user_name, domainname, None)
    dn = create_obj(udm, new_group_name, [user_dn])
    obj = find_obj(default_ox_context, new_group_name)
    old_id = obj.id
    udm.modify("groups/group", dn, {"name": "new" + new_group_name})
    obj = find_obj(default_ox_context, "new" + new_group_name)
    assert obj.id == old_id


def test_add_group_with_multiple_users_and_contexts(
    new_context_id_generator,
    new_user_name_generator,
    new_group_name,
    ox_host,
    udm,
    domainname,
):
    new_context_id = new_context_id_generator()
    create_context(udm, ox_host, new_context_id)
    user_dn1 = create_user(udm, new_user_name_generator(), domainname, new_context_id)
    new_context_id2 = new_context_id_generator()
    create_context(udm, ox_host, new_context_id2)
    user_dn2 = create_user(udm, new_user_name_generator(), domainname, new_context_id2)
    user_dn3 = create_user(udm, new_user_name_generator(), domainname, new_context_id2)
    create_obj(udm, new_group_name, [user_dn1, user_dn2, user_dn3])
    obj = find_obj(new_context_id, new_group_name)
    assert obj.name == new_group_name
    assert len(obj.members) == 1
    obj2 = find_obj(new_context_id2, new_group_name)
    assert obj2.name == new_group_name
    assert len(obj2.members) == 2


def test_modify_group(
    default_ox_context, new_user_name, new_group_name, udm, domainname
):
    user_dn = create_user(udm, new_user_name, domainname, None)
    dn = create_obj(udm, new_group_name, [user_dn])
    udm.modify("groups/group", dn, {"name": "x" + new_group_name + "x"})
    obj = find_obj(default_ox_context, "x" + new_group_name + "x")
    assert obj.name == "x" + new_group_name + "x"
    assert len(obj.members) == 1


def test_rename_user(
    default_ox_context, new_user_name, new_group_name, udm, domainname
):
    user_dn = create_user(udm, new_user_name, domainname, None)
    create_obj(udm, new_group_name, [user_dn])
    obj = find_obj(default_ox_context, new_group_name)
    old_members = obj.members
    print(old_members)
    udm.modify("users/user", user_dn, {"username": "new" + new_user_name})
    obj = find_obj(default_ox_context, new_group_name)
    assert old_members == obj.members
    assert obj.members == None


def test_remove_user(
    default_ox_context, new_user_name_generator, new_group_name, udm, domainname
):
    user_dn1 = create_user(udm, new_user_name_generator(), domainname, None)
    user_dn2 = create_user(udm, new_user_name_generator(), domainname, None)
    create_obj(udm, new_group_name, [user_dn1, user_dn2])
    obj = find_obj(default_ox_context, new_group_name)
    assert len(obj.members) == 2
    udm.remove("users/user", user_dn1)
    obj = find_obj(default_ox_context, new_group_name)
    assert len(obj.members) == 1
    udm.remove("users/user", user_dn2)
    find_obj(default_ox_context, new_group_name, assert_empty=True)


def test_remove_group(
    new_context_id, new_group_name, new_user_name, udm, ox_host, domainname
):
    create_context(udm, ox_host, new_context_id)
    user_dn = create_user(udm, new_user_name, domainname, new_context_id)
    dn = create_obj(udm, new_group_name, [user_dn])
    find_obj(new_context_id, new_group_name)
    udm.remove("groups/group", dn)
    find_obj(new_context_id, new_group_name, assert_empty=True)
