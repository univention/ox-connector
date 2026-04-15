# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import pytest


def create_obj(
    udm,
    name,
    domainname,
    personal,
    users,
    position="cn=functional_accounts,cn=open-xchange",
):
    dn = udm.create(
        "oxmail/functional_account",
        position,
        {
            "name": name,
            "mailPrimaryAddress": "{}@{}".format(name, domainname),
            "personal": personal,
            "users": users,
        },
    )
    print("Created account", dn, "in UDM")
    return dn


POSITIONS = ["cn=functional_accounts,cn=open-xchange", "cn=users"]


@pytest.mark.parametrize('position', POSITIONS)
def test_add_functional_account_with_user_different_case_in_dn(
    get_ox_object,
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
    position,
):
    """
    Check if functional account is created if user.dn does not match case of dn on user object
    Creating a functional account should create it in contexts of the user
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(
        udm,
        new_functional_account_name,
        domainname,
        "Personal",
        [user.dn.upper()],
        position=position,
    )
    wait_for_listener(dn)
    account = get_ox_object(context_id, "SecondaryAccount")[0]
    ox_user = get_ox_object(context_id, "User", user.properties["username"])[0]
    assert account.userId == ox_user.id


@pytest.mark.parametrize('position', POSITIONS)
def test_add_functional_account_with_user(
    get_ox_object,
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
    position,
):
    """
    Creating a functional account should create it in contexts of the user
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(
        udm,
        new_functional_account_name,
        domainname,
        "Personal",
        [user.dn],
        position=position,
    )
    wait_for_listener(dn)
    account = get_ox_object(context_id, "SecondaryAccount")[0]
    ox_user = get_ox_object(context_id, "User", user.properties["username"])[0]
    assert account.userId == ox_user.id


@pytest.mark.parametrize('position', POSITIONS)
def test_add_functional_account_with_2_of_5_users(
    get_ox_object,
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
    position,
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
    dn = create_obj(
        udm,
        new_functional_account_name,
        domainname,
        "Personal",
        [user1.dn, user2.dn],
        position=position,
    )
    wait_for_listener(dn)
    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 2
    ox_user1 = get_ox_object(context_id, "User", user1.properties["username"])[
        0
    ]
    ox_user2 = get_ox_object(context_id, "User", user2.properties["username"])[
        0
    ]
    assert sorted([account.userId for account in accounts]) == sorted(
        [ox_user1.id, ox_user2.id],
    )


@pytest.mark.parametrize('position', POSITIONS)
def test_multiple_functional_accounts_same_user(
    get_ox_object,
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
    position,
):
    """
    Having two functional accounts with the same user must work
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn1 = create_obj(
        udm,
        new_functional_account_name + "-1",
        domainname,
        "Personal",
        [user.dn],
        position=position,
    )
    wait_for_listener(dn1)
    dn2 = create_obj(
        udm,
        new_functional_account_name + "-2",
        domainname,
        "Personal",
        [user.dn],
        position=position,
    )
    wait_for_listener(dn2)
    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 2
    ox_user = get_ox_object(context_id, "User", user.properties["username"])[0]
    for account in accounts:
        assert account.userId == ox_user.id


@pytest.mark.parametrize('position', POSITIONS)
def test_multiple_functional_accounts_different_user(
    get_ox_object,
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
    position,
):
    """
    Having two functional accounts with one user each must work
    """
    context_id = create_ox_context()
    user1 = create_ox_user(context_id=context_id)
    user2 = create_ox_user(context_id=context_id)
    dn1 = create_obj(
        udm,
        new_functional_account_name + "-1",
        domainname,
        "Personal",
        [user1.dn],
        position=position,
    )
    wait_for_listener(dn1)
    dn2 = create_obj(
        udm,
        new_functional_account_name + "-2",
        domainname,
        "Personal",
        [user2.dn],
        position=position,
    )
    wait_for_listener(dn2)
    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 2
    ox_user1 = get_ox_object(context_id, "User", user1.properties["username"])[
        0
    ]
    ox_user2 = get_ox_object(context_id, "User", user2.properties["username"])[
        0
    ]
    for account in accounts:
        if account.name == new_functional_account_name + "-1":
            assert account.userId == ox_user1.id
        elif account.name == new_functional_account_name + "-2":
            assert account.userId == ox_user2.id
        else:
            raise RuntimeError("Who is that? " + account.name)


@pytest.mark.parametrize('position', POSITIONS)
def test_modify_functional_account(
    get_ox_object,
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
    position,
):
    """
    Creating a functional account with 2 of 5 users should exactly create 2 accounts
    """
    context_id = create_ox_context()
    user1 = create_ox_user(context_id=context_id)
    user2 = create_ox_user(context_id=context_id)
    dn = create_obj(
        udm,
        new_functional_account_name,
        domainname,
        "Personal",
        [user1.dn],
        position=position,
    )
    wait_for_listener(dn)
    ox_user1 = get_ox_object(context_id, "User", user1.properties["username"])[
        0
    ]
    ox_user2 = get_ox_object(context_id, "User", user2.properties["username"])[
        0
    ]

    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 1
    assert accounts[0].userId == ox_user1.id

    udm.modify(
        "oxmail/functional_account",
        dn,
        {
            "users": [user2.dn],
        },
    )
    wait_for_listener(dn)
    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 1
    assert accounts[0].userId == ox_user2.id


@pytest.mark.parametrize('position', POSITIONS)
def test_empty_functional_account(
    get_ox_object,
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
    position,
):
    """
    When a UDM functional_account has no users, no SecondaryAccount should exist
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(
        udm,
        new_functional_account_name,
        domainname,
        "Personal",
        [user.dn],
        position=position,
    )
    wait_for_listener(dn)

    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 1

    udm.modify(
        "oxmail/functional_account",
        dn,
        {
            "users": [],
        },
    )
    wait_for_listener(dn)
    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 0


@pytest.mark.parametrize('position', POSITIONS)
def test_remove_functional_account(
    get_ox_object,
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
    position,
):
    """
    Removing a functional account needs to remove the SecondaryAccount
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(
        udm,
        new_functional_account_name,
        domainname,
        "Personal",
        [user.dn],
        position=position,
    )
    wait_for_listener(dn)

    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 1

    udm.remove("oxmail/functional_account", dn)
    wait_for_listener(dn)
    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 0


@pytest.mark.parametrize('position', POSITIONS)
def test_remove_user(
    get_ox_object,
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
    position,
):
    """
    Removing a user which has been part of a functional account needs to work
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(
        udm,
        new_functional_account_name,
        domainname,
        "Personal",
        [user.dn],
        position=position,
    )
    wait_for_listener(dn)

    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 1

    udm.remove("users/user", user.dn)
    wait_for_listener(user.dn)
    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 0


@pytest.mark.parametrize('position', POSITIONS)
def test_modify_user(
    get_ox_object,
    create_ox_context,
    create_ox_user,
    new_functional_account_name,
    udm,
    domainname,
    wait_for_listener,
    position,
):
    """
    Removing a user which has been part of a functional account needs to work
    """
    context_id = create_ox_context()
    user = create_ox_user(context_id=context_id)
    dn = create_obj(
        udm,
        new_functional_account_name,
        domainname,
        "Personal",
        [user.dn],
        position,
    )
    wait_for_listener(dn)

    accounts = get_ox_object(context_id, "SecondaryAccount")
    ox_user = get_ox_object(context_id, "User", user.properties["username"])[0]
    assert len(accounts) == 1
    assert accounts[0].userId == ox_user.id

    new_dn = udm.modify(
        "users/user",
        user.dn,
        {"username": "new" + user.properties["username"]},
    )
    assert user.dn != new_dn
    wait_for_listener(new_dn)
    for account in udm.search(
        "oxmail/functional_account",
        f"cn={new_functional_account_name}",
    ):
        account = account.open()
        assert account.properties["users"] == [new_dn]
        break
    else:
        raise RuntimeError("No UDM object found")

    ox_user2 = get_ox_object(
        context_id,
        "User",
        "new" + user.properties["username"],
    )[0]
    accounts = get_ox_object(context_id, "SecondaryAccount")
    assert len(accounts) == 1
    assert accounts[0].userId == ox_user2.id
