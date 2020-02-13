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


def find_obj(context_id, name, assert_empty=False):
    User = get_ox_integration_class("SOAP", "User")
    objs = User.list(context_id, pattern=name)
    if assert_empty:
        assert len(objs) == 0
    else:
        assert len(objs) == 1
        obj = objs[0]
        print("Found", obj)
        return obj


def delete_obj(context_id, name):
    obj = find_obj(context_id, name)
    print("Removing", obj.id, "directly in OX")
    obj.remove()
    find_obj(context_id, name, assert_empty=True)


def test_ignore_user(default_ox_context, new_user_name, udm, domainname):
    """
    isOxUser = Not should not create a user
    """
    create_obj(udm, new_user_name, domainname, None, enabled=False)
    find_obj(default_ox_context, new_user_name, assert_empty=True)


def test_add_user_in_default_context(
    default_ox_context, new_user_name, udm, domainname
):
    """
    Creating a user without a context should add it in the default context
    """
    create_obj(udm, new_user_name, domainname, None)
    obj = find_obj(default_ox_context, new_user_name)
    assert obj.name == new_user_name
    assert obj.email1 == "{}@{}".format(new_user_name, domainname)


def test_rename_user(default_ox_context, new_user_name, udm, domainname):
    """
    Renaming a user should keep its ID
    """
    dn = create_obj(udm, new_user_name, domainname, None)
    obj = find_obj(default_ox_context, new_user_name)
    old_id = obj.id
    udm.modify(
        "users/user", dn, {"username": "new" + new_user_name},
    )
    obj = find_obj(default_ox_context, "new" + new_user_name)
    assert old_id == obj.id


def test_add_user(new_context_id, new_user_name, udm, ox_host, domainname):
    """
    isOxUser = OK should create a user
    """
    create_context(udm, ox_host, new_context_id)
    create_obj(udm, new_user_name, domainname, new_context_id)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.name == new_user_name
    assert obj.email1 == "{}@{}".format(new_user_name, domainname)


def test_modify_user(new_context_id, new_user_name, udm, ox_host, domainname):
    """
    Changing UDM object should be reflected in OX
    """
    new_mail_address = "{}2@{}".format(new_user_name, domainname)
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    udm.modify(
        "users/user",
        dn,
        {
            "lastname": "Newman",
            "mailPrimaryAddress": new_mail_address,
            "oxCommercialRegister": "A register",
        },
    )
    obj = find_obj(new_context_id, new_user_name)
    assert obj.email1 == new_mail_address
    assert obj.commercial_register == "A register"
    assert obj.sur_name == "Newman"


def test_full_blown_user(new_context_id, new_user_name, udm, ox_host, domainname):
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
    create_obj(udm, new_user_name, domainname, new_context_id, attrs=attrs)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.room_number == "120"
    assert obj.telephone_pager == "112"


def test_modify_user_without_ox_obj(
    new_context_id, new_user_name, udm, ox_host, domainname
):
    """
    Changing UDM object without a OX pendant should just create it
    """
    new_mail_address = "{}2@{}".format(new_user_name, domainname)
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
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
    obj = find_obj(new_context_id, new_user_name)
    assert obj.email1 == new_mail_address
    assert obj.commercial_register == "A register"
    assert obj.sur_name == "Newman"


def test_modify_mailserver(
    default_imap_server, new_context_id, new_user_name, udm, ox_host, domainname
):
    udm.create(
        "computers/memberserver",
        "cn=memberserver,cn=computers",
        {"name": "test-member", "password": "univention", "service": ["IMAP"]},
        wait_for_listener=False,
    )
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.imap_server_string == default_imap_server
    mail_home_server = "test-member.{}".format(domainname)
    udm.modify(
        "users/user", dn, {"mailHomeServer": mail_home_server},
    )
    obj = find_obj(new_context_id, new_user_name)
    # would fail if default_imap_server has a different port...
    assert obj.imap_server_string == "imap://" + mail_home_server + ":143"


def test_remove_user(new_context_id, new_user_name, udm, ox_host, domainname):
    """
    Removing a user in UDM should remove the user in OX
    """
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    udm.remove("users/user", dn)
    find_obj(new_context_id, new_user_name, assert_empty=True)


def test_enable_and_disable_user(
    new_context_id, new_user_name, udm, ox_host, domainname
):
    """
    Add a new UDM user (not yet active in OX)
    Setting isOxUser = OK should create the user
    Setting isOxUser = Not should delete the user
    """
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id, enabled=False)
    udm.modify("users/user", dn, {"isOxUser": True})
    find_obj(new_context_id, new_user_name)
    udm.modify("users/user", dn, {"isOxUser": False})
    find_obj(new_context_id, new_user_name, assert_empty=True)


def test_alias(new_context_id, new_user_name, udm, ox_host, domainname):
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
    udm.modify(
        "users/user",
        dn,
        {
            "mailPrimaryAddress": mail_addresses[0],
            "mailAlternativeAddress": mail_addresses[1:],
        },
    )
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
    obj = find_obj(new_context_id, new_user_name)
    assert sorted(obj.aliases) == sorted(mail_addresses)
