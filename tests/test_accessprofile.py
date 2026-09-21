# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import pytest

from univention.ox.provisioning.accessprofiles import (
    get_access_profile,
    get_access_profiles,
)


def create_obj(udm, name, right):
    obj = udm.create(
        "oxmail/accessprofile",
        "cn=accessprofiles,cn=open-xchange",
        {
            "name": name,
            "displayName": name.replace("_", " ").title(),
            right: True,
        },
    )
    return obj.dn


def find_access(find_ox_object, context_id, name, assert_empty=False):
    obj = find_ox_object(context_id, "User", name, assert_empty)
    return obj.service(obj.context_id).get_module_access({"id": obj.id})


def test_disabled_user(
    udm,
    default_ox_context,
    new_user_name,
    create_ox_user,
    wait_for_listener,
    file_utility,
    find_ox_object,
):
    """
    A disabled user must have no OX access rights
    """
    ox_access = "accessprofile_test_disabled_user"
    assert get_access_profile(ox_access) is None
    dn = create_obj(udm, ox_access, "usm")
    wait_for_listener(dn)
    fname = "/var/lib/univention-appcenter/apps/ox-connector/data/ModuleAccessDefinitions.properties"
    with file_utility.open(fname) as fd:
        content = fd.read()
        assert f"{ox_access}=usm\n" in content
    get_access_profiles(force_reload=True)
    assert get_access_profile(ox_access) == ["USM"]

    create_ox_user(
        name=new_user_name,
        further_udm_attrs={"oxAccess": ox_access, "disabled": True},
    )
    access = find_access(find_ox_object, default_ox_context, new_user_name)
    for right in access:
        if right == "OLOX20" or right == "publication":  # deprecated rights
            continue
        assert access[right] is False


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
    create_ox_user,
    wait_for_listener,
    right,
    right_soap,
    file_utility,
    find_ox_object,
):
    """
    Create a right object for every right and test existance.
    """
    ox_access = f"accessprofile_{right}"
    assert get_access_profile(ox_access) is None
    dn = create_obj(udm, ox_access, right)
    wait_for_listener(dn)
    fname = "/var/lib/univention-appcenter/apps/ox-connector/data/ModuleAccessDefinitions.properties"
    with file_utility.open(fname) as fd:
        content = fd.read()
        assert f"{ox_access}={right}\n" in content
    get_access_profiles(force_reload=True)
    profile = get_access_profile(ox_access)
    assert profile == [right_soap]
    user_dn = create_ox_user(
        name=new_user_name,
        further_udm_attrs={"oxAccess": ox_access},
    ).dn
    access = find_access(find_ox_object, default_ox_context, new_user_name)
    assert access[right_soap] is True
    for _right in access:
        if _right == "OLOX20" or _right == "publication":  # deprecated rights
            continue
        if _right != right_soap:
            assert access[_right] is False

    udm.remove(
        "users/user",
        user_dn,
    )  # needs to be removed before accessprofile
    udm.remove("oxmail/accessprofile", dn)
    wait_for_listener(dn)
    get_access_profiles(force_reload=True)
    assert get_access_profile(ox_access) is None
    with file_utility.open(fname) as fd:
        content = fd.read()
        assert f"{ox_access}={right}\n" not in content


@pytest.mark.parametrize(
    "special_character",
    [
        '!',
        '#',
        '$',
        '%',
        '&',
        "'",
        '*',
        '-',
        '.',
        '/',
        ':',
        '?',
        '@',
        '[',
        ']',
        '^',
        '_',
        '`',
        '{',
        '|',
        '}',
        '~',
    ],
)
def test_accessprofile_with_special_characters(
    udm,
    default_ox_context,
    new_user_name,
    create_ox_user,
    wait_for_listener,
    special_character,
    file_utility,
    find_ox_object,
):
    """
    Create an access profile with special characters and test existance.
    """
    ox_access = f"accessprofile_{special_character}"
    assert get_access_profile(ox_access) is None
    dn = create_obj(udm, ox_access, "usm")
    wait_for_listener(dn)
    fname = "/var/lib/univention-appcenter/apps/ox-connector/data/ModuleAccessDefinitions.properties"
    with file_utility.open(fname) as fd:
        content = fd.read()
        assert f"{ox_access}=usm\n" in content
    get_access_profiles(force_reload=True)
    profile = get_access_profile(ox_access)
    assert profile == ["USM"]
    user_dn = create_ox_user(
        name=new_user_name,
        further_udm_attrs={"oxAccess": ox_access},
    ).dn
    access = find_access(find_ox_object, default_ox_context, new_user_name)
    assert access["USM"] is True
    for _right in access:
        if _right == "OLOX20" or _right == "publication":  # deprecated rights
            continue
        if _right != "USM":
            assert access[_right] is False

    udm.remove(
        "users/user",
        user_dn,
    )  # needs to be removed before accessprofile
    udm.remove("oxmail/accessprofile", dn)
    wait_for_listener(dn)
    get_access_profiles(force_reload=True)
    assert get_access_profile(ox_access) is None
    with file_utility.open(fname) as fd:
        content = fd.read()
        assert f"{ox_access}=usm\n" not in content
