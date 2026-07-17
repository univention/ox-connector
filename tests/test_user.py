# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import os
import random
import typing
import uuid

import pytest

from urllib.parse import urlparse
from univention.ox.soap.backend_base import get_ox_integration_class
from univention.ox.provisioning.users import _get_name

T = typing.TypeVar("T")


def get_identifier(udm_object):
    return _get_name(udm_object.properties)


def delete_obj(find_ox_object, context_id, udm_object) -> None:
    obj = find_ox_object(context_id, "User", get_identifier(udm_object))
    print("Removing", obj.id, "directly in OX")
    obj.remove()
    find_ox_object(
        context_id,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )


def test_ignore_user(
    find_ox_object,
    create_ox_user,
    default_ox_context,
    new_user_name,
    wait_for_listener,
):
    """
    isOxUser = False (Not) should not create a user
    """
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=None,
        enabled=False,
        wait=False,
    )
    wait_for_listener(udm_object.dn)
    find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )


def test_add_user_in_default_context(
    find_ox_object,
    create_ox_user,
    default_ox_context,
    new_user_name,
    domainname,
    wait_for_listener,
):
    """
    Creating a user without a context should add it in the default context
    """
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=default_ox_context,
        wait=False,
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
    )
    assert obj.name == get_identifier(udm_object)
    assert obj.email1 == "{}@{}".format(new_user_name, domainname)


def test_rename_user(
    find_ox_object,
    create_ox_user,
    default_ox_context,
    new_user_name,
    udm,
    wait_for_listener,
):
    """
    Renaming a user should keep its ID
    """
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=default_ox_context,
        wait=False,
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
    )
    old_id = obj.id
    udm_object = udm.modify(
        "users/user",
        udm_object.dn,
        {"username": "new" + new_user_name},
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
    )
    assert old_id == obj.id


def test_add_user(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    new_user_name,
    domainname,
    wait_for_listener,
):
    """
    isOxUser = True (OK) should create a user
    """
    new_context_id = create_ox_context()
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=new_context_id,
        wait=False,
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    assert obj.name == get_identifier(udm_object)
    assert obj.email1 == "{}@{}".format(new_user_name, domainname)


def test_modify_user(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    new_user_name,
    domainname,
    udm,
    wait_for_listener,
):
    """
    Changing UDM object should be reflected in OX
    """
    new_mail_address = "{}2@{}".format(new_user_name, domainname)
    new_context_id = create_ox_context()
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=new_context_id,
        wait=False,
    )
    wait_for_listener(
        udm_object.dn,
    )  # make sure we wait for the modify step below
    udm.modify(
        "users/user",
        udm_object.dn,
        {
            "lastname": "Newman",
            "mailPrimaryAddress": new_mail_address,
            "oxCommercialRegister": "A register",
        },
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    assert obj.email1 == new_mail_address
    assert obj.commercial_register == "A register"
    assert obj.sur_name == "Newman"


@pytest.mark.skipif(
    os.getenv("OX_USER_IDENTIFIER") != "username",
    reason="""
OX_USER_IDENTIFIER != name, so a user account can actually be named like the technical admin account.
Creating the user with the same name will fail because, old object is not found because of different
identifier and a user with the same primary mail already exists""",
)
def test_modify_context_admin(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    domainname,
    udm,
    wait_for_listener,
):
    """
    Adding/Modifying a user with the same name as an OX context admin
    is to be ignored as e.g. writing the password hash of the LDAP
    user into OX will break the authentication from the ox-connector side
    """
    new_context_id = create_ox_context()
    username = "oxadmin-context{}".format(new_context_id)
    udm_object = create_ox_user(
        name=username,
        context_id=new_context_id,
        wait=False,
    )
    wait_for_listener(udm_object.dn)

    surname = "new-lastname"
    udm_object = udm.modify(
        "users/user",
        udm_object.dn,
        {
            "lastname": surname,
        },
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    assert obj.sur_name != surname


def no_none():
    return NotImplemented


def none() -> None:
    return None


def empty() -> typing.List[typing.Any]:
    return []


def random_string() -> str:
    return str(uuid.uuid4())


def ident(x: T) -> T:
    return x


def take_first(x: typing.List[T]) -> typing.Optional[T]:
    if len(x) > 0:
        return x[0]


def take_second(x: typing.List[T]) -> typing.Optional[T]:
    if len(x) > 1:
        return x[1]


def random_mail_address() -> str:
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
    none_generator: typing.Callable[[], None] = none
    random_value_generator: typing.Callable[[], str] = random_string
    soap_value_from_udm_value: typing.Callable[[T], T] = ident


user_attributes: typing.List[UserAttributeTest] = [
    UserAttributeTest("branches", "oxBranches"),
    UserAttributeTest("cellular_telephone1", "oxMobileBusiness"),
    UserAttributeTest(
        "cellular_telephone2",
        "mobileTelephoneNumber",
        random_value_generator=random_list_of_string,
        none_generator=empty,
        soap_value_from_udm_value=take_first,
    ),
    UserAttributeTest("city_business", "city"),
    UserAttributeTest("city_home", "oxCityHome"),
    UserAttributeTest("city_other", "oxCityOther"),
    UserAttributeTest("commercial_register", "oxCommercialRegister"),
    UserAttributeTest("company", "organisation"),
    UserAttributeTest("country_business", "oxCountryBusiness"),
    UserAttributeTest("country_home", "oxCountryHome"),
    UserAttributeTest("country_other", "oxCountryOther"),
    UserAttributeTest("department", "oxDepartment"),
    UserAttributeTest("display_name", "oxDisplayName", none_generator=no_none),
    UserAttributeTest(
        "email1",
        "mailPrimaryAddress",
        random_value_generator=random_mail_address,
        none_generator=no_none,
    ),
    UserAttributeTest(
        "email2",
        "oxEmail2",
        random_value_generator=random_mail_address,
    ),
    UserAttributeTest(
        "email3",
        "oxEmail3",
        random_value_generator=random_mail_address,
    ),
    UserAttributeTest("fax_business", "oxFaxBusiness"),
    UserAttributeTest("fax_home", "oxFaxHome"),
    UserAttributeTest("fax_other", "oxFaxOther"),
    UserAttributeTest("given_name", "firstname", none_generator=no_none),
    UserAttributeTest(
        "imap_login",
        "mailPrimaryAddress",
        random_value_generator=random_mail_address,
        none_generator=no_none,
    ),
    UserAttributeTest("instant_messenger1", "oxInstantMessenger1"),
    UserAttributeTest("instant_messenger2", "oxInstantMessenger2"),
    UserAttributeTest("manager_name", "oxManagerName"),
    UserAttributeTest("marital_status", "oxMarialStatus"),
    UserAttributeTest("middle_name", "oxMiddleName"),
    UserAttributeTest("nickname", "oxNickName"),
    UserAttributeTest("note", "oxNote"),
    UserAttributeTest("number_of_children", "oxNumOfChildren"),
    UserAttributeTest("number_of_employee", "employeeNumber"),
    UserAttributeTest("position", "oxPosition"),
    UserAttributeTest("postal_code_business", "postcode"),
    UserAttributeTest("postal_code_home", "oxPostalCodeHome"),
    UserAttributeTest("postal_code_other", "oxPostalCodeOther"),
    UserAttributeTest(
        "primary_email",
        "mailPrimaryAddress",
        random_value_generator=random_mail_address,
        none_generator=no_none,
    ),
    UserAttributeTest("profession", "oxProfession"),
    UserAttributeTest(
        "room_number",
        "roomNumber",
        random_value_generator=random_list_of_string,
        none_generator=empty,
        soap_value_from_udm_value=take_first,
    ),
    UserAttributeTest("sales_volume", "oxSalesVolume"),
    UserAttributeTest("spouse_name", "oxSpouseName"),
    UserAttributeTest("state_business", "oxStateBusiness"),
    UserAttributeTest("state_home", "oxStateHome"),
    UserAttributeTest("state_other", "oxStateOther"),
    UserAttributeTest("street_business", "street"),
    UserAttributeTest("street_home", "oxStreetHome"),
    UserAttributeTest("street_other", "oxStreetOther"),
    UserAttributeTest("suffix", "oxSuffix"),
    UserAttributeTest("sur_name", "lastname", none_generator=no_none),
    UserAttributeTest("tax_id", "oxTaxId"),
    UserAttributeTest("telephone_assistant", "oxTelephoneAssistant"),
    UserAttributeTest(
        "telephone_business1",
        "phone",
        random_value_generator=random_list_of_string,
        none_generator=empty,
        soap_value_from_udm_value=take_first,
    ),
    UserAttributeTest(
        "telephone_business2",
        "phone",
        random_value_generator=random_list_of_strings,
        none_generator=empty,
        soap_value_from_udm_value=take_second,
    ),
    UserAttributeTest("telephone_car", "oxTelephoneCar"),
    UserAttributeTest("telephone_company", "oxTelephoneCompany"),
    UserAttributeTest(
        "telephone_home1",
        "homeTelephoneNumber",
        random_value_generator=random_list_of_string,
        none_generator=empty,
        soap_value_from_udm_value=take_first,
    ),
    UserAttributeTest(
        "telephone_home2",
        "homeTelephoneNumber",
        random_value_generator=random_list_of_strings,
        none_generator=empty,
        soap_value_from_udm_value=take_second,
    ),
    UserAttributeTest("telephone_ip", "oxTelephoneIp"),
    UserAttributeTest("telephone_other", "oxTelephoneOther"),
    UserAttributeTest(
        "telephone_pager",
        "pagerTelephoneNumber",
        random_value_generator=random_list_of_string,
        none_generator=empty,
        soap_value_from_udm_value=take_first,
    ),
    UserAttributeTest("telephone_telex", "oxTelephoneTelex"),
    UserAttributeTest("telephone_ttytdd", "oxTelephoneTtydd"),
    UserAttributeTest("title", "title"),
    UserAttributeTest("url", "oxUrl"),
    UserAttributeTest("userfield01", "oxUserfield01"),
    UserAttributeTest("userfield02", "oxUserfield02"),
    UserAttributeTest("userfield03", "oxUserfield03"),
    UserAttributeTest("userfield04", "oxUserfield04"),
    UserAttributeTest("userfield05", "oxUserfield05"),
    UserAttributeTest("userfield06", "oxUserfield06"),
    UserAttributeTest("userfield07", "oxUserfield07"),
    UserAttributeTest("userfield08", "oxUserfield08"),
    UserAttributeTest("userfield09", "oxUserfield09"),
    UserAttributeTest("userfield10", "oxUserfield10"),
    UserAttributeTest("userfield11", "oxUserfield11"),
    UserAttributeTest("userfield12", "oxUserfield12"),
    UserAttributeTest("userfield13", "oxUserfield13"),
    UserAttributeTest("userfield14", "oxUserfield14"),
    UserAttributeTest("userfield15", "oxUserfield15"),
    UserAttributeTest("userfield16", "oxUserfield16"),
    UserAttributeTest("userfield17", "oxUserfield17"),
    UserAttributeTest("userfield18", "oxUserfield18"),
    UserAttributeTest("userfield19", "oxUserfield19"),
    UserAttributeTest("userfield20", "oxUserfield20"),
]
random.shuffle(user_attributes)


udm_prop2soap_prop: typing.Dict[str, str] = dict(
    (user_attribute.udm_name, user_attribute.soap_name)
    for user_attribute in user_attributes
)


def attr_id(value: UserAttributeTest, index=[]) -> str:
    try:
        index[0] += 1
    except IndexError:
        index.append(1)
    return f"{value.udm_name} ({index[0]}/{len(user_attributes)})"


@pytest.mark.parametrize("user_test", user_attributes, ids=attr_id)
def test_modify_user_set_and_unset_string_attributes(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    new_user_name,
    domainname,
    udm,
    wait_for_listener,
    user_test,
):
    """
    Changing UDM object should be reflected in OX
    """
    new_context_id = create_ox_context()
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=new_context_id,
        wait=False,
    )
    wait_for_listener(
        udm_object.dn,
    )  # make sure we wait for the modify step below
    values = [
        user_test.random_value_generator(),
        user_test.none_generator(),
        user_test.random_value_generator(),
    ]
    for value in values:
        if value is NotImplemented:
            continue
        udm.modify(
            "users/user",
            udm_object.dn,
            {user_test.udm_name: value},
        )
        wait_for_listener(udm_object.dn)
        obj = find_ox_object(
            new_context_id,
            "User",
            get_identifier(udm_object),
        )
        soap_value = getattr(obj, user_test.soap_name)
        value = user_test.soap_value_from_udm_value(value)
        assert soap_value == value


def test_full_blown_user(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    new_user_name,
    new_user_name_generator,
    domainname,
    wait_for_listener,
):
    new_context_id = create_ox_context()
    attrs = {
        "city": new_user_name_generator(),
        "firstname": new_user_name_generator(),
        "lastname": new_user_name_generator(),
        "homeTelephoneNumber": [
            new_user_name_generator(),
            new_user_name_generator(),
        ],
        "mailPrimaryAddress": "{}@{}".format(
            new_user_name_generator(),
            domainname,
        ),
        "oxAccess": "premium",
        # TODO:
        # "oxAnniversary": "{}.{}.19{}".format(
        #     random.randint(1, 27), random.randint(1, 12), random.randint(11, 99)
        # ),
        # "oxBirthday": "{}.{}.19{}".format(
        #     random.randint(1, 27), random.randint(1, 12), random.randint(11, 99)
        # ),
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
        "pagerTelephoneNumber": [new_user_name_generator()],
        "phone": [new_user_name_generator(), new_user_name_generator()],
        "postcode": new_user_name_generator(),
        "roomNumber": [new_user_name_generator()],
        "street": new_user_name_generator(),
    }
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=new_context_id,
        wait=False,
        further_udm_attrs=attrs,
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    for k, v in attrs.items():
        if k == "oxAccess":
            continue
        elif k in ("pagerTelephoneNumber", "roomNumber"):
            v = v[0]  # OX supports only one value, not a list
        elif k in ("phone", "homeTelephoneNumber"):
            continue  # handle separately
        soap_prop = udm_prop2soap_prop[k]
        obj_item = getattr(obj, soap_prop)
        error_msg = f"Expected for k={k!r}({soap_prop!r}) v={v!r} but found {obj_item!r}."
        if isinstance(v, list):
            assert set(v) == set(obj_item), error_msg
        else:
            assert v == obj_item, error_msg
    # handle phone and homeTelephoneNumber
    #     homeTelephoneNumber -> telephone_home1, telephone_home2
    #     phone               -> telephone_business1, telephone_business2
    for k, soap_props in (
        ("homeTelephoneNumber", ("telephone_home1", "telephone_home2")),
        ("phone", ("telephone_business1", "telephone_business2")),
    ):
        v = set(attrs[k])
        obj_items = {getattr(obj, soap_prop) for soap_prop in soap_props}
        error_msg = f"Expected for k={k!r}({soap_props!r}) v={v!r} but found {obj_items!r}."
        assert v == obj_items, error_msg


@pytest.mark.skip("Fails since our cache implementation")
def test_modify_user_without_ox_obj(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    new_user_name,
    domainname,
    udm,
    wait_for_listener,
):
    """
    Changing UDM object without a OX pendant should just create it
    """
    new_mail_address = "{}2@{}".format(new_user_name, domainname)
    new_context_id = create_ox_context()
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=new_context_id,
        wait=False,
    )
    wait_for_listener(
        udm_object.dn,
    )  # make sure we wait for the modify step below
    delete_obj(find_ox_object, new_context_id, udm_object)
    udm.modify(
        "users/user",
        udm_object.dn,
        {
            "lastname": "Newman",
            "mailPrimaryAddress": new_mail_address,
            "oxCommercialRegister": "A register",
        },
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    assert obj.email1 == new_mail_address
    assert obj.commercial_register == "A register"
    assert obj.sur_name == "Newman"


def test_modify_mailserver(
    find_ox_object,
    default_imap_server,
    create_ox_context,
    create_ox_user,
    new_user_name,
    domainname,
    udm,
    wait_for_listener,
):
    udm.create(
        "computers/memberserver",
        "cn=memberserver,cn=computers",
        {"name": "test-member", "password": "univention", "service": ["IMAP"]},
    )
    new_context_id = create_ox_context()
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=new_context_id,
        wait=False,
    )
    wait_for_listener(
        udm_object.dn,
    )  # make sure we wait for the modify step below
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    assert obj.imap_server_string == default_imap_server
    mail_home_server = "test-member.{}".format(domainname)
    udm.modify(
        "users/user",
        udm_object.dn,
        {"mailHomeServer": mail_home_server},
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    url = urlparse(default_imap_server)
    assert (
        obj.imap_server_string
        == f"{url.scheme}://{mail_home_server}:{url.port}"
    )


def test_remove_user(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    new_user_name,
    udm,
    wait_for_listener,
):
    """
    Removing a user in UDM should remove the user in OX
    """
    new_context_id = create_ox_context()
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=new_context_id,
        wait=False,
    )
    wait_for_listener(udm_object.dn)
    udm.remove("users/user", udm_object.dn)
    wait_for_listener(udm_object.dn)
    find_ox_object(
        new_context_id,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )


def test_enable_and_disable_user(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    new_user_name,
    udm,
    wait_for_listener,
):
    """
    Add a new UDM user (not yet active in OX)
    Setting isOxUser = True (OK) should create the user
    Setting isOxUser = False (Not) should delete the user
    """
    new_context_id = create_ox_context()
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=None,
        enabled=False,
        wait=False,
    )
    wait_for_listener(
        udm_object.dn,
    )  # make sure we wait for the modify step below
    # BUG: some hook seems to remove the ox specific attributes when enabling the user
    # BUG: so we have to do it in two steps: Bug #50469
    udm.modify("users/user", udm_object.dn, {"isOxUser": True})
    wait_for_listener(udm_object.dn)
    udm.modify(
        "users/user",
        udm_object.dn,
        {"oxContext": new_context_id, "oxDisplayName": new_user_name},
    )
    wait_for_listener(udm_object.dn)
    find_ox_object(new_context_id, "User", get_identifier(udm_object))
    udm.modify("users/user", udm_object.dn, {"isOxUser": False})
    wait_for_listener(udm_object.dn)
    find_ox_object(
        new_context_id,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )


def test_change_context(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    new_user_name,
    udm,
    wait_for_listener,
):
    """
    Special case: Change context:
    * Delete user in old context
    * Create "same" user in new context
    Test twice, just to be sure
    """
    old_context_id = create_ox_context()
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=old_context_id,
        wait=False,
    )
    wait_for_listener(udm_object.dn)
    find_ox_object(old_context_id, "User", get_identifier(udm_object))
    new_context_id = create_ox_context()
    udm.modify("users/user", udm_object.dn, {"oxContext": new_context_id})
    wait_for_listener(udm_object.dn)
    find_ox_object(
        old_context_id,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )
    find_ox_object(new_context_id, "User", get_identifier(udm_object))
    new_context_id2 = create_ox_context()
    udm.modify("users/user", udm_object.dn, {"oxContext": new_context_id2})
    wait_for_listener(udm_object.dn)
    find_ox_object(
        old_context_id,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )
    find_ox_object(
        new_context_id,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )
    find_ox_object(new_context_id2, "User", get_identifier(udm_object))


@pytest.mark.k8s_skip(
    reason="Waiting for the same DN fails when k8s log backend falls back to polling because of 'fsnotify too many open files'.",
)
def test_existing_user_in_different_context(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    new_user_name,
    domainname,
    udm,
    wait_for_listener,
):
    """
    User already exists in OX DB (legacy data?) and a new
    user with the same name is created in UDM. First a another
    context; then the user is moved to the original context
    """
    User = get_ox_integration_class("SOAP", "User")
    new_context_id = create_ox_context()
    mail_address = "{}@{}".format(new_user_name, domainname)
    legacy_user = User(
        context_id=new_context_id,
        name=new_user_name,
        display_name=new_user_name,
        given_name="Leon",
        password="dummy",
        sur_name=new_user_name,
        primary_email=mail_address,
        email1=mail_address,
    )
    legacy_user.create()
    new_context_id2 = create_ox_context()
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=new_context_id2,
        wait=False,
    )
    wait_for_listener(udm_object.dn)
    udm.modify(
        "users/user",
        udm_object.dn,
        {"oxContext": new_context_id},
    )
    wait_for_listener(udm_object.dn)
    find_ox_object(
        new_context_id2,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    assert obj.given_name == "Emil"


def test_alias(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    new_user_name,
    domainname,
    udm,
    wait_for_listener,
):
    """
    Changing mailPrimaryAddress and email1 leads to appropriate aliases
    """
    new_context_id = create_ox_context()
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=new_context_id,
        wait=False,
    )
    mail_addresses = [
        "test1-{}@{}".format(new_user_name, domainname),
        "test2-{}@{}".format(new_user_name, domainname),
        "test3-{}@{}".format(new_user_name, domainname),
        "test4-{}@{}".format(new_user_name, domainname),
    ]
    wait_for_listener(
        udm_object.dn,
    )  # make sure we wait for the modify step below
    udm.modify(
        "users/user",
        udm_object.dn,
        {
            "mailPrimaryAddress": mail_addresses[0],
            "mailAlternativeAddress": mail_addresses[1:],
        },
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    assert sorted(obj.aliases) == sorted(mail_addresses)
    mail_addresses = [
        "test5-{}@{}".format(new_user_name, domainname),
    ]
    udm.modify(
        "users/user",
        udm_object.dn,
        {
            "mailPrimaryAddress": mail_addresses[0],
            "mailAlternativeAddress": mail_addresses[1:],
        },
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    assert sorted(obj.aliases) == sorted(mail_addresses)
    mail_addresses = [
        "test6-{}@{}".format(new_user_name, domainname),
        "test7-{}@{}".format(new_user_name, domainname),
    ]
    udm.modify(
        "users/user",
        udm_object.dn,
        {
            "mailPrimaryAddress": mail_addresses[0],
            "mailAlternativeAddress": mail_addresses[1:],
        },
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(new_context_id, "User", get_identifier(udm_object))
    assert sorted(obj.aliases) == sorted(mail_addresses)


def test_toggle_is_ox_user_property(
    find_ox_object,
    create_ox_user,
    default_ox_context,
    new_user_name,
    udm,
    wait_for_listener,
):
    """
    Toggling isOxUser property should create or remove the user in OX accordingly.
    Issue: https://git.knut.univention.de/univention/open-xchange/provisioning
    /-/issues/54
    """
    # Initially, create a user with isOxUser=False
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=default_ox_context,
        enabled=False,
        wait=False,
    )
    wait_for_listener(udm_object.dn)
    find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )

    # Toggle isOxUser to True and set a context
    udm.modify(
        "users/user",
        udm_object.dn,
        {"isOxUser": True, "oxContext": default_ox_context},
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
        assert_empty=False,
    )
    assert obj.name == get_identifier(udm_object)

    # Toggle isOxUser back to False, and the user should be removed from OX
    udm.modify("users/user", udm_object.dn, {"isOxUser": False})
    wait_for_listener(udm_object.dn)
    find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )


def test_toggle_is_ox_user_property_no_change(
    find_ox_object,
    create_ox_user,
    default_ox_context,
    new_user_name,
    udm,
    wait_for_listener,
):
    """
    Sad path (no change): Toggling isOxUser property should return isOxUser False as
    there is no change.
    Issue: https://git.knut.univention.de/univention/open-xchange/provisioning
    /-/issues/54
    """
    # Initially, create a user with isOxUser=False
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=None,
        enabled=False,
        wait=False,
    )
    wait_for_listener(
        udm_object.dn,
    )  # Ensure we wait for the modification to take effect
    find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )

    # Toggle isOxUser to False and it should still not be found in OX
    udm.modify(
        "users/user",
        udm_object.dn,
        {"isOxUser": False, "description": random_string()},
    )
    wait_for_listener(udm_object.dn)
    find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )


def test_toggle_is_ox_user_property_new_context(
    find_ox_object,
    create_ox_context,
    create_ox_user,
    default_ox_context,
    new_user_name,
    udm,
    wait_for_listener,
):
    """
    Sad path (invalid context): Toggling isOxUser property should fail to add the
    user in OX as the context is invalid.
    Issue: https://git.knut.univention.de/univention/open-xchange/provisioning
    /-/issues/54
    """
    # Initially, create a user with isOxUser=False
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=default_ox_context,
        enabled=False,
        wait=False,
    )
    wait_for_listener(udm_object.dn)
    find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )

    # Create new context and set it to user
    new_context_id = create_ox_context()
    udm.modify(
        "users/user",
        udm_object.dn,
        {"isOxUser": True, "oxContext": new_context_id},
    )
    wait_for_listener(udm_object.dn)

    # Ensure the user is not added to the old OX context
    find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
        assert_empty=True,
    )
    # Ensure the user is added to the new OX context
    find_ox_object(
        new_context_id,
        "User",
        get_identifier(udm_object),
        assert_empty=False,
    )


def test_default_sender_address(
    find_ox_object,
    create_ox_user,
    default_ox_context,
    new_user_name,
    domainname,
    udm,
    wait_for_listener,
):
    udm_object = create_ox_user(
        name=new_user_name,
        context_id=default_ox_context,
        wait=False,
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
    )
    assert obj.default_sender_address == obj.primary_email
    udm_obj = list(udm.search("users/user", f"username={new_user_name}"))[
        0
    ].open()
    # new_lastname = udm_obj.properties["lastname"] + "-Schmidt"  # unused variable
    old_primary_email = udm_obj.properties["mailPrimaryAddress"]
    old_primary_email_part1, old_primary_email_part2 = old_primary_email.split(
        "@",
    )
    new_primary_email = (
        f"{old_primary_email_part1}-schmidt@{old_primary_email_part2}"
    )
    udm.modify(
        "users/user",
        udm_object.dn,
        {
            "mailPrimaryAddress": new_primary_email,
            "mailAlternativeAddress": [old_primary_email],
        },
    )
    wait_for_listener(udm_object.dn)
    obj = find_ox_object(
        default_ox_context,
        "User",
        get_identifier(udm_object),
    )
    assert obj.primary_email == new_primary_email
    assert obj.default_sender_address == obj.primary_email
