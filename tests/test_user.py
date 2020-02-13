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


def create_obj(udm, name, domainname, context_id, enabled=True):
    dn = udm.create(
        "users/user",
        "cn=users",
        {
            "username": name,
            "firstname": "Emil",
            "lastname": name.title(),
            "password": "univention",
            "mailPrimaryAddress": "{}@{}".format(name, domainname),
            "isOxUser": enabled,
            "oxAccess": "premium",
            "oxContext": context_id,
        },
    )
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
        "users/user", dn, {"username": "new" + new_user_name,},
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


def test_modify_user_without_ox_obj(new_context_id, new_user_name, udm, ox_host, domainname):
    '''
    Changing UDM object without a OX pendant should just create it
    '''
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


def test_modify_mailserver(default_imap_server, new_context_id, new_user_name, udm, ox_host, domainname):
    udm.create('computers/memberserver', 'cn=memberserver,cn=computers', {'name': 'test-member', 'password': 'univention', 'service': ['IMAP']}, wait_for_listener=False)
    create_context(udm, ox_host, new_context_id)
    dn = create_obj(udm, new_user_name, domainname, new_context_id)
    obj = find_obj(new_context_id, new_user_name)
    assert obj.imap_server_string == default_imap_server
    mail_home_server = 'test-member.{}'.format(domainname)
    udm.modify(
        "users/user",
        dn,
        {
            "mailHomeServer": mail_home_server,
        },
    )
    obj = find_obj(new_context_id, new_user_name)
    # would fail if default_imap_server has a different port...
    assert obj.imap_server_string == 'imap://' + mail_home_server + ':143'


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
