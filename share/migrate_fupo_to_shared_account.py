#!/usr/bin/python3
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

import argparse
import os
import sys

from pprint import pprint
from univention.admin.rest.client import Object, UDM, UnprocessableEntity
from ldap.dn import explode_rdn, explode_dn, str2dn
from ldap import DECODING_ERROR


def default_if_empty(value: str) -> str:
    """Return the default if value is empty."""
    return value if value else 'Full Mail Access'


def migrate_fupo_to_shared(
    fupo: Object,
    new_dn: str,
    permission: str,
    udm_client: UDM,
    oxContext: int,
    dry_run: bool,
) -> None:
    print('')
    print('Migrating the following functional account: ' + fupo.dn)
    print('UDM object:')
    print(fupo)
    print('Functional account properties:')
    pprint(fupo.properties)

    if dry_run:
        print('Step 1/4: Creating new shared account: ' + new_dn)
        print('')
        print('Step 2/4: Update the new shared account with linked users.')
        for user in fupo.objects['users']:
            user_object = user.open()
            if user_object.properties['isOxUser']:
                print(
                    'Step 2/4: Linking the following users: '
                    + user.open().dn
                    + ' with '
                    + permission,
                )
            else:
                print(
                    'WARNING: %s is not an OxUser, not linking it.'
                    % user_object.dn,
                )
        print('')
        print('Step 3/4: Removing old functional account: ' + fupo.dn)
        print('')
        print(
            'Step 4/4: Update the shared account email:'
            + fupo.properties['mailPrimaryAddress'],
        )
        print('')
    else:
        permission_module = udm_client.get("oxmail/shared_account_permission")
        shared_account_module = udm_client.get("oxmail/shared_account")
        email = fupo.properties['mailPrimaryAddress']
        permission_obj = next(
            permission_module.search('displayName=%s' % permission),
            None,
        )
        if permission_obj:
            permission_obj = permission_obj.open()
        else:
            sys.exit("ERROR: Aborting. Permission not found: " + permission)

        try:
            print('Step 1/4: Create a new shared account: ' + new_dn)
            print('')
            new_shared_account = shared_account_module.get(new_dn)
        except UnprocessableEntity:
            new_shared_account = shared_account_module.new(
                position=",".join(explode_dn(new_dn)[1:]),
            )

        new_shared_account.properties['name'] = str2dn(new_dn)[0][0][1]
        new_shared_account.properties['displayName'] = fupo.properties['name']
        new_shared_account.properties['mailPrimaryAddress'] = 'tmp_' + email
        new_shared_account.properties['oxContext'] = int(
            os.environ.get("DEFAULT_CONTEXT", oxContext),
        )
        try:
            new_shared_account.save()
        except UnprocessableEntity:
            sys.exit(
                'ERROR: Something wnent wrong while saving the dn: %s, aborting.'
                % new_shared_account.properties['name'],
            )

        print('Step 2/4: Update the new shared account with linked users.')
        for user in fupo.objects['users']:
            user_object = user.open()
            if user_object.properties['isOxUser']:
                print(
                    'Step 2/4: Linking the following users: '
                    + user_object.dn
                    + ' with '
                    + permission_obj.dn,
                )
                new_shared_account.properties['users'].append(
                    [
                        user_object.properties['univentionObjectIdentifier'],
                        permission_obj.properties[
                            'univentionObjectIdentifier'
                        ],
                    ],
                )
            else:
                print(
                    'WARNING: %s is not an OxUser, not linking it.'
                    % user_object.dn,
                )
        try:
            print('')
            new_shared_account.save()
        except UnprocessableEntity:
            sys.exit(
                'ERROR: Error while trying to link users to shared accounts.',
            )

        # delete old fupo
        print('Step 3/4: Deleting old functional account: ' + fupo.dn)
        print('')
        try:
            fupo.delete()
        except UnprocessableEntity:
            sys.exit(
                'ERROR: Error while trying to delete the functional account.',
            )

        # update email of the shared account to the fupo address
        print(
            'Step 4/4: Update the new shared account: '
            + new_shared_account.dn
            + 'email to: '
            + email,
        )
        print('')
        new_shared_account.properties['mailPrimaryAddress'] = email
        try:
            new_shared_account.save()
        except UnprocessableEntity:
            sys.exit(
                'ERROR: Error while trying to update the email of the shared account. Manual intervention needed.',
            )

        print('Resulting shared account: ' + new_shared_account.dn)
        print(new_shared_account)
        pprint(new_shared_account.properties)
        print('')


def generate_new_dn(dn: str, ldap_base: str) -> str:
    try:
        rdn = explode_rdn(dn)
    except DECODING_ERROR:
        sys.exit("ERROR: Cannot parse the specify dn: %s" % dn)
    new_base = f"cn=shared_accounts,cn=open-xchange,{ldap_base}"
    new_dn = f"{rdn[0]},{new_base}"
    return new_dn


parser = argparse.ArgumentParser()
parser.add_argument("dn", help='dn of the object to migrate, or \'*\' for all')
parser.add_argument(
    'permission',
    type=default_if_empty,
    help='Name of the permission given to the new shared account',
    nargs='?',
)

parser.add_argument(
    "new_dn",
    help="New dn, only used for single object migration",
    nargs="?",
)
parser.add_argument(
    "udm_user",
    help="Username to connect to the UDM REST API, can be specify as an environment variable UDM_USERNAME",
    nargs='?',
)
parser.add_argument(
    "udm_password",
    help="Password to connect to the UDM REST API, can be specify as an environment variable UDM_PASSWORD",
    nargs='?',
)
parser.add_argument(
    "udm_url",
    help="URL of the UDM REST API endpoint,  can be specify as an environment variable UDM_URL",
    nargs='?',
)
parser.add_argument(
    '--ox-context',
    help="Ox context where the shared account will be created.",
)
parser.add_argument("--dry-run", help="Enable a dry run", action='store_true')
args = parser.parse_args()
dn = args.dn
permission = args.permission
dry_run = args.dry_run

udm_url = os.environ.get("UDM_URL", args.udm_url)
udm_username = os.environ.get("UDM_USERNAME", args.udm_user)
udm_password = os.environ.get("UDM_PASSWORD", args.udm_password)

if not udm_url:
    sys.exit("ERROR: No UDM URL configured")
if not udm_username:
    sys.exit("ERROR: No UDM username provided")
if not udm_password:
    sys.exit("ERROR: No UDM password provided")


udm_client = UDM.http(udm_url, udm_username, udm_password)
ldap_base = udm_client.get_ldap_base()
fupo_module = udm_client.get("oxmail/functional_account")

if args.dry_run:
    print('dn: ' + dn)
    print('permission: ' + permission)
    print(args.new_dn)
    print('udm user: ' + udm_username)
    print('udm password: ' + '***')
    print('udm url: ' + udm_url)
    print('dry run: ' + str(dry_run))

if dn == '*':
    try:
        list_fupo = [fupo.open() for fupo in fupo_module.search('cn=*')]
    except Exception as exc:
        sys.exit(
            "ERROR: Something went wrong while fetching functional accounts, aborting: %s"
            % exc,
        )

    if dry_run:
        print(
            'Found the following Functional Accounts: '
            + ", ".join([fupo.dn for fupo in list_fupo]),
        )

    for fupo in list_fupo:
        new_dn = generate_new_dn(fupo.dn, ldap_base)
        migrate_fupo_to_shared(
            fupo,
            new_dn,
            permission,
            udm_client,
            args.ox_context,
            dry_run,
        )

else:
    if args.new_dn:
        new_dn = args.new_dn
    else:
        new_dn = generate_new_dn(dn, ldap_base)

    try:
        fupo = fupo_module.get(dn)
    except UnprocessableEntity:
        sys.exit("ERROR: %s cannot be found, aborting." % dn)

    migrate_fupo_to_shared(
        fupo,
        new_dn,
        permission,
        udm_client,
        args.ox_context,
        dry_run,
    )
