import random
import string
import uuid
import typing

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


class UserAttributeTest(typing.NamedTuple):
    soap_name: str
    udm_name: str
    none_generator: str = none
    random_value_generator: str = random_string
    soap_value_from_udm_value: str = ident


def user_attributes():
    attrs = []
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
    new_context_id,
    new_user_name,
    new_user_name_generator,
    udm,
    ox_host,
    domainname,
    wait_for_listener,
):
    create_context(udm, ox_host, new_context_id)
    attrs = {
        "city": new_user_name_generator(),
        "country": random.choice(("AF", "CZ", "DE", "FR", "US")),
        "departmentNumber": [new_user_name_generator(), new_user_name_generator()],
        "displayName": new_user_name_generator(),
        "e-mail": [
            "{}@{}".format(new_user_name_generator(), domainname),
            "{}@{}".format(new_user_name_generator(), domainname),
        ],
        "firstname": new_user_name_generator(),
        "gecos": new_user_name_generator(),
        "homePostalAddress": [
            {
                "street": new_user_name_generator(),
                "zipcode": new_user_name_generator(),
                "city": new_user_name_generator(),
            },
            {
                "street": new_user_name_generator(),
                "zipcode": new_user_name_generator(),
                "city": new_user_name_generator(),
            },
        ],
        "homeTelephoneNumber": [new_user_name_generator(), new_user_name_generator()],
        "homedrive": "{}:".format(random.choice(string.uppercase)),
        "lastname": new_user_name_generator(),
        "mailForwardCopyToSelf": "0",
        "mailPrimaryAddress": "{}@{}".format(new_user_name_generator(), domainname),
        "mobileTelephoneNumber": [new_user_name_generator(), new_user_name_generator()],
        "oxAccess": "premium",
        "oxAnniversary": "{}.{}.19{}".format(
            random.randint(1, 27), random.randint(1, 12), random.randint(11, 99)
        ),
        "oxBirthday": "{}.{}.19{}".format(
            random.randint(1, 27), random.randint(1, 12), random.randint(11, 99)
        ),
        "oxBranches": new_user_name_generator(),
        "oxCityHome": new_user_name_generator(),
        "oxCityOther": new_user_name_generator(),
        "oxCommercialRegister": new_user_name_generator(),
        "oxCountryBusiness": new_user_name_generator(),
        "oxCountryHome": new_user_name_generator(),
        "oxCountryOther": new_user_name_generator(),
        "oxDepartment": new_user_name_generator(),
        "oxDisplayName": new_user_name_generator(),
        "oxEmail2": "{}@gmx.de".format(new_user_name_generator()),
        "oxEmail3": "{}@gmx.de".format(new_user_name_generator()),
        "oxFaxBusiness": new_user_name_generator(),
        "oxFaxHome": new_user_name_generator(),
        "oxFaxOther": new_user_name_generator(),
        "oxInstantMessenger1": new_user_name_generator(),
        "oxInstantMessenger2": new_user_name_generator(),
        "oxLanguage": random.choice(("de_DE", "fr_FR", "en_US")),
        "oxManagerName": new_user_name_generator(),
        "oxMarialStatus": new_user_name_generator(),
        "oxMiddleName": new_user_name_generator(),
        "oxMobileBusiness": new_user_name_generator(),
        "oxNickName": new_user_name_generator(),
        "oxNote": new_user_name_generator(),
        "oxNumOfChildren": new_user_name_generator(),
        "oxPosition": new_user_name_generator(),
        "oxPostalCodeHome": new_user_name_generator(),
        "oxPostalCodeOther": new_user_name_generator(),
        "oxProfession": new_user_name_generator(),
        "oxSalesVolume": new_user_name_generator(),
        "oxSpouseName": new_user_name_generator(),
        "oxStateBusiness": new_user_name_generator(),
        "oxStateHome": new_user_name_generator(),
        "oxStateOther": new_user_name_generator(),
        "oxStreetHome": new_user_name_generator(),
        "oxStreetOther": new_user_name_generator(),
        "oxSuffix": new_user_name_generator(),
        "oxTaxId": new_user_name_generator(),
        "oxTelephoneAssistant": new_user_name_generator(),
        "oxTelephoneCar": new_user_name_generator(),
        "oxTelephoneCompany": new_user_name_generator(),
        "oxTelephoneIp": new_user_name_generator(),
        "oxTelephoneOther": new_user_name_generator(),
        "oxTelephoneTelex": new_user_name_generator(),
        "oxTelephoneTtydd": new_user_name_generator(),
        "oxTimeZone": "Europe/Berlin",
        "oxUrl": "https://{}.{}/{}/".format(
            new_user_name_generator(),
            new_user_name_generator(),
            new_user_name_generator(),
        ),
        "oxUserfield01": new_user_name_generator(),
        "oxUserfield02": new_user_name_generator(),
        "oxUserfield03": new_user_name_generator(),
        "oxUserfield04": new_user_name_generator(),
        "oxUserfield05": new_user_name_generator(),
        "oxUserfield06": new_user_name_generator(),
        "oxUserfield07": new_user_name_generator(),
        "oxUserfield08": new_user_name_generator(),
        "oxUserfield09": new_user_name_generator(),
        "oxUserfield10": new_user_name_generator(),
        "oxUserfield11": new_user_name_generator(),
        "oxUserfield12": new_user_name_generator(),
        "oxUserfield13": new_user_name_generator(),
        "oxUserfield14": new_user_name_generator(),
        "oxUserfield15": new_user_name_generator(),
        "oxUserfield16": new_user_name_generator(),
        "oxUserfield17": new_user_name_generator(),
        "oxUserfield18": new_user_name_generator(),
        "oxUserfield19": new_user_name_generator(),
        "oxUserfield20": new_user_name_generator(),
        "pagerTelephoneNumber": [new_user_name_generator(), new_user_name_generator()],
        "phone": [new_user_name_generator(), new_user_name_generator()],
        "postcode": new_user_name_generator(),
        "roomNumber": [new_user_name_generator(), new_user_name_generator()],
        "shell": "/bin/{}".format(new_user_name_generator()),
        "street": new_user_name_generator(),
    }
    dn = create_obj(udm, new_user_name, domainname, new_context_id, attrs=attrs)
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    for k, v in attrs.items():
        obj_item = getattr(obj, k)
        error_msg = "Expected for k={!r} v={!r} but found {!r}.".format(k, v, obj_item)
        if isinstance(v, list):
            assert set(v) == set(obj_item), error_msg
        else:
            assert v == obj_item, error_msg


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
