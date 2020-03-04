import uuid
from collections import namedtuple

import pytest

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


def create_obj(udm, name, domainname, context_id, attrs=None, enabled=True):
    _attrs = {
        "username": name,
        "firstname": "Emil",
        "lastname": name.title(),
        "password": "univention",
        "mailPrimaryAddress": "{}@{}".format(name, domainname),
        "isOxUser": enabled,
        "oxAccess": "premium",
        "oxContext": context_id,
    }
    if attrs:
        _attrs.update(attrs)
    dn = udm.create("users/user", "cn=users", _attrs,)
    return dn


def find_obj(context_id, name, assert_empty=False, print_obj=True):
    User = get_ox_integration_class("SOAP", "User")
    objs = User.list(context_id, pattern=name)
    if assert_empty:
        assert len(objs) == 0
    else:
        assert len(objs) == 1
        obj = objs[0]
        if print_obj:
            print("Found", obj)
        return obj


def delete_obj(context_id, name):
    obj = find_obj(context_id, name)
    print("Removing", obj.id, "directly in OX")
    obj.remove()
    find_obj(context_id, name, assert_empty=True)


def test_ignore_user(
    default_ox_context, new_user_name, udm, domainname, wait_for_listener
):
    """
    isOxUser = Not should not create a user
    """
    dn = create_obj(udm, new_user_name, domainname, None, enabled=False)
    wait_for_listener(dn)
    find_obj(default_ox_context, new_user_name, assert_empty=True)


def test_add_user_in_default_context(
    default_ox_context, new_user_name, udm, domainname, wait_for_listener
):
    """
    Creating a user without a context should add it in the default context
    """
    dn = create_obj(udm, new_user_name, domainname, default_ox_context)
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, new_user_name)
    assert obj.name == new_user_name
    assert obj.email1 == "{}@{}".format(new_user_name, domainname)


def test_rename_user(
    default_ox_context, new_user_name, udm, domainname, wait_for_listener
):
    """
    Renaming a user should keep its ID
    """
    dn = create_obj(udm, new_user_name, domainname, default_ox_context)
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, new_user_name)
    old_id = obj.id
    udm.modify(
        "users/user", dn, {"username": "new" + new_user_name},
    )
    wait_for_listener(dn)
    obj = find_obj(default_ox_context, "new" + new_user_name)
    assert old_id == obj.id


def test_add_user(
    new_context_id, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    """
    isOxUser = OK should create a user
    """
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.name == new_user_name
    assert obj.email1 == "{}@{}".format(new_user_name, domainname)


def test_modify_user(
    new_context_id, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    """
    Changing UDM object should be reflected in OX
    """
    new_mail_address = "{}2@{}".format(new_user_name, domainname)
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    wait_for_listener(dn)  # make sure we wait for the modify step below
    udm.modify(
        "users/user",
        dn,
        {
            "lastname": "Newman",
            "mailPrimaryAddress": new_mail_address,
            "oxCommercialRegister": "A register",
        },
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.email1 == new_mail_address
    assert obj.commercial_register == "A register"
    assert obj.sur_name == "Newman"


def no_none():
    return NotImplemented


def none():
    return None


def empty():
    return []


def random_string():
    return str(uuid.uuid4())


def ident(x):
    return x


def take_first(x):
    if len(x) > 0:
        return x[0]


def take_second(x):
    if len(x) > 1:
        return x[1]


def random_mail_address():
    import os

    domainname = os.environ["DOMAINNAME"]
    return f"{random_string()}@{domainname}"


def random_list_of_string():
    return [random_string()]


def random_list_of_strings():
    return ["xxx", random_string()]


def random_language():
    return "fr_FR"  # very random


def random_timezone():
    return "Australia/Sydney"  # very random


def user_attributes():
    attrs = []
    UserAttributeTest = namedtuple(
        "UserAttributeTest",
        [
            "soap_name",
            "udm_name",
            "none_generator",
            "random_value_generator",
            "soap_value_from_udm_value",
        ],
        defaults=[none, random_string, ident],
    )
    attrs.append(UserAttributeTest("branches", "oxBranches"))
    attrs.append(UserAttributeTest("cellular_telephone1", "oxMobileBusiness"))
    attrs.append(
        UserAttributeTest(
            "cellular_telephone2",
            "mobileTelephoneNumber",
            random_value_generator=random_list_of_string,
            none_generator=empty,
            soap_value_from_udm_value=take_first,
        )
    )
    attrs.append(UserAttributeTest("city_business", "city"))
    attrs.append(UserAttributeTest("city_home", "oxCityHome"))
    attrs.append(UserAttributeTest("city_other", "oxCityOther"))
    attrs.append(UserAttributeTest("commercial_register", "oxCommercialRegister"))
    attrs.append(UserAttributeTest("company", "organisation"))
    attrs.append(UserAttributeTest("country_business", "oxCountryBusiness"))
    attrs.append(UserAttributeTest("country_home", "oxCountryHome"))
    attrs.append(UserAttributeTest("country_other", "oxCountryOther"))
    attrs.append(UserAttributeTest("department", "oxDepartment"))
    attrs.append(
        UserAttributeTest("display_name", "oxDisplayName", none_generator=no_none)
    )
    attrs.append(
        UserAttributeTest(
            "email1",
            "mailPrimaryAddress",
            random_value_generator=random_mail_address,
            none_generator=no_none,
        )
    )
    attrs.append(
        UserAttributeTest(
            "email2", "oxEmail2", random_value_generator=random_mail_address
        )
    )
    attrs.append(
        UserAttributeTest(
            "email3", "oxEmail3", random_value_generator=random_mail_address
        )
    )
    attrs.append(UserAttributeTest("fax_business", "oxFaxBusiness"))
    attrs.append(UserAttributeTest("fax_home", "oxFaxHome"))
    attrs.append(UserAttributeTest("fax_other", "oxFaxOther"))
    attrs.append(UserAttributeTest("given_name", "firstname", none_generator=no_none))
    attrs.append(
        UserAttributeTest(
            "imap_login",
            "mailPrimaryAddress",
            random_value_generator=random_mail_address,
            none_generator=no_none,
        )
    )
    attrs.append(UserAttributeTest("instant_messenger1", "oxInstantMessenger1"))
    attrs.append(UserAttributeTest("instant_messenger2", "oxInstantMessenger2"))
    attrs.append(
        UserAttributeTest(
            "language",
            "oxLanguage",
            random_value_generator=random_language,
            none_generator=no_none,
        )
    )
    attrs.append(UserAttributeTest("manager_name", "oxManagerName"))
    attrs.append(UserAttributeTest("marital_status", "oxMarialStatus"))
    attrs.append(UserAttributeTest("middle_name", "oxMiddleName"))
    attrs.append(UserAttributeTest("nickname", "oxNickName"))
    attrs.append(UserAttributeTest("note", "oxNote"))
    attrs.append(UserAttributeTest("number_of_children", "oxNumOfChildren"))
    attrs.append(UserAttributeTest("number_of_employee", "employeeNumber"))
    attrs.append(UserAttributeTest("position", "oxPosition"))
    attrs.append(UserAttributeTest("postal_code_business", "postcode"))
    attrs.append(UserAttributeTest("postal_code_home", "oxPostalCodeHome"))
    attrs.append(UserAttributeTest("postal_code_other", "oxPostalCodeOther"))
    attrs.append(
        UserAttributeTest(
            "primary_email",
            "mailPrimaryAddress",
            random_value_generator=random_mail_address,
            none_generator=no_none,
        )
    )
    attrs.append(UserAttributeTest("profession", "oxProfession"))
    attrs.append(
        UserAttributeTest(
            "room_number",
            "roomNumber",
            random_value_generator=random_list_of_string,
            none_generator=empty,
            soap_value_from_udm_value=take_first,
        )
    )
    attrs.append(UserAttributeTest("sales_volume", "oxSalesVolume"))
    attrs.append(UserAttributeTest("spouse_name", "oxSpouseName"))
    attrs.append(UserAttributeTest("state_business", "oxStateBusiness"))
    attrs.append(UserAttributeTest("state_home", "oxStateHome"))
    attrs.append(UserAttributeTest("state_other", "oxStateOther"))
    attrs.append(UserAttributeTest("street_business", "street"))
    attrs.append(UserAttributeTest("street_home", "oxStreetHome"))
    attrs.append(UserAttributeTest("street_other", "oxStreetOther"))
    attrs.append(UserAttributeTest("suffix", "oxSuffix"))
    attrs.append(UserAttributeTest("sur_name", "lastname", none_generator=no_none))
    attrs.append(UserAttributeTest("tax_id", "oxTaxId"))
    attrs.append(UserAttributeTest("telephone_assistant", "oxTelephoneAssistant"))
    attrs.append(
        UserAttributeTest(
            "telephone_business1",
            "phone",
            random_value_generator=random_list_of_string,
            none_generator=empty,
            soap_value_from_udm_value=take_first,
        )
    )
    attrs.append(
        UserAttributeTest(
            "telephone_business2",
            "phone",
            random_value_generator=random_list_of_strings,
            none_generator=empty,
            soap_value_from_udm_value=take_second,
        )
    )
    attrs.append(UserAttributeTest("telephone_car", "oxTelephoneCar"))
    attrs.append(UserAttributeTest("telephone_company", "oxTelephoneCompany"))
    attrs.append(
        UserAttributeTest(
            "telephone_home1",
            "homeTelephoneNumber",
            random_value_generator=random_list_of_string,
            none_generator=empty,
            soap_value_from_udm_value=take_first,
        )
    )
    attrs.append(
        UserAttributeTest(
            "telephone_home2",
            "homeTelephoneNumber",
            random_value_generator=random_list_of_strings,
            none_generator=empty,
            soap_value_from_udm_value=take_second,
        )
    )
    attrs.append(UserAttributeTest("telephone_ip", "oxTelephoneIp"))
    attrs.append(UserAttributeTest("telephone_other", "oxTelephoneOther"))
    attrs.append(
        UserAttributeTest(
            "telephone_pager",
            "pagerTelephoneNumber",
            random_value_generator=random_list_of_string,
            none_generator=empty,
            soap_value_from_udm_value=take_first,
        )
    )
    attrs.append(UserAttributeTest("telephone_telex", "oxTelephoneTelex"))
    attrs.append(UserAttributeTest("telephone_ttytdd", "oxTelephoneTtydd"))
    attrs.append(
        UserAttributeTest(
            "timezone",
            "oxTimeZone",
            random_value_generator=random_timezone,
            none_generator=no_none,
        )
    )
    attrs.append(UserAttributeTest("title", "title"))
    attrs.append(UserAttributeTest("url", "oxUrl"))
    attrs.append(UserAttributeTest("userfield01", "oxUserfield01"))
    attrs.append(UserAttributeTest("userfield02", "oxUserfield02"))
    attrs.append(UserAttributeTest("userfield03", "oxUserfield03"))
    attrs.append(UserAttributeTest("userfield04", "oxUserfield04"))
    attrs.append(UserAttributeTest("userfield05", "oxUserfield05"))
    attrs.append(UserAttributeTest("userfield06", "oxUserfield06"))
    attrs.append(UserAttributeTest("userfield07", "oxUserfield07"))
    attrs.append(UserAttributeTest("userfield08", "oxUserfield08"))
    attrs.append(UserAttributeTest("userfield09", "oxUserfield09"))
    attrs.append(UserAttributeTest("userfield10", "oxUserfield10"))
    attrs.append(UserAttributeTest("userfield11", "oxUserfield11"))
    attrs.append(UserAttributeTest("userfield12", "oxUserfield12"))
    attrs.append(UserAttributeTest("userfield13", "oxUserfield13"))
    attrs.append(UserAttributeTest("userfield14", "oxUserfield14"))
    attrs.append(UserAttributeTest("userfield15", "oxUserfield15"))
    attrs.append(UserAttributeTest("userfield16", "oxUserfield16"))
    attrs.append(UserAttributeTest("userfield17", "oxUserfield17"))
    attrs.append(UserAttributeTest("userfield18", "oxUserfield18"))
    attrs.append(UserAttributeTest("userfield19", "oxUserfield19"))
    attrs.append(UserAttributeTest("userfield20", "oxUserfield20"))
    return attrs


@pytest.mark.parametrize("user_test", user_attributes())
def test_modify_user_set_and_unset_string_attributes(
    new_context_id,
    new_user_name,
    udm,
    ox_host,
    domainname,
    wait_for_listener,
    user_test,
):
    """
    Changing UDM object should be reflected in OX
    """
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    wait_for_listener(dn)  # make sure we wait for the modify step below
    values = [
        user_test.random_value_generator(),
        user_test.none_generator(),
        user_test.random_value_generator(),
    ]
    for value in values:
        if value is NotImplemented:
            continue
        udm.modify(
            "users/user", dn, {user_test.udm_name: value},
        )
        wait_for_listener(dn)
        obj = find_obj(new_context_id, new_user_name, print_obj=False)
        soap_value = getattr(obj, user_test.soap_name)
        value = user_test.soap_value_from_udm_value(value)
        assert soap_value == value


def test_full_blown_user(
    new_context_id, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    create_context(udm, ox_host, new_context_id)
    attrs = {
        "city": "gesch. Stadt",
        "country": "AF",
        "departmentNumber": ["DEMOSCHOOL", "gesch. Abteilungsnummer"],
        "displayName": "Demo Student",
        "e-mail": [
            "demo_student@{}".format(domainname),
            "demo_student22@{}".format(domainname),
        ],
        "firstname": "Demo",
        "gecos": "Demo Student",
        "homePostalAddress": [
            {
                "street": "privat Straße1",
                "zipcode": "privat Postleitzahl1",
                "city": "privat Stadt1",
            },
            {
                "street": "privat Straße2",
                "zipcode": "privat Postleitzahl2",
                "city": "privat Stadt2",
            },
        ],
        "homeTelephoneNumber": ["030 / 123456", "789"],
        "homedrive": "I:",
        "lastname": "Student",
        "mailForwardCopyToSelf": "0",
        "mailPrimaryAddress": "demo_student@{}".format(domainname),
        "mobileTelephoneNumber": ["123-345", "00 987"],
        "oxAccess": "premium",
        "oxAnniversary": "11.11.1911",
        "oxBirthday": "12.12.1912",
        "oxBranches": "Branchen",
        "oxCityHome": "Stadt privat",
        "oxCityOther": "Stadt weitere",
        "oxCommercialRegister": "Handelsregister",
        "oxCountryBusiness": "Land Firma",
        "oxCountryHome": "Land privat",
        "oxCountryOther": "Land weiteres",
        "oxDepartment": "Abteilung",
        "oxDisplayName": "Demo Student",
        "oxEmail2": "privat@gmx.de",
        "oxEmail3": "weitere@gmx.de",
        "oxFaxBusiness": "Fax geschäftlich",
        "oxFaxHome": "Fax privat",
        "oxFaxOther": "Fax weiteres",
        "oxInstantMessenger1": "IM Firma",
        "oxInstantMessenger2": "IM privat",
        "oxLanguage": "de_DE",
        "oxManagerName": "Manager",
        "oxMarialStatus": "Familienstand",
        "oxMiddleName": "gesch. Zweiter Vorname",
        "oxMobileBusiness": "Mobiltelefon geschäftlich",
        "oxNickName": "gesch. Spitzname",
        "oxNote": "Bemerkungengesch. ",
        "oxNumOfChildren": "Kinder",
        "oxPosition": "Position",
        "oxPostalCodeHome": "PLZ privat",
        "oxPostalCodeOther": "Postleitzahl weitere",
        "oxProfession": "Beruf",
        "oxSalesVolume": "Umsatz",
        "oxSpouseName": "Name des Ehegatten",
        "oxStateBusiness": "Bundesland Firma",
        "oxStateHome": "Bundesland privat",
        "oxStateOther": "Bundesland weiteres",
        "oxStreetHome": "Straße privat",
        "oxStreetOther": "Straße weitere",
        "oxSuffix": "gesch. Namenssuffix",
        "oxTaxId": "Steuernummer",
        "oxTelephoneAssistant": "Assistent",
        "oxTelephoneCar": "Autotelefon",
        "oxTelephoneCompany": "Telefon Zentrale",
        "oxTelephoneIp": "VoIP",
        "oxTelephoneOther": "Telefon weiteres",
        "oxTelephoneTelex": "Telex",
        "oxTelephoneTtydd": "Texttelefon",
        "oxTimeZone": "Europe/Berlin",
        "oxUrl": "URL",
        "oxUserfield01": "Optional 1",
        "oxUserfield02": "Optional 2",
        "oxUserfield03": "Optional 3",
        "oxUserfield04": "Optional 4",
        "oxUserfield05": "Optional 5",
        "oxUserfield06": "Optional 6",
        "oxUserfield07": "Optional 7",
        "oxUserfield08": "Optional 8",
        "oxUserfield09": "Optional 9",
        "oxUserfield10": "Optional 10",
        "oxUserfield11": "Optional 11",
        "oxUserfield12": "Optional 12",
        "oxUserfield13": "Optional 13",
        "oxUserfield14": "Optional 14",
        "oxUserfield15": "Optional 15",
        "oxUserfield16": "Optional 16",
        "oxUserfield17": "Optional 17",
        "oxUserfield18": "Optional 18",
        "oxUserfield19": "Optional 19",
        "oxUserfield20": "Optional 20",
        "pagerTelephoneNumber": ["112", "456-789"],
        "phone": ["0421 / 123456789", "0800 1234"],
        "postcode": "gesch. Postleitzahl",
        "roomNumber": ["120", "110"],
        "shell": "/bin/bash",
        "street": "gesch. Straße",
    }
    dn = create_obj(udm, new_user_name, domainname, new_context_id, attrs=attrs)
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.room_number == "120"
    assert obj.telephone_pager == "112"


def test_modify_user_without_ox_obj(
    new_context_id, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    """
    Changing UDM object without a OX pendant should just create it
    """
    new_mail_address = "{}2@{}".format(new_user_name, domainname)
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    wait_for_listener(dn)  # make sure we wait for the modify step below
    delete_obj(new_context_id, new_user_name)
    udm.modify(
        "users/user",
        dn,
        {
            "lastname": "Newman",
            "mailPrimaryAddress": new_mail_address,
            "oxCommercialRegister": "A register",
        },
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.email1 == new_mail_address
    assert obj.commercial_register == "A register"
    assert obj.sur_name == "Newman"


def test_modify_mailserver(
    default_imap_server,
    new_context_id,
    new_user_name,
    udm,
    ox_host,
    domainname,
    wait_for_listener,
):
    udm.create(
        "computers/memberserver",
        "cn=memberserver,cn=computers",
        {"name": "test-member", "password": "univention", "service": ["IMAP"]},
    )
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    wait_for_listener(dn)  # make sure we wait for the modify step below
    obj = find_obj(new_context_id, new_user_name)
    assert obj.imap_server_string == default_imap_server
    mail_home_server = "test-member.{}".format(domainname)
    udm.modify(
        "users/user", dn, {"mailHomeServer": mail_home_server},
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    # would fail if default_imap_server has a different port...
    assert obj.imap_server_string == "imap://" + mail_home_server + ":143"


def test_remove_user(
    new_context_id, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    """
    Removing a user in UDM should remove the user in OX
    """
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    udm.remove("users/user", dn)
    wait_for_listener(dn)
    find_obj(new_context_id, new_user_name, assert_empty=True)


def test_enable_and_disable_user(
    new_context_id, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    """
    Add a new UDM user (not yet active in OX)
    Setting isOxUser = OK should create the user
    Setting isOxUser = Not should delete the user
    """
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id, enabled=False)
    wait_for_listener(dn)  # make sure we wait for the modify step below
    udm.modify("users/user", dn, {"isOxUser": True})
    wait_for_listener(dn)
    find_obj(new_context_id, new_user_name)
    udm.modify("users/user", dn, {"isOxUser": False})
    wait_for_listener(dn)
    find_obj(new_context_id, new_user_name, assert_empty=True)


def test_change_context(
    new_context_id_generator, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    """
    Special case: Change context:
    * Delete user in old context
    * Create "same" user in new context
    Test twice, just to be sure
    """
    old_context_id = new_context_id_generator()
    create_context(udm, ox_host, old_context_id)
    dn = create_obj(udm, new_user_name, domainname, old_context_id)
    wait_for_listener(dn)
    find_obj(old_context_id, new_user_name)
    new_context_id = new_context_id_generator()
    create_context(udm, ox_host, new_context_id)
    udm.modify("users/user", dn, {"oxContext": new_context_id})
    wait_for_listener(dn)
    find_obj(old_context_id, new_user_name, assert_empty=True)
    find_obj(new_context_id, new_user_name)
    new_context_id2 = new_context_id_generator()
    create_context(udm, ox_host, new_context_id2)
    udm.modify("users/user", dn, {"oxContext": new_context_id2})
    wait_for_listener(dn)
    find_obj(old_context_id, new_user_name, assert_empty=True)
    find_obj(new_context_id, new_user_name, assert_empty=True)
    find_obj(new_context_id2, new_user_name)


def test_alias(
    new_context_id, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    """
    Changing mailPrimaryAddress and email1 leads to appropriate aliases
    """
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    mail_addresses = [
        "test1-{}@{}".format(new_user_name, domainname),
        "test2-{}@{}".format(new_user_name, domainname),
        "test3-{}@{}".format(new_user_name, domainname),
        "test4-{}@{}".format(new_user_name, domainname),
    ]
    wait_for_listener(dn)  # make sure we wait for the modify step below
    udm.modify(
        "users/user",
        dn,
        {
            "mailPrimaryAddress": mail_addresses[0],
            "mailAlternativeAddress": mail_addresses[1:],
        },
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert sorted(obj.aliases) == sorted(mail_addresses)
    mail_addresses = [
        "test5-{}@{}".format(new_user_name, domainname),
    ]
    udm.modify(
        "users/user",
        dn,
        {
            "mailPrimaryAddress": mail_addresses[0],
            "mailAlternativeAddress": mail_addresses[1:],
        },
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert sorted(obj.aliases) == sorted(mail_addresses)
    mail_addresses = [
        "test6-{}@{}".format(new_user_name, domainname),
        "test7-{}@{}".format(new_user_name, domainname),
    ]
    udm.modify(
        "users/user",
        dn,
        {
            "mailPrimaryAddress": mail_addresses[0],
            "mailAlternativeAddress": mail_addresses[1:],
        },
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert sorted(obj.aliases) == sorted(mail_addresses)
