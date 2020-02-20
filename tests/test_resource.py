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
    )
    return dn


def create_obj(udm, name, domainname, context_id, ox_admin):
    dn = udm.create(
        "oxresources/oxresources",
        "cn=oxresources,cn=open-xchange",
        {
            "name": name,
            "displayname": name.upper(),
            "description": "A description for {}".format(name),
            "resourceMailAddress": "{}@{}".format(name, domainname),
            "resourceadmin": str(ox_admin.properties["uidNumber"]),
            "oxContext": context_id,
        },
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
    default_ox_context, new_resource_name, udm, domainname, ox_admin_udm_user
):
    """
    Creating a resource without a context should create it in OX' default context
    """
    create_obj(udm, new_resource_name, domainname, None, ox_admin_udm_user)
    obj = find_obj(default_ox_context, new_resource_name)
    assert obj.display_name == new_resource_name.upper()
    assert obj.description == "A description for {}".format(new_resource_name)
    assert obj.email == "{}@{}".format(new_resource_name, domainname)


def test_add_resource(
    new_context_id,
    new_resource_name,
    udm,
    ox_host,
    domainname,
    ox_admin_udm_user,
    wait_for_listener,
):
    """
    Creating a resource should create it in OX
    """
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(
        udm, new_resource_name, domainname, new_context_id, ox_admin_udm_user
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_resource_name)
    assert obj.display_name == new_resource_name.upper()
    assert obj.description == "A description for {}".format(new_resource_name)
    assert obj.email == "{}@{}".format(new_resource_name, domainname)


def test_modify_resource(
    new_context_id,
    new_resource_name,
    udm,
    ox_host,
    domainname,
    ox_admin_udm_user,
    wait_for_listener,
):
    """
    Modification of attributes are reflected in OX
    """
    new_mail_address = "{}2@{}".format(new_resource_name, domainname)
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(
        udm, new_resource_name, domainname, new_context_id, ox_admin_udm_user
    )
    udm.modify(
        "oxresources/oxresources",
        dn,
        {
            "description": None,
            "displayname": "New Display",
            "resourceMailAddress": new_mail_address,
        },
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_resource_name)
    assert obj.display_name == "New Display"
    assert obj.email == new_mail_address
    assert obj.description is None  # FIXME: fails...


def test_remove_resource(
    new_context_id,
    new_resource_name,
    udm,
    ox_host,
    domainname,
    ox_admin_udm_user,
    wait_for_listener,
):
    """
    Deleting a resource should delete it from OX
    """
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(
        udm, new_resource_name, domainname, new_context_id, ox_admin_udm_user
    )
    udm.remove("oxresources/oxresources", dn)
    wait_for_listener(dn)
    find_obj(new_context_id, new_resource_name, assert_empty=True)


def test_change_context_resource(
    new_context_id_generator,
    new_resource_name,
    udm,
    ox_host,
    domainname,
    ox_admin_udm_user,
    wait_for_listener,
):
    """
    Special case: If a resource changes its context, the object is
    deleted from the old and newly created in the other context. Attributes
    stay, though.
    """
    new_context_id = new_context_id_generator()
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(
        udm, new_resource_name, domainname, new_context_id, ox_admin_udm_user
    )
    new_context_id2 = new_context_id_generator()
    create_context(udm, ox_host, new_context_id2)
    udm.modify("oxresources/oxresources", dn, {"description": "Soon in a new context"})
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
