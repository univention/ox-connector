import pytest

from univention.ox.backend_base import get_ox_integration_class
from univention.ox.provisioning.accessprofiles import (
    get_access_profile,
    get_access_profiles,
)


def create_user(udm, name, domainname, context_id, ox_access):
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
            "oxAccess": ox_access,
            "oxContext": context_id,
        },
    )
    return dn


def create_obj(udm, name, right):
    dn = udm.create(
        "oxmail/accessprofile",
        "cn=accessprofiles,cn=open-xchange",
        {"name": name, "displayName": name.replace("_", " ").title(), right: True},
    )
    return dn


def find_access(context_id, name, assert_empty=False, print_obj=True):
    User = get_ox_integration_class("SOAP", "User")
    objs = User.list(context_id, pattern=name)
    if assert_empty:
        assert len(objs) == 0
    else:
        assert len(objs) == 1
        obj = objs[0]
        if print_obj:
            print("Found", obj)
        return obj.service(obj.context_id).get_module_access({"id": obj.id})


@pytest.mark.parametrize(
    "right,right_soap",
    [
        ("usm", "USM"),
        ("activesync", "activeSync"),
        ("calendar", "calendar"),
        ("collectemailaddresses", "collectEmailAddresses"),
        ("contacts", "contacts"),
        ("delegatetask", "delegateTask"),
        ("deniedportal", "deniedPortal"),
        ("editgroup", "editGroup"),
        ("editpassword", "editPassword"),
        ("editpublicfolders", "editPublicFolders"),
        ("editresource", "editResource"),
        ("globaladdressbookdisabled", "globalAddressBookDisabled"),
        ("ical", "ical"),
        ("infostore", "infostore"),
        ("multiplemailaccounts", "multipleMailAccounts"),
        ("readcreatesharedfolders", "readCreateSharedFolders"),
        ("subscription", "subscription"),
        ("syncml", "syncml"),
        ("tasks", "tasks"),
        ("vcard", "vcard"),
        ("webdav", "webdav"),
        ("webdavxml", "webdavXml"),
        ("webmail", "webmail"),
    ],
)
def test_every_one_right_access_profile(
    udm,
    default_ox_context,
    new_user_name,
    wait_for_listener,
    domainname,
    right,
    right_soap,
):
    """
    Create a right object for every right and test existance.
    """
    ox_access = f"accessprofile_{right}"
    assert get_access_profile(ox_access) is None
    dn = create_obj(udm, ox_access, right)
    wait_for_listener(dn)
    fname = "/var/lib/univention-appcenter/apps/ox-connector/data/ModuleAccessDefinitions.properties"
    with open(fname) as fd:
        content = fd.read()
        assert f"{ox_access}={right}\n" in content
    get_access_profiles(force_reload=True)
    profile = get_access_profile(ox_access)
    assert profile == [right_soap]
    user_dn = create_user(udm, new_user_name, domainname, default_ox_context, ox_access)
    wait_for_listener(user_dn)
    access = find_access(default_ox_context, new_user_name)
    assert access[right_soap] is True
    for _right in access:
        if _right == 'OLOX20' or _right == 'publication': # deprecated rights
            continue
        if _right != right_soap:
            assert access[_right] is False

    udm.remove("users/user", user_dn)  # needs to be removed before accessprofile
    udm.remove("oxmail/accessprofile", dn)
    wait_for_listener(dn)
    get_access_profiles(force_reload=True)
    assert get_access_profile(ox_access) is None
    with open(fname) as fd:
        content = fd.read()
        assert f"{ox_access}={right}\n" not in content
