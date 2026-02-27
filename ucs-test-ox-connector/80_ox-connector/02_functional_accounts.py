#!/usr/share/ucs-test/runner pytest-3 -s -l -vv
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2025 Univention GmbH

# desc: Check functional account dovecot login
# tags: [apptest]
# roles: []
# exposure: dangerous
# packages:
# - univention-ox

import os
import univention.testing.strings as uts
import univention.admin.uldap
from univention.testing.utils import wait_for_listener_replication
import subprocess
import pytest
from univention.config_registry import ucr as _ucr


ADMINDN = _ucr.get(
    'tests/domainadmin/account',
    'uid=Administrator,cn=users,%s' % (_ucr.get('ldap/base'),),
)
ADMINPW = _ucr.get('tests/domainadmin/pwd', 'univention')


@pytest.fixture(scope='session')
def maildomain(udm_session):
    maildomain = f'{uts.random_name()}.{uts.random_name()}'
    udm_session.create_object(
        'mail/domain',
        binddn=ADMINDN,
        bindpwd=ADMINPW,
        name=maildomain,
    )
    yield maildomain


@pytest.fixture(scope='session')
def position(udm_session):
    ouname = f'1+{uts.random_username_special_characters()}'
    oudn = udm_session.create_object(
        'container/ou',
        binddn=ADMINDN,
        bindpwd=ADMINPW,
        name=ouname,
    )
    yield oudn


@pytest.mark.parametrize(
    'username, memberOfFunc',
    [
        (uts.random_name(), True),
        (uts.random_name(), False),
    ],
)
@pytest.mark.skipif(
    not os.path.isfile('/usr/sbin/ox-server-install'),
    reason='fails on hosts without ox',
)
def test_func_acc_login(
    udm,
    ucr,
    maildomain,
    position,
    username,
    memberOfFunc,
):

    # create user
    mailprimaryaddress = f'{uts.random_name()}@{maildomain}'
    userdn = udm.create_object(
        'users/user',
        binddn=ADMINDN,
        bindpwd=ADMINPW,
        username=username,
        firstname=username,
        position=position,
        lastname=username,
        password='univention',
        mailPrimaryAddress=mailprimaryaddress,
    )

    # create functional account
    funcdn = udm.create_object(
        'oxmail/functional_account',
        binddn=ADMINDN,
        bindpwd=ADMINPW,
        name=uts.random_name(),
        users=[userdn] if memberOfFunc else [],
        mailPrimaryAddress=f'{uts.random_name()}@{maildomain}',
    )

    # get uoid of functional account
    lo, _position = univention.admin.uldap.getMachineConnection()
    oldattr = lo.search(base=funcdn)
    uoid = oldattr[0][1].get('univentionObjectIdentifier')[0].decode('utf-8')

    # wait for listener
    wait_for_listener_replication()

    # login as user should always work
    subprocess.check_output(
        ['doveadm', 'auth', 'login', f'{username}', 'univention'],
    )

    if memberOfFunc:
        subprocess.check_output(
            ['doveadm', 'auth', 'login', f'{uoid}{username}', 'univention'],
        )
        subprocess.check_output(
            [
                'doveadm',
                'auth',
                'login',
                f'{uoid}{mailprimaryaddress}',
                'univention',
            ],
        )
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_output(
                [
                    'doveadm',
                    'auth',
                    'login',
                    f'{uoid}{username}',
                    'univention123',
                ],
            )
    else:
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_output(
                [
                    'doveadm',
                    'auth',
                    'login',
                    f'{uoid}{username}',
                    'univention',
                ],
            )
        with pytest.raises(subprocess.CalledProcessError):
            subprocess.check_output(
                [
                    'doveadm',
                    'auth',
                    'login',
                    f'{uoid}{mailprimaryaddress}',
                    'univention',
                ],
            )
