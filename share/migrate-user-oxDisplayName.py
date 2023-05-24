#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Univention GmbH
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

import csv
import os

from argparse import ArgumentParser

from univention.config_registry import ConfigRegistry
import univention.admin.uldap
import univention.admin.modules as udm_modules
import univention.admin.objects as udm_objects

# determine current lookup filter from users/user
udm_modules.update()
usersmod = udm_modules.get("users/user")
user_filter = str(usersmod.lookup_filter(filter_s='(&(objectClass=oxUserObject)(oxDisplayName=*))'))

ucr = ConfigRegistry()
ucr.load()


def write_it(lo, pos, fname):
    if os.path.exists(fname):
        print("{} already exists, not touching it... Remove it and rerun this script if needed".format(fname))
        return
    with open(fname, 'w') as fd:
        csv_writer = csv.writer(fd, delimiter='\t',
                            quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for res in lo.search(filter=user_filter, attr=['oxDisplayName', 'displayName']):
            dn, attrs = res
            ox_display_name = attrs.get('oxDisplayName', [None])[0]
            display_name = attrs.get('displayName', [None])[0]
            new_displayname = display_name or ox_display_name
            if new_displayname != display_name:
                print("Found {} with displayname {} {}".format(dn, display_name, new_display))
                csv_writer.writerow(dn, new_displayname)


def apply_it(lo, pos, fname):
    mod = udm_modules.get('users/user')
    udm_modules.init(lo, pos, mod)
    with open(fname) as fd:
        csv_reader = csv.reader(fd, delimiter='\t', quotechar='|')
        for line in csv_reader:
            dn = line[0]
            displayname = line[1]
            user = udm_objects.get(mod, None, lo, pos, dn)
            udm_objects.open(user)
            del user['oxDisplayName']
            user['displayName'] = displayname
            user.modify()
            print("{}: changed to ({})".format(user.dn, displayname))


parser = ArgumentParser()
parser.add_argument('--write', action='store_true', help='Write the current state of the user display names')
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
