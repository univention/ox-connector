#
#
# Univention Admin Modules
#  hook definitions
#
# Copyright (C) 2025 Univention GmbH
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
from ldap.dn import str2dn, dn2str
from ldap.filter import filter_format

import univention.debug as ud
import univention.admin.modules
import univention.admin.uexceptions
import univention.admin.localization
import univention.uldap
from univention.config_registry import ConfigRegistry
from univention.admin.hook import simpleHook

translation = univention.admin.localization.translation(
    "univention.admin.hooks.oxDeputyPermissionHook",
)
_ = translation.translate

ucr = ConfigRegistry()
ucr.load()

DEFAULT_CONTEXT = ucr.get('ox/context/id')


class oxDeputyPermissionHook(simpleHook):
    type = "oxDeputyPermissionHook"

    def _get_user(self, lo, dn):
        """Returns the user with the given DN"""
        try:
            user = univention.admin.handlers.users.user.lookup(
                None,
                lo,
                filter_s='',
                base=dn,
            )[0]
            user.open()
            return user
        except univention.admin.uexceptions.noObject:
            # base=dn raises an error
            return None

    def hook_open(self, obj):
        """Split entries for correct representation in UMC"""
        attrs = ["oxDeputyPermissionGivenTo"]
        for attr in attrs:
            if obj.info.get(attr):
                new = [
                    entry.split(" |:$:| ") for entry in obj.info.get(attr, [])
                ]
                obj.info[attr] = new
                new = [
                    entry.split(" |:$:| ")
                    for entry in obj.oldinfo.get(attr, [])
                ]
                obj.oldinfo[attr] = new

    def hook_ldap_pre_create(self, obj):
        # FIXME: Bug #57709
        old = obj.info.get("oxDeputyPermissionGivenTo", [])
        new = [u' |:$:| '.join(entry) for entry in old]
        obj.info['oxDeputyPermissionGivenTo'] = new

        self.validate_user(obj)

    def hook_ldap_pre_modify(self, obj):
        """
        Remove all permissions from obj and all referencing permissions to this obj on other users if:
        - user becomes isOxUser=Not
        - user changes the context
        OX itself deletes the permissions in these cases, but we have to know this in LDAP too.
        """
        # FIXME: Bug #57709
        old = obj.oldinfo.get("oxDeputyPermissionGivenTo", [])
        new = [u' |:$:| '.join(entry) for entry in old]
        obj.oldinfo['oxDeputyPermissionGivenTo'] = new
        old = obj.info.get("oxDeputyPermissionGivenTo", [])
        new = [u' |:$:| '.join(entry) for entry in old]
        obj.info['oxDeputyPermissionGivenTo'] = new

        if obj.hasChanged("isOxUser"):
            if obj.info.get("isOxUser", "Not") == "OK":
                # do not clear deputies if user becomes enabled
                pass
            else:
                # clear all deputies if user will be disabled for OX
                ud.debug(
                    ud.ADMIN,
                    ud.INFO,
                    "oxDeputyPermissionHook: clear all permissions because user will get isOxUser=Not",
                )
                obj.info['oxDeputyPermissionGivenTo'] = []
                self.clear_referencing_deputies(obj)
        if obj.hasChanged("oxContext"):
            # clear all deputies
            ud.debug(
                ud.ADMIN,
                ud.INFO,
                "oxDeputyPermissionHook: clear all permissions because users context changed",
            )
            self.clear_referencing_deputies(obj)
        if obj.info.get("_no_validate_user_in_ox_deputy_permission_hook"):
            del obj.info["_no_validate_user_in_ox_deputy_permission_hook"]
            return

        self.validate_user(obj)

    def hook_ldap_post_modify(self, obj):
        if not isinstance(obj, univention.admin.handlers.users.user.object):
            return
        if obj.lo.compare_dn(obj.old_dn.lower(), obj.dn.lower()):
            return
        search_for_dn = dn2str(str2dn(obj.old_dn))
        user_dn = obj.lo.searchDn(
            filter_format(
                'oxDeputyPermissionGivenTo=%s |:$:| *',
                [search_for_dn],
            ),
        )
        for user in user_dn:
            user = self._get_user(obj.lo, user)
            if not user:
                continue
            oxDeputyPermissionGivenTo = []
            for entry in user.info.get("oxDeputyPermissionGivenTo", []):
                if obj.lo.compare_dn(entry[0].lower(), obj.old_dn.lower()):
                    oxDeputyPermissionGivenTo.append([obj.dn] + entry[1:])
                else:
                    oxDeputyPermissionGivenTo.append(entry)
            user.info["oxDeputyPermissionGivenTo"] = oxDeputyPermissionGivenTo
            user.info["_no_validate_user_in_ox_deputy_permission_hook"] = True
            user.modify(ignore_license=True)

    def hook_ldap_pre_move(self, obj):
        # FIXME: Bug #57709
        old = obj.info.get("oxDeputyPermissionGivenTo", [])
        new = [u' |:$:| '.join(entry) for entry in old]
        obj.info['oxDeputyPermissionGivenTo'] = new

        # i think this is not needed. but _maybe_ a second, yet unknown
        # ldap_pre_move hook would set the oxContext based on the container or
        # so? although... how would the hook ensure it runs first?
        # self.validate_user(obj)

    def hook_ldap_post_move(self, obj):
        self.hook_ldap_post_modify(obj)

    def hook_ldap_post_remove(self, obj):
        self.clear_referencing_deputies(obj)

    def validate_user(self, obj):
        """
        prevent:
        - setting two deputy permisisons for the same user <-> objects
        - setting deputy permission for oneself
        - setting deputy permission for users in different oxContext
        """
        if not isinstance(obj, univention.admin.handlers.users.user.object):
            return
        entries = [
            x.split(" |:$:| ")
            for x in obj.info.get("oxDeputyPermissionGivenTo", [])
        ]
        user_dns = set(entry[0] for entry in entries)
        if len(user_dns) != len(entries):
            raise univention.admin.uexceptions.valueError(
                _(
                    "The permission can only be granted once between the same accounts.",
                ),
            )
        for entry in entries:
            user_dn = entry[0]
            if obj.lo.compare_dn(user_dn.lower(), obj.dn.lower()):
                raise univention.admin.uexceptions.valueError(
                    _(
                        "The deputy permission cannot be granted for the same object.",
                    ),
                )
            user = self._get_user(obj.lo, user_dn)
            if not user:
                continue
            user_ox_context = user["oxContext"]
            obj_ox_context = obj["oxContext"]
            if str(user_ox_context) != str(obj_ox_context):
                raise univention.admin.uexceptions.valueError(
                    _(
                        "Deputy permissions can only be granted for users in the same OX context.",
                    ),
                )

    def clear_referencing_deputies(self, obj):
        """Search all users with deputy permission regarding obj and remove this entry"""
        if not isinstance(obj, univention.admin.handlers.users.user.object):
            return
        user_dn = obj.lo.searchDn(
            filter_format('oxDeputyPermissionGivenTo=%s |:$:| *', [obj.dn]),
        )
        for dn in user_dn:
            user = self._get_user(obj.lo, dn)
            if not user:
                continue
            oxDeputyPermissionGivenTo = []
            for entry in user.info.get("oxDeputyPermissionGivenTo", []):
                if obj.lo.compare_dn(entry[0].lower(), obj.old_dn.lower()):
                    pass
                else:
                    oxDeputyPermissionGivenTo.append(entry)
            user.info["oxDeputyPermissionGivenTo"] = oxDeputyPermissionGivenTo
            user.modify(ignore_license=True)
