# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

import pytest
from contextlib import nullcontext as does_not_raise
import requests

from univention.ox.provisioning.functional_account import configure_functional_account_login


@pytest.mark.parametrize("test_input,expected_output,expectation",
                         [("{{fa_entry_uuid}}", [(0,17)], does_not_raise()),
                          ("{{entry_uuid}}{{fa_entry_uuid}}", [(14, 31),(0,14)], does_not_raise()),
                          ("{{fa_entry_uuid}}:", [(0,17)], does_not_raise()),
                          ("{{fa_entry_uuid}}::::", [(0,17)], does_not_raise()),
                          ("{{fa_entry_uuid}}:{{username}}", [(18, 30), (0,17)], does_not_raise()),
                          ("{{fa_entry_uuid}}:{{username}}+", [(18, 30), (0,17)], does_not_raise()),
                          (".{{fa_entry_uuid}}", [(1,18)], does_not_raise()),
                          ("{{fa_entry_uuid}}a", [(0,17)], does_not_raise()),
                          ("fa_entry_uuid", [], does_not_raise()),
                          ])
def test_functional_account_setting(test_input, expected_output, expectation):
    with expectation:
        res = configure_functional_account_login(test_input)
        assert res == expected_output


def get_default_containers(uri, username, password):
    session = requests.Session()
    session.auth = (username, password)
    session.headers = {
        'X-Requested-With': 'XmlHttpRequest',
        'Accept': 'application/json',
    }
    data = {
        'options': {
            'objectType': 'oxmail/functional_account',
        },
        'flavor': 'oxmail/functional_account',
    }
    res = session.post(f"{uri}/command/udm/containers", data=data)
    return [i.get('id') for i in res.json().get('result')]


def test_functional_account_default_container(udm, udm_admin_username, udm_admin_password, umc_uri, ldap_base):
    try:
        dn = f'cn=default containers,cn=univention,{ldap_base}'
        udm.modify('settings/directory', dn, {'ox_functional_accounts': [f'cn=users,{ldap_base}', f'cn=groups,{ldap_base}']})
        containers = get_default_containers(umc_uri, udm_admin_username, udm_admin_password)
        expected = [f'cn=groups,{ldap_base}', f'cn=functional_accounts,cn=open-xchange,{ldap_base}', f'cn=users,{ldap_base}']
        assert set(containers) == set(expected)
    finally:
        udm.modify('settings/directory', dn, {'ox_functional_accounts': []})
