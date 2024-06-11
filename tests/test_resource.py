# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import pytest
from univention.ox.soap.backend_base import get_ox_integration_class


def create_obj(udm, name, domainname, context_id, user, attrs=None):
    default_attrs = {
        "name": name,
        "displayname": name,
        "description": "A description for {}".format(name),
        "resourceMailAddress": "{}@{}".format(name, domainname),
        "resourceadmin": str(user.properties["uidNumber"]),
        "oxContext": context_id,
    }

    if attrs is not None:
        default_attrs.update(attrs)

    dn = udm.create(
        "oxresources/oxresources",
        "cn=oxresources,cn=open-xchange",
        default_attrs,
    )
    return dn


def find_obj(context_id, name, assert_empty=False):
    Resource = get_ox_integration_class("SOAP", "Resource")
    objs = Resource.list(context_id, pattern=name)
    if assert_empty:
        assert len(objs) == 0
    else:
        assert len(objs) == 1
        obj = objs[0]
        print("Found", obj)
        return obj


def test_add_resource_in_default_context(
        default_ox_context,
        new_resource_name,
        create_ox_user,
        udm,
        domainname,
        new_user_name,
        wait_for_listener,
):
    """
    Creating a resource without a context should create it in OX' default context
    """
    user = create_ox_user(new_user_name)
    dn = create_obj(udm, new_resource_name, domainname, None, user)
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, new_resource_name)
    assert obj.display_name == new_resource_name
    assert obj.description == "A description for {}".format(new_resource_name)
    assert obj.email == "{}@{}".format(new_resource_name, domainname)


def test_add_resource(
        new_context_id,
        new_resource_name,
        udm,
        create_ox_context,
        create_ox_user,
        domainname,
        new_user_name,
        wait_for_listener,
):
    """
    Creating a resource should create it in OX
    """
    create_ox_context(new_context_id)
    user = create_ox_user(new_user_name, new_context_id)
    dn = create_obj(udm, new_resource_name, domainname, new_context_id, user)
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_resource_name)
    assert obj.display_name == new_resource_name
    assert obj.description == "A description for {}".format(new_resource_name)
    assert obj.email == "{}@{}".format(new_resource_name, domainname)


def test_modify_resource(
        new_context_id,
        new_resource_name,
        udm,
        create_ox_context,
        create_ox_user,
        domainname,
        new_user_name,
        wait_for_listener,
):
    """
    Modification of attributes are reflected in OX
    """
    new_mail_address = "{}2@{}".format(new_resource_name, domainname)
    create_ox_context(new_context_id)
    user = create_ox_user(new_user_name, new_context_id)
    dn = create_obj(udm, new_resource_name, domainname, new_context_id, user)
    wait_for_listener(dn)
    new_attrs = {
        "description": f"foo {new_resource_name} bar",
        "displayname": "New Display",
        "resourceMailAddress": new_mail_address,
    }
    udm.modify("oxresources/oxresources", dn, new_attrs)
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_resource_name)
    assert obj.display_name == new_attrs["displayname"]
    assert obj.email == new_attrs["resourceMailAddress"]
    assert obj.description == new_attrs["description"]


def test_remove_resource(
        new_context_id,
        new_resource_name,
        udm,
        create_ox_context,
        create_ox_user,
        domainname,
        new_user_name,
        wait_for_listener,
):
    """
    Deleting a resource should delete it from OX
    """
    create_ox_context(new_context_id)
    user = create_ox_user(new_user_name, new_context_id)
    dn = create_obj(udm, new_resource_name, domainname, new_context_id, user)
    wait_for_listener(dn)
    udm.remove("oxresources/oxresources", dn)
    wait_for_listener(dn)
    find_obj(new_context_id, new_resource_name, assert_empty=True)


def test_change_context_resource(
        new_context_id_generator,
        new_resource_name,
        udm,
        create_ox_context,
        create_ox_user,
        domainname,
        new_user_name,
        wait_for_listener,
):
    """
    Special case: If a resource changes its context, the object is
    deleted from the old and newly created in the other context. Attributes
    stay, though.
    """
    new_context_id = new_context_id_generator()
    create_ox_context(new_context_id)
    user = create_ox_user(new_user_name, new_context_id)
    dn = create_obj(udm, new_resource_name, domainname, new_context_id, user)
    wait_for_listener(dn)
    new_context_id2 = new_context_id_generator()
    create_ox_context(new_context_id2)
    udm.modify("oxresources/oxresources", dn, {"description": "Soon in a new context"})
    wait_for_listener(dn)
    udm.modify(
        "oxresources/oxresources",
        dn,
        {"oxContext": new_context_id2, "displayname": "New Object in new Context"},
    )
    wait_for_listener(dn)
    find_obj(new_context_id, new_resource_name, assert_empty=True)
    obj = find_obj(new_context_id2, new_resource_name)
    assert obj.display_name == "New Object in new Context"
    assert obj.description == "Soon in a new context"


def test_empty_name_resource(
        udm,
        domainname,
        default_ox_context,
        new_user_name,
        wait_for_listener,
        create_ox_user
):
    user = create_ox_user(new_user_name)
    empty_name = ""

    # Name is required, so this should fail
    with pytest.raises(Exception):
        dn = create_obj(udm, empty_name, domainname, default_ox_context, user)
        wait_for_listener(dn)


def test_all_empty_attributes_resource(
        default_ox_context,
        new_resource_name,
        create_ox_user,
        udm,
        domainname,
        new_user_name,
        wait_for_listener,
):
    empty_attrs = {
        "name": "",
        "displayname": "",
        "description": "",
        "resourceMailAddress": "",
        "resourceadmin": "",
        "oxContext": "",
    }
    user = create_ox_user(new_user_name)

    # All fields are required (except description), so this should fail
    with pytest.raises(Exception):
        dn = create_obj(udm, empty_attrs["name"], domainname, default_ox_context, user)
        wait_for_listener(dn)


def test_unset_all_attributes_resource(
        default_ox_context,
        new_resource_name,
        udm,
        create_ox_context,
        create_ox_user,
        domainname,
        new_user_name,
        wait_for_listener,
):
    # Create a resource with all attributes set
    resource_name = "TestResourceWithAttributes"
    initial_attrs = {
        "name": resource_name,
        "displayname": "Test Resource",
        "description": "A test resource",
        "resourceMailAddress": f"{resource_name}@{domainname}",
        "resourceadmin": "admin123",
    }

    user = create_ox_user(new_user_name)
    dn = create_obj(udm, resource_name, domainname, default_ox_context,
                    user, attrs=initial_attrs)
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, resource_name)

    assert obj is not None

    # Unset all attributes (only description can be set to an empty value,
    # as the other attributes are required)
    unset_attrs = {
        "description": "",
    }

    udm.modify("oxresources/oxresources", dn, unset_attrs)
    wait_for_listener(dn)
    obj_after_unset = find_obj(default_ox_context, resource_name)

    assert obj_after_unset.description is None
    assert obj_after_unset.name == resource_name


def test_invalid_context_id_resource(
        udm,
        domainname,
        wait_for_listener,
        create_ox_user
):
    invalid_context_id = "invalid_context_id"
    user = create_ox_user("test_user")

    # Context ID must be an integer, so this should fail
    with pytest.raises(Exception):
        create_obj(udm, "invalid_resource", domainname, invalid_context_id, user)


def test_missing_user_resource(
        udm,
        domainname,
        default_ox_context,
        wait_for_listener,
):
    # User is required, so this should fail
    with pytest.raises(Exception):
        create_obj(udm, "some_name", domainname, default_ox_context, None)


def test_missing_name_resource(
        udm,
        domainname,
        default_ox_context,
        wait_for_listener,
        create_ox_user
):
    user = create_ox_user("test_user")

    # Name is required, so this should fail
    with pytest.raises(Exception):
        create_obj(udm, None, domainname, default_ox_context, user)


def test_wrong_name_resource(
        udm,
        domainname,
        default_ox_context,
        wait_for_listener,
        create_ox_user
):
    user = create_ox_user("test_user")

    # Name must be a string, so this should fail
    with pytest.raises(Exception):
        create_obj(udm, [1, 2, 3], domainname, default_ox_context, user)


def test_delete_already_deleted_resource(
        udm,
        domainname,
        default_ox_context,
        wait_for_listener,
        create_ox_user
):
    user = create_ox_user("test_user")
    dn = create_obj(udm, "resource_to_be_deleted", domainname,
                    default_ox_context, user)
    wait_for_listener(dn)
    udm.remove("oxresources/oxresources", dn)
    wait_for_listener(dn)

    # Deleting a resource that has already been deleted should fail
    with pytest.raises(Exception):
        udm.remove("oxresources/oxresources", dn)
