#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2022 Univention GmbH
#
# http://www.univention.de/
#
# All rights reserved.
#
# The source code of this program is made available
# under the terms of the GNU Affero General Public License version 3
# (GNU AGPL V3) as published by the Free Software Foundation.
#
# Binary versions of this program provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention and not subject to the GNU AGPL V3.
#
# In the case you use this program under the terms of the GNU AGPL V3,
# the program is provided in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the
# GNU Affero General Public License for more details.
#
# You should have received a copy of the GNU Affero General Public
# License with the Debian GNU/Linux or Univention distribution in file
# /usr/share/common-licenses/AGPL-3; if not, see
# <http://www.gnu.org/licenses/>.

import os

from argparse import ArgumentParser

from univention.config_registry import ConfigRegistry
import univention.admin.uldap
import univention.admin.modules as udm_modules
import univention.admin.objects as udm_objects

# determine current lookup filter from users/user
udm_modules.update()
usersmod = udm_modules.get("users/user")
user_filter = str(usersmod.lookup_filter(filter_s='(objectClass=oxUserObject)'))

ucr = ConfigRegistry()
ucr.load()


def write_it(lo, pos, fname):
    if os.path.exists(fname):
        print("{} already exists, not touching it... Remove it and rerun this script if needed".format(fname))
        return
    with open(fname, 'w') as fd:
        for res in lo.search(filter=user_filter, attr=['oxAccess', 'oxDrive']):
            dn, attrs = res
            profile = attrs.get('oxAccess', ['none'])[0]
            if profile in ['webmail', 'pim'] and attrs.get('oxDrive', ['0'])[0] == '1':
                profile = profile + '_drive'
            print("Found {} having access to {}".format(dn, profile))
            fd.write("{}\t{}\n".format(dn, profile))


def apply_it(lo, pos, fname):
    mod = udm_modules.get('users/user')
    udm_modules.init(lo, pos, mod)
    with open(fname) as fd:
        for line in fd:
            dn, access = line[:-1].split('\t')
            user = udm_objects.get(mod, None, lo, pos, dn)
            udm_objects.open(user)
            old_access = user['oxAccess']
            if old_access == access:
                print("{}: no access change ({})".format(user.dn, access))
            else:
                user['oxAccess'] = access
                user.modify()
                print("{}: changed to ({})".format(user.dn, access))


parser = ArgumentParser()
parser.add_argument('--write', action='store_true', help='Write the current state of the user access profiles')
parser.add_argument('--apply', action='store_true', help='Apply a previously written state to the users')
parser.add_argument('--file', help='Filename where the state is written to or read from')
parser.add_argument('--binddn', help='Bind DN for LDAP connection')
parser.add_argument('--bindpwdfile', help='Filename where the LDAP password is stored in')
args = parser.parse_args()

master = ucr.get('ldap/master')
port = ucr.get('ldap/master/port')
base = ucr.get('ldap/base')

if args.binddn:
    lo = univention.admin.uldap.access(master, port, base, args.binddn, open(args.bindpwdfile).read())
    pos = univention.admin.uldap.position(base)
else:
    lo, pos = univention.admin.uldap.getAdminConnection()

if args.write:
    write_it(lo, pos, args.file)
if args.apply:
    apply_it(lo, pos, args.file)
