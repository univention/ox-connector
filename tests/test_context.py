# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

from univention.ox.soap.backend_base import get_ox_integration_class


def create_context(udm, ox_host, context_id, max_quota=1000):
    dn = udm.create(
        "oxmail/oxcontext",
        "cn=open-xchange",
        {
            "oxQuota": max_quota,
            "contextid": context_id,
            "name": "context{}".format(context_id),
        },
    )
    return dn


def context_exists(context_id):
    Context = get_ox_integration_class("SOAP", "Context")
    cs = Context.list(pattern=context_id)
    return len(cs) == 1


def test_add_context(new_context_id, udm, ox_host, wait_for_listener):
    """
    Creating a UDM context object should create one in OX
    """
    dn = create_context(udm, ox_host, new_context_id)
    wait_for_listener(dn)
    Context = get_ox_integration_class("SOAP", "Context")
    cs = Context.list(pattern=new_context_id)
    assert len(cs) == 1
    c = cs[0]
    assert c.name == "context{}".format(new_context_id)
    assert c.max_quota == 1000


def test_add_context_without_quota(
    new_context_id,
    udm,
    ox_host,
    wait_for_listener,
):
    """
    Creating a UDM context object should create one in OX
    """
    dn = create_context(udm, ox_host, new_context_id, None)
    wait_for_listener(dn)
    Context = get_ox_integration_class("SOAP", "Context")
    cs = Context.list(pattern=new_context_id)
    assert len(cs) == 1
    c = cs[0]
    assert c.name == "context{}".format(new_context_id)
    assert c.max_quota is None


def test_modify_context(new_context_id, udm, ox_host, wait_for_listener):
    """
    Modification of the attributes should be reflected
    (currently only holds for quota)
    """
    dn = create_context(udm, ox_host, new_context_id)
    wait_for_listener(dn)
    udm.modify("oxmail/oxcontext", dn, {"oxQuota": 2000})
    wait_for_listener(dn)
    Context = get_ox_integration_class("SOAP", "Context")
    cs = Context.list(pattern=new_context_id)
    assert len(cs) == 1
    c = cs[0]
    assert c.name == "context{}".format(new_context_id)
    assert c.max_quota == 2000


def test_remove_context(new_context_id, udm, ox_host, wait_for_listener):
    """
    Deleting a UDM context object should delete it in OX
    """
    dn = create_context(udm, ox_host, new_context_id)
    wait_for_listener(dn)
    assert context_exists(new_context_id)

    udm.remove("oxmail/oxcontext", dn)
    wait_for_listener(dn)
    assert not context_exists(new_context_id)
