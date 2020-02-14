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


def test_add_context(new_context_id, udm, ox_host):
    """
    Creating a UDM context object should create one in OX
    """
    create_context(udm, ox_host, new_context_id)
    Context = get_ox_integration_class("SOAP", "Context")
    cs = Context.list(pattern=new_context_id)
    assert len(cs) == 1
    c = cs[0]
    assert c.name == "context{}".format(new_context_id)
    assert c.max_quota == 1000


def test_modify_context(new_context_id, udm, ox_host):
    """
    Modification of the attributes should be reflected
    (currently only holds for quota)
    """
    dn = create_context(udm, ox_host, new_context_id)
    udm.modify("oxmail/oxcontext", dn, {"oxQuota": 2000})
    Context = get_ox_integration_class("SOAP", "Context")
    cs = Context.list(pattern=new_context_id)
    assert len(cs) == 1
    c = cs[0]
    assert c.name == "context{}".format(new_context_id)
    assert c.max_quota == 2000


def test_remove_context(new_context_id, udm, ox_host):
    """
    Deleting a UDM context object should delete it in OX
    """
    dn = create_context(udm, ox_host, new_context_id)
    udm.remove("oxmail/oxcontext", dn)
    Context = get_ox_integration_class("SOAP", "Context")
    cs = Context.list(pattern=new_context_id)
    assert len(cs) == 0
