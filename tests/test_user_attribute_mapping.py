# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import json
import os
import random
import subprocess
import typing
import uuid
from random import randrange
from datetime import timedelta, datetime


import pytest
from univention.ox.provisioning.default_user_mapping import DEFAULT_USER_MAPPING
from univention.ox.soap.backend_base import User, get_ox_integration_class

T = typing.TypeVar("T")


def create_obj(udm, name, domainname, context_id, attrs=None, enabled=True) -> str:
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
    dn = udm.create(
        "users/user",
        "cn=users",
        _attrs,
    )
    return dn


def find_obj(context_id, name, assert_empty=False, print_obj=True) -> User:
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


def delete_obj(context_id, name) -> None:
    obj = find_obj(context_id, name)
    print("Removing", obj.id, "directly in OX")
    obj.remove()
    find_obj(context_id, name, assert_empty=True)


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


def random_date():
    start = datetime.strptime('1/1/1990', '%m/%d/%Y')
    end = datetime.strptime('1/1/2024', '%m/%d/%Y')
    delta = end - start
    int_delta = (delta.days * 24 * 60 * 60) + delta.seconds
    random_second = randrange(int_delta)
    return (start + timedelta(seconds=random_second)).replace(hour=0, minute=0, second=0).strftime("%Y-%m-%d")


def str2isodate(text):
    exc1 = exc2 = None
    try:
        the_date = datetime.datetime.strptime(text, "%Y-%m-%d")
        return "{:%Y-%m-%d}".format(the_date)
    except (TypeError, ValueError) as exc:
        exc1 = exc
    try:
        the_date = datetime.datetime.strptime(text, "%d.%m.%Y")
        return "{:%Y-%m-%d}".format(the_date)
    except (TypeError, ValueError) as exc:
        exc2 = exc
    raise ValueError(
        "Value {!r} in unknown date format or year before 1900 ({} {}).".format(
            text, exc1, exc2,
        ),
    )


class UserAttributeTest(typing.NamedTuple):
    soap_name: str
    udm_name: str
    none_generator: typing.Callable[[], None] = none
    random_value_generator: typing.Callable[[], str] = random_string
    soap_value_from_udm_value: typing.Callable[[T], T] = ident


def get_user_mapping():
    try:
        with open(
            "/var/lib/univention-appcenter/apps/ox-connector/data/AttributeMapping.json",
            "r",
        ) as fd:
            return json.loads(fd.read())
    except (OSError, ValueError, IOError):
        return DEFAULT_USER_MAPPING


ATTRIBUTE_MAPPING = get_user_mapping()


user_attributes: typing.List[UserAttributeTest] = [
    UserAttributeTest("branches", ATTRIBUTE_MAPPING["branches"].get("ldap_attribute")),
    UserAttributeTest(
        "cellular_telephone1",
        ATTRIBUTE_MAPPING["cellular_telephone1"].get("ldap_attribute"),
    ),
    UserAttributeTest(
        "cellular_telephone2",
        ATTRIBUTE_MAPPING["cellular_telephone2"].get("ldap_attribute"),
        random_value_generator=random_list_of_string,
        none_generator=empty,
        soap_value_from_udm_value=take_first,
    ),
    UserAttributeTest(
        "city_business", ATTRIBUTE_MAPPING["city_business"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "city_home", ATTRIBUTE_MAPPING["city_home"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "city_other", ATTRIBUTE_MAPPING["city_other"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "commercial_register",
        ATTRIBUTE_MAPPING["commercial_register"].get("ldap_attribute"),
    ),
    UserAttributeTest("company", ATTRIBUTE_MAPPING["company"].get("ldap_attribute")),
    UserAttributeTest(
        "country_business", ATTRIBUTE_MAPPING["country_business"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "country_home", ATTRIBUTE_MAPPING["country_home"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "country_other", ATTRIBUTE_MAPPING["country_other"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "department", ATTRIBUTE_MAPPING["department"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "display_name",
        ATTRIBUTE_MAPPING["display_name"].get("ldap_attribute"),
        none_generator=no_none,
    ),
    #UserAttributeTest(
    #    "birthday",
    #    ATTRIBUTE_MAPPING["birthday"].get("ldap_attribute"),
    #    random_value_generator=random_date,
    #    soap_value_from_udm_value=str2isodate
    #), Bug in OX prevents from unsetting this attribute via SOAP if it was already set
    #UserAttributeTest(
    #    "anniversary",
    #    ATTRIBUTE_MAPPING["anniversary"].get("ldap_attribute"),
    #    random_value_generator=random_date,
    #    soap_value_from_udm_value=str2isodate
    #), Bug in OX prevents from unsetting this attribute via SOAP if it was already set
    UserAttributeTest(
        "email2",
        ATTRIBUTE_MAPPING["email2"].get("ldap_attribute"),
        random_value_generator=random_mail_address,
    ),
    UserAttributeTest(
        "email3",
        ATTRIBUTE_MAPPING["email3"].get("ldap_attribute"),
        random_value_generator=random_mail_address,
    ),
    UserAttributeTest(
        "fax_business", ATTRIBUTE_MAPPING["fax_business"].get("ldap_attribute")
    ),
    UserAttributeTest("fax_home", ATTRIBUTE_MAPPING["fax_home"].get("ldap_attribute")),
    UserAttributeTest(
        "fax_other", ATTRIBUTE_MAPPING["fax_other"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "given_name",
        ATTRIBUTE_MAPPING["given_name"].get("ldap_attribute"),
        none_generator=no_none,
    ),
    UserAttributeTest(
        "instant_messenger1",
        ATTRIBUTE_MAPPING["instant_messenger1"].get("ldap_attribute"),
    ),
    UserAttributeTest(
        "instant_messenger2",
        ATTRIBUTE_MAPPING["instant_messenger2"].get("ldap_attribute"),
    ),
    UserAttributeTest(
        "manager_name", ATTRIBUTE_MAPPING["manager_name"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "marital_status", ATTRIBUTE_MAPPING["marital_status"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "middle_name", ATTRIBUTE_MAPPING["middle_name"].get("ldap_attribute")
    ),
    UserAttributeTest("nickname", ATTRIBUTE_MAPPING["nickname"].get("ldap_attribute")),
    UserAttributeTest("note", ATTRIBUTE_MAPPING["note"].get("ldap_attribute")),
    UserAttributeTest(
        "number_of_children",
        ATTRIBUTE_MAPPING["number_of_children"].get("ldap_attribute"),
    ),
    UserAttributeTest(
        "number_of_employee",
        ATTRIBUTE_MAPPING["number_of_employee"].get("ldap_attribute"),
    ),
    UserAttributeTest("position", ATTRIBUTE_MAPPING["position"].get("ldap_attribute")),
    UserAttributeTest(
        "postal_code_business",
        ATTRIBUTE_MAPPING["postal_code_business"].get("ldap_attribute"),
    ),
    UserAttributeTest(
        "postal_code_home", ATTRIBUTE_MAPPING["postal_code_home"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "postal_code_other",
        ATTRIBUTE_MAPPING["postal_code_other"].get("ldap_attribute"),
    ),
    UserAttributeTest(
        "profession", ATTRIBUTE_MAPPING["profession"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "room_number",
        ATTRIBUTE_MAPPING["room_number"].get("ldap_attribute"),
        random_value_generator=random_list_of_string,
        none_generator=empty,
        soap_value_from_udm_value=take_first,
    ),
    UserAttributeTest(
        "sales_volume", ATTRIBUTE_MAPPING["sales_volume"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "spouse_name", ATTRIBUTE_MAPPING["spouse_name"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "state_business", ATTRIBUTE_MAPPING["state_business"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "state_home", ATTRIBUTE_MAPPING["state_home"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "state_other", ATTRIBUTE_MAPPING["state_other"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "street_business", ATTRIBUTE_MAPPING["street_business"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "street_home", ATTRIBUTE_MAPPING["street_home"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "street_other", ATTRIBUTE_MAPPING["street_other"].get("ldap_attribute")
    ),
    UserAttributeTest("suffix", ATTRIBUTE_MAPPING["suffix"].get("ldap_attribute")),
    UserAttributeTest(
        "sur_name",
        ATTRIBUTE_MAPPING["sur_name"].get("ldap_attribute"),
        none_generator=no_none,
    ),
    UserAttributeTest("tax_id", ATTRIBUTE_MAPPING["tax_id"].get("ldap_attribute")),
    UserAttributeTest(
        "telephone_assistant",
        ATTRIBUTE_MAPPING["telephone_assistant"].get("ldap_attribute"),
    ),
    UserAttributeTest(
        "telephone_business1",
        ATTRIBUTE_MAPPING["telephone_business1"].get("ldap_attribute"),
        random_value_generator=random_list_of_string,
        none_generator=empty,
        soap_value_from_udm_value=take_first,
    ),
    UserAttributeTest(
        "telephone_business2",
        ATTRIBUTE_MAPPING["telephone_business2"].get("ldap_attribute"),
        random_value_generator=random_list_of_strings,
        none_generator=empty,
        soap_value_from_udm_value=take_second,
    ),
    UserAttributeTest(
        "telephone_car", ATTRIBUTE_MAPPING["telephone_car"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "telephone_company",
        ATTRIBUTE_MAPPING["telephone_company"].get("ldap_attribute"),
    ),
    UserAttributeTest(
        "telephone_home1",
        ATTRIBUTE_MAPPING["telephone_home1"].get("ldap_attribute"),
        random_value_generator=random_list_of_string,
        none_generator=empty,
        soap_value_from_udm_value=take_first,
    ),
    UserAttributeTest(
        "telephone_home2",
        ATTRIBUTE_MAPPING["telephone_home2"].get("ldap_attribute"),
        random_value_generator=random_list_of_strings,
        none_generator=empty,
        soap_value_from_udm_value=take_second,
    ),
    UserAttributeTest(
        "telephone_ip", ATTRIBUTE_MAPPING["telephone_ip"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "telephone_other", ATTRIBUTE_MAPPING["telephone_other"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "telephone_pager",
        ATTRIBUTE_MAPPING["telephone_pager"].get("ldap_attribute"),
        random_value_generator=random_list_of_string,
        none_generator=empty,
        soap_value_from_udm_value=take_first,
    ),
    UserAttributeTest(
        "telephone_telex", ATTRIBUTE_MAPPING["telephone_telex"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "telephone_ttytdd", ATTRIBUTE_MAPPING["telephone_ttytdd"].get("ldap_attribute")
    ),
    UserAttributeTest("title", ATTRIBUTE_MAPPING["title"].get("ldap_attribute")),
    UserAttributeTest("url", ATTRIBUTE_MAPPING["url"].get("ldap_attribute")),
    UserAttributeTest(
        "userfield01", ATTRIBUTE_MAPPING["userfield01"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield02", ATTRIBUTE_MAPPING["userfield02"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield03", ATTRIBUTE_MAPPING["userfield03"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield04", ATTRIBUTE_MAPPING["userfield04"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield05", ATTRIBUTE_MAPPING["userfield05"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield06", ATTRIBUTE_MAPPING["userfield06"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield07", ATTRIBUTE_MAPPING["userfield07"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield08", ATTRIBUTE_MAPPING["userfield08"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield09", ATTRIBUTE_MAPPING["userfield09"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield10", ATTRIBUTE_MAPPING["userfield10"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield11", ATTRIBUTE_MAPPING["userfield11"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield12", ATTRIBUTE_MAPPING["userfield12"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield13", ATTRIBUTE_MAPPING["userfield13"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield14", ATTRIBUTE_MAPPING["userfield14"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield15", ATTRIBUTE_MAPPING["userfield15"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield16", ATTRIBUTE_MAPPING["userfield16"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield17", ATTRIBUTE_MAPPING["userfield17"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield18", ATTRIBUTE_MAPPING["userfield18"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield19", ATTRIBUTE_MAPPING["userfield19"].get("ldap_attribute")
    ),
    UserAttributeTest(
        "userfield20", ATTRIBUTE_MAPPING["userfield20"].get("ldap_attribute")
    ),
]



def attr_id(value: UserAttributeTest, index=[]) -> str:
    try:
        index[0] += 1
    except IndexError:
        index.append(1)
    return f"{value.udm_name} ({index[0]}/{len(user_attributes)})"


@pytest.mark.parametrize("user_test", user_attributes, ids=attr_id)
def test_unset_set_mapping(
    create_ox_context,
    new_user_name,
    new_user_name_generator,
    udm,
    domainname,
    user_test,
    wait_for_listener,
):
    """
    Unsetting an OX property from the mapping should prevent the synchronization.
    """

    new_context_id = create_ox_context()
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    wait_for_listener(dn)  # make sure we wait for the modify step below
    value = user_test.random_value_generator()
    if value is NotImplemented:
        return
    udm.modify(
        "users/user",
        dn,
        {user_test.udm_name: value},
    )

    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name, print_obj=False)
    soap_value = getattr(obj, user_test.soap_name)
    assert soap_value is not None

    # Check that after unsetting the mapping the value is None
    subprocess.run(
        [
            "python3",
            "/usr/local/share/ox-connector/resources/change_attribute_mapping.py",
            "modify",
            "--unset",
            user_test.soap_name,
        ]
    )
    value = user_test.random_value_generator()
    udm.modify(
        "users/user",
        dn,
        {user_test.udm_name: value, "description": random_string()},
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name, print_obj=False)
    soap_value = getattr(obj, user_test.soap_name)
    assert soap_value is None

    subprocess.run(
        [
            "python3",
            "/usr/local/share/ox-connector/resources/change_attribute_mapping.py",
            "modify",
            "--set",
            user_test.soap_name,
            user_test.udm_name,
        ]
    )

    # Check that after setting the mapping the value is synchronized
    udm.modify(
        "users/user",
        dn,
        {user_test.udm_name: value, "description": random_string()},
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name, print_obj=False)
    soap_value = getattr(obj, user_test.soap_name)
    value = user_test.soap_value_from_udm_value(value)
    assert soap_value == value

    # subprocess.run(['python3', '/usr/local/share/ox-connector/resources/change_attribute_mapping.py', 'restore_default'])


def test_change_mapping(
    create_ox_context,
    new_user_name,
    udm,
    domainname,
    wait_for_listener,
):
    subprocess.run(
        [
            "python3",
            "/usr/local/share/ox-connector/resources/change_attribute_mapping.py",
            "modify",
            "--set",
            "userfield01",
            "description",
        ]
    )

    new_mail_address = "{}2@{}".format(new_user_name, domainname)
    new_context_id = create_ox_context()
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    wait_for_listener(dn)  # make sure we wait for the modify step below
    description = "Using description as userfield01"
    udm.modify(
        "users/user",
        dn,
        {
            "description": description,
            "mailPrimaryAddress": new_mail_address,
        },
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.userfield01 == description

    subprocess.run(
        [
            "python3",
            "/usr/local/share/ox-connector/resources/change_attribute_mapping.py",
            "modify",
            "--set",
            "userfield01",
            "oxUserfield01",
        ]
    )
    description2 = "Using oxUserfield01 as userfield01"

    udm.modify(
        "users/user",
        dn,
        {
            "oxUserfield01": description2,
        },
    )

    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.userfield01 == description2

    subprocess.run(
        [
            "python3",
            "/usr/local/share/ox-connector/resources/change_attribute_mapping.py",
            "modify",
            "--set",
            "email1",
            "mailPrimaryAddress",
            "--unset_alternatives",
            "email1",
        ]
    )


def test_use_alternative(
    create_ox_context,
    new_user_name,
    udm,
    domainname,
    wait_for_listener,
):
    subprocess.run(
        [
            "python3",
            "/usr/local/share/ox-connector/resources/change_attribute_mapping.py",
            "modify",
            "--set",
            "email1",
            "oxUserfield01",
            "--set_alternatives",
            "email1",
            "mailPrimaryAddress",
        ]
    )

    new_mail_address = "{}2@{}".format(new_user_name, domainname)
    new_context_id = create_ox_context()
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    wait_for_listener(dn)  # make sure we wait for the modify step below
    udm.modify(
        "users/user",
        dn,
        {
            "mailPrimaryAddress": new_mail_address,
        },
    )
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.email1 == new_mail_address

    # Check that after setting the main attribute that value is used
    new_mail_address2 = "{}222@{}".format(new_user_name, domainname)
    udm.modify(
        "users/user",
        dn,
        {
            "oxUserfield01": new_mail_address2,
        },
    )

    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.email1 == new_mail_address2

    subprocess.run(
        [
            "python3",
            "/usr/local/share/ox-connector/resources/change_attribute_mapping.py",
            "modify",
            "--set",
            "email1",
            "mailPrimaryAddress",
            "--unset_alternatives",
            "email1",
        ]
    )
