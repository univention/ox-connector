#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# As of version 2.1.4 the user attribute oxAccessUSM is deprecated.
# USM permissions should now only be granted via access profiles.
# This script finds all users who still have the deprecated attribute
# oxAccessUSM and creates an access profile for them which contains
# an equivalent to the permissions previously set by the oxAccessUSM
# attribute.
#
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
import re
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path
from argparse import ArgumentParser

from univention.config_registry import ConfigRegistry
import univention.admin.uldap
import univention.admin.modules as udm_modules
import univention.admin.objects as udm_objects

# determine current lookup filter from users/user
udm_modules.update()
usersmod = udm_modules.get("users/user")
user_filter = str(usersmod.lookup_filter(
    filter_s='(&(objectClass=oxUserObject)(oxDisplayName=*))'))

ucr = ConfigRegistry()
ucr.load()

base_dir = Path("/var/lib/univention-appcenter/apps/")
data_dir = base_dir / "ox-connector" / "data"
access_definitions_file = data_dir / "ModuleAccessDefinitions.properties"

capability_map = {
    "usm": "USM",
    "activesync": "activeSync",
    "calendar": "calendar",
    "collectemailaddresses": "collectEmailAddresses",
    "contacts": "contacts",
    "delegatetask": "delegateTask",
    "deniedportal": "deniedPortal",
    "editgroup": "editGroup",
    "editpassword": "editPassword",
    "editpublicfolders": "editPublicFolders",
    "editresource": "editResource",
    "globaladdressbookdisabled": "globalAddressBookDisabled",
    "ical": "ical",
    "infostore": "infostore",
    "multiplemailaccounts": "multipleMailAccounts",
    # "": "publicFolderEditable",  # context admin right
    "readcreatesharedfolders": "readCreateSharedFolders",
    "subscription": "subscription",
    "syncml": "syncml",
    "tasks": "tasks",
    "vcard": "vcard",
    "webdav": "webdav",
    "webdavxml": "webdavXml",
    "webmail": "webmail",
}

capability_map_rev = {y: x for x, y in capability_map.items()}

_profiles = OrderedDict()


def get_access_profiles(force_reload):
    if not _profiles or force_reload:
        _profiles.clear()
        regex = re.compile(r"^(\w+)=(.+)")
        try:
            with open(access_definitions_file) as fd:
                for line in fd:
                    match = regex.match(line)
                    if match:
                        name = match.groups()[0].strip()
                        capabilities = {x.strip()
                                        for x in match.groups()[1].split(",")}
                        _profiles[name] = [
                            capability_map.get(cap, cap) for cap in capabilities
                        ]
        except EnvironmentError:
            print(
                f"Could not read {access_definitions_file}. Working with empty set..."
            )
    return deepcopy(_profiles)


def get_access_profile(profile_name, force_reload=False):
    return get_access_profiles(force_reload).get(profile_name)


def write_it(lo, pos, fname):
    if os.path.exists(fname):
        print("{} already exists, not touching it... Remove it and rerun this script if needed".format(fname))
        return
    with open(fname, 'w') as fd:
        csv_writer = csv.writer(fd, delimiter='\t',
                                quotechar='|', quoting=csv.QUOTE_MINIMAL)
        for res in lo.search(filter=user_filter, attr=['oxAccess', 'oxAccessUSM']):
            dn, attrs = res
            ox_access_usm = attrs.get('oxAccessUSM', [None])[0]
            ox_access = attrs.get('oxAccess', [b''])[0].decode('UTF-8')
            access_profile = get_access_profile(ox_access)
            if ox_access_usm == b"OK" and access_profile and not ('USM' in access_profile and 'activeSync' in access_profile):
                print("Found {} with oxAccessUSM enabled and an Access profile without mobility {}".format(
                    dn, ox_access))
                csv_writer.writerow((dn, ox_access))


def apply_it(lo, pos, fname):
    mod = udm_modules.get('users/user')
    udm_modules.init(lo, pos, mod)

    mod_accessprofile = udm_modules.get('oxmail/accessprofile')
    accessprofile_pos = univention.admin.uldap.position(
        f"cn=accessprofiles,cn=open-xchange,{ucr['ldap/base']}")
    udm_modules.init(lo, pos, mod)

    with open(fname) as fd:
        csv_reader = csv.reader(fd, delimiter='\t', quotechar='|')
        for line in csv_reader:
            dn = line[0]
            ox_access = line[1]
            user = udm_objects.get(mod, None, lo, pos, dn)
            udm_objects.open(user)
            if get_access_profile(ox_access + "_mobility", True):
                user['oxAccess'] = ox_access + "_mobility"
            else:
                if not get_access_profile(ox_access + "_mobility_migrated", True):
                    oxaccess_profile = udm_objects.default(
                        mod_accessprofile, None, lo, accessprofile_pos)
                    oxaccess_profile.open()
                    access_profile = get_access_profile(ox_access)
                    for k in access_profile:
                        oxaccess_profile[capability_map_rev[k]] = True
                    oxaccess_profile['usm'] = True
                    oxaccess_profile['activesync'] = True
                    oxaccess_profile['name'] = ox_access + "_mobility_migrated"
                    oxaccess_profile['displayName'] = oxaccess_profile['name']
                    try:
                        oxaccess_profile.create()
                        print("Creating Access profile {} with mobility enabled from {}".format(
                            ox_access + "_mobility_migrated", ox_access))
                    except univention.admin.uexceptions.objectExists:
                        pass

                user['oxAccess'] = ox_access + "_mobility_migrated"
            user.modify()
            print("Changed access profile for {}".format(user.dn))


parser = ArgumentParser()
parser.add_argument('--write', action='store_true',
                    help='Write the current state of the user display names')
parser.add_argument('--apply', action='store_true',
                    help='Apply a previously written state to the users')
parser.add_argument(
    '--file', help='Filename where the state is written to or read from')
parser.add_argument('--binddn', help='Bind DN for LDAP connection')
parser.add_argument(
    '--bindpwdfile', help='Filename where the LDAP password is stored in')
args = parser.parse_args()

master = ucr.get('ldap/master')
port = ucr.get('ldap/master/port')
base = ucr.get('ldap/base')

if args.binddn:
    lo = univention.admin.uldap.access(
        master, port, base, args.binddn, open(args.bindpwdfile).read())
    pos = univention.admin.uldap.position(base)
else:
    lo, pos = univention.admin.uldap.getAdminConnection()

if args.write:
    write_it(lo, pos, args.file)
if args.apply:
    apply_it(lo, pos, args.file)
