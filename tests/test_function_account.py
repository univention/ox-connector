# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

from univention.ox.soap.backend_base import get_ox_integration_class
from univention.ox.provisioning.helpers import get_obj_by_name_from_ox


def create_obj(udm, name, domainname, personal, users, groups):
    dn = udm.create(
        "oxmail/functional_account",
        "cn=functional_accounts,cn=open-xchange",
        {
            "name": name,
            "mailPrimaryAddress": "{}@{}".format(name, domainname),
            "personal": personal,
            "users": users,
            "groups": groups,
        },
    )
    print("Created account", dn, "in UDM")
    return dn


def list_objs(context_id):
    FunctionalAccount = get_ox_integration_class("SOAP", "SecondaryAccount")
    return FunctionalAccount.list(context_id=context_id)


def get_user_from_ox(username, context_id):
    User = get_ox_integration_class("SOAP", "User")
    return get_obj_by_name_from_ox(User, context_id, username)


def test_add_functional_account_with_user(
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Creating a functional account should create it in contexts of the user
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(udm, new_functional_account_name, domainname, "Personal", [user.dn], [])
    wait_for_listener(dn)
    accounts = list_objs(context_id)
    assert len(accounts) == 1
    ox_user = get_user_from_ox(user.properties["username"], context_id)
    account = accounts[0]
    assert account.userId == ox_user.id


def test_add_functional_account_with_2_of_5_users(
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Creating a functional account with 2 of 5 users should exactly create 2 accounts
    """
    context_id = create_ox_context()
    user1 = create_ox_user(context_id=context_id)
    create_ox_user(context_id=context_id)
    user2 = create_ox_user(context_id=context_id)
    create_ox_user(context_id=context_id)
    create_ox_user(context_id=context_id)
    dn = create_obj(udm, new_functional_account_name, domainname, "Personal", [user1.dn, user2.dn], [])
    wait_for_listener(dn)
    accounts = list_objs(context_id)
    assert len(accounts) == 2
    ox_user1 = get_user_from_ox(user1.properties["username"], context_id)
    ox_user2 = get_user_from_ox(user2.properties["username"], context_id)
    assert sorted([account.userId for account in accounts]) == sorted([ox_user1.id, ox_user2.id])


def test_multiple_functional_accounts_same_user(
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Having two functional accounts with the same user must work
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn1 = create_obj(udm, new_functional_account_name + "-1", domainname, "Personal", [user.dn], [])
    wait_for_listener(dn1)
    dn2 = create_obj(udm, new_functional_account_name + "-2", domainname, "Personal", [user.dn], [])
    wait_for_listener(dn2)
    accounts = list_objs(context_id)
    assert len(accounts) == 2
    ox_user = get_user_from_ox(user.properties["username"], context_id)
    for account in accounts:
        assert account.userId == ox_user.id


def test_multiple_functional_accounts_different_user(
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Having two functional accounts with one user each must work
    """
    context_id = create_ox_context()
    user1 = create_ox_user(context_id=context_id)
    user2 = create_ox_user(context_id=context_id)
    dn1 = create_obj(udm, new_functional_account_name + "-1", domainname, "Personal", [user1.dn], [])
    wait_for_listener(dn1)
    dn2 = create_obj(udm, new_functional_account_name + "-2", domainname, "Personal", [user2.dn], [])
    wait_for_listener(dn2)
    accounts = list_objs(context_id)
    assert len(accounts) == 2
    ox_user1 = get_user_from_ox(user1.properties["username"], context_id)
    ox_user2 = get_user_from_ox(user2.properties["username"], context_id)
    for account in accounts:
        if account.name == new_functional_account_name + "-1":
            assert account.userId == ox_user1.id
        elif account.name == new_functional_account_name + "-2":
            assert account.userId == ox_user2.id
        else:
            raise RuntimeError("Who is that? " + account.name)


def test_modify_functional_account(
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Creating a functional account with 2 of 5 users should exactly create 2 accounts
    """
    context_id = create_ox_context()
    user1 = create_ox_user(context_id=context_id)
    user2 = create_ox_user(context_id=context_id)
    dn = create_obj(udm, new_functional_account_name, domainname, "Personal", [user1.dn], [])
    wait_for_listener(dn)
    ox_user1 = get_user_from_ox(user1.properties["username"], context_id)
    ox_user2 = get_user_from_ox(user2.properties["username"], context_id)

    accounts = list_objs(context_id)
    assert len(accounts) == 1
    assert accounts[0].userId == ox_user1.id

    udm.modify("oxmail/functional_account", dn, {
        "users": [user2.dn],
    })
    wait_for_listener(dn)
    accounts = list_objs(context_id)
    assert len(accounts) == 1
    assert accounts[0].userId == ox_user2.id


def test_empty_functional_account(
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    When a UDM functional_account has no users, no SecondaryAccount should exist
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(udm, new_functional_account_name, domainname, "Personal", [user.dn], [])
    wait_for_listener(dn)

    accounts = list_objs(context_id)
    assert len(accounts) == 1

    udm.modify("oxmail/functional_account", dn, {
        "users": [],
    })
    wait_for_listener(dn)
    accounts = list_objs(context_id)
    assert len(accounts) == 0


def test_remove_functional_account(
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Removing a functional account needs to remove the SecondaryAccount
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(udm, new_functional_account_name, domainname, "Personal", [user.dn], [])
    wait_for_listener(dn)

    accounts = list_objs(context_id)
    assert len(accounts) == 1

    udm.remove("oxmail/functional_account", dn)
    wait_for_listener(dn)
    accounts = list_objs(context_id)
    assert len(accounts) == 0


def test_remove_user(
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Removing a user which has been part of a functional account needs to work
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(udm, new_functional_account_name, domainname, "Personal", [user.dn], [])
    wait_for_listener(dn)

    accounts = list_objs(context_id)
    assert len(accounts) == 1

    udm.remove("users/user", user.dn)
    wait_for_listener(user.dn)
    wait_for_listener(dn)
    accounts = list_objs(context_id)
    assert len(accounts) == 0


def test_modify_user(
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
):
    """
    Removing a user which has been part of a functional account needs to work
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(udm, new_functional_account_name, domainname, "Personal", [user.dn], [])
    wait_for_listener(dn)

    accounts = list_objs(context_id)
    ox_user = get_user_from_ox(user.properties["username"], context_id)
    assert len(accounts) == 1
    assert accounts[0].userId == ox_user.id

    new_dn = udm.modify("users/user", user.dn, {"username": "new" + user.properties["username"]})
    assert user.dn != new_dn
    wait_for_listener(new_dn)
    wait_for_listener(dn)
    for account in udm.search("oxmail/functional_account", f"cn={new_functional_account_name}"):
        account = account.open()
        assert account.properties["users"] == [new_dn]
        break
    else:
        raise RuntimeError("No UDM object found")

    ox_user2 = get_user_from_ox("new" + user.properties["username"], context_id)
    accounts = list_objs(context_id)
    assert len(accounts) == 1
    assert accounts[0].userId == ox_user2.id
