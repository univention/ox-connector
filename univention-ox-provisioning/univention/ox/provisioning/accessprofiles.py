# -*- coding: utf-8 -*-
#
# Copyright 2020 Univention GmbH
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


import logging
import re
from collections import OrderedDict
from copy import deepcopy
from pathlib import Path

logger = logging.getLogger("listener")


base_dir = Path("/var/lib/univention-appcenter/apps/")
data_dir = base_dir / "ox-connector" / "data"
access_definitions_file = data_dir / "ModuleAccessDefinitions.properties"


def empty_rights_profile():
    return {access: False for access in capability_map.values()}


def create_accessprofile(obj):
    logger.info("Adding an accessprofile is like modifying it...")
    modify_accessprofile(obj)


def modify_accessprofile(obj):
    logger.info(f"Changing accessprofile {obj.distinguished_name}")
    profiles = get_access_profiles(force_reload=False)
    rights = []
    for key, value in capability_map.items():
        if obj.attributes.get(key) == "TRUE":
            rights.append(value)
    profiles[obj.attributes["name"]] = rights
    save_accessprofiles(profiles)
    get_access_profiles(force_reload=True)


def delete_accessprofile(obj):
    logger.info(f"Removing accessprofile {obj.distinguished_name}")
    profiles = get_access_profiles(force_reload=False)
    profiles.pop(obj.old_attributes["name"], None)
    save_accessprofiles(profiles)
    get_access_profiles(force_reload=True)


def save_accessprofiles(profiles):
    reverse_capability_map = {value: key for key, value in capability_map.items()}
    with open(access_definitions_file, "w") as fd:
        fd.write("# This file is generated by the ox-connector App automatically.\n")
        fd.write("# It is controlled by the UDM module oxmail/accessprofile\n\n")
        for name, rights in profiles.items():
            rights = [reverse_capability_map.get(right, right) for right in rights]
            fd.write(f"{name}={','.join(sorted(rights))}\n\n")


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
                        capabilities = {x.strip() for x in match.groups()[1].split(",")}
                        _profiles[name] = [
                            capability_map.get(cap, cap) for cap in capabilities
                        ]
        except EnvironmentError:
            logger.warning(
                "Could not read %s. Working with empty set...", access_definitions_file,
            )
    return deepcopy(_profiles)


def get_access_profile(profile_name):
    return get_access_profiles(force_reload=False).get(profile_name)
