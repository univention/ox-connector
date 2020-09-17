import os
import random
import typing
import uuid

import pytest

from univention.ox.backend_base import User, get_ox_integration_class

T = typing.TypeVar("T")


def create_context(udm, ox_host, context_id) -> str:
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
        "users/user",
        dn,
        {"username": "new" + new_user_name},
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
    UserAttributeTest("email2", "oxEmail2", random_value_generator=random_mail_address),
    UserAttributeTest("email3", "oxEmail3", random_value_generator=random_mail_address),
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
    UserAttributeTest(
        "language",
        "oxLanguage",
        random_value_generator=random_language,
        none_generator=no_none,
    ),
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
    UserAttributeTest(
        "timezone",
        "oxTimeZone",
        random_value_generator=random_timezone,
        none_generator=no_none,
    ),
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
            "users/user",
            dn,
            {user_test.udm_name: value},
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
        "firstname": new_user_name_generator(),
        "lastname": new_user_name_generator(),
        "homeTelephoneNumber": [new_user_name_generator(), new_user_name_generator()],
        "mailPrimaryAddress": "{}@{}".format(new_user_name_generator(), domainname),
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
        "pagerTelephoneNumber": [new_user_name_generator()],
        "phone": [new_user_name_generator(), new_user_name_generator()],
        "postcode": new_user_name_generator(),
        "roomNumber": [new_user_name_generator()],
        "street": new_user_name_generator(),
    }
    dn = create_obj(udm, new_user_name, domainname, new_context_id, attrs=attrs)
    wait_for_listener(dn)
    obj = find_obj(new_context_id, new_user_name)
    for k, v in attrs.items():
        if k == "oxAccess":
            continue
        elif k in ("pagerTelephoneNumber", "roomNumber"):
            v = v[0]  # OX supports only one value, not a list
        elif k in ("phone", "homeTelephoneNumber"):
            continue  # handle separately
        soap_prop = udm_prop2soap_prop[k]
        obj_item = getattr(obj, soap_prop)
        error_msg = (
            f"Expected for k={k!r}({soap_prop!r}) v={v!r} but found {obj_item!r}."
        )
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
        error_msg = (
            f"Expected for k={k!r}({soap_props!r}) v={v!r} but found {obj_items!r}."
        )
        assert v == obj_items, error_msg


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
        "users/user",
        dn,
        {"mailHomeServer": mail_home_server},
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
    dn = create_obj(udm, new_user_name, domainname, None, enabled=False)
    wait_for_listener(dn)  # make sure we wait for the modify step below
    # BUG: some hook seems to remove the ox specific attributes when enabling the user
    # BUG: so we have to do it in two steps: Bug #50469
    udm.modify("users/user", dn, {"isOxUser": True})
    udm.modify(
        "users/user", dn, {"oxContext": new_context_id, "oxDisplayName": new_user_name}
    )
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


def test_existing_user_in_different_context(
    new_context_id_generator, new_user_name, udm, ox_host, domainname, wait_for_listener
):
    """
    User already exists in OX DB (legacy data?) and a new
    user with the same name is created in UDM. First a another
    context; then the user is moved to the original context
    """
    User = get_ox_integration_class("SOAP", "User")
    new_context_id = new_context_id_generator()
    context_dn = create_context(udm, ox_host, new_context_id)
    wait_for_listener(context_dn)
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
    new_context_id2 = new_context_id_generator()
    create_context(udm, ox_host, new_context_id2)
    dn = create_obj(udm, new_user_name, domainname, new_context_id2)
    wait_for_listener(dn)
    udm.modify(
        "users/user",
        dn,
        {"oxContext": new_context_id},
    )
    wait_for_listener(dn)
    find_obj(new_context_id2, new_user_name, assert_empty=True)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.given_name == "Emil"


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
