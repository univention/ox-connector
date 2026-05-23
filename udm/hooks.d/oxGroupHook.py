#
# Univention Admin Modules
#  hook definitions
#
# Copyright (C) 2004-2025 Univention GmbH
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
from ldap.filter import filter_format

import univention.debug
import univention.admin.modules
import univention.admin.uexceptions
import univention.admin.localization
import univention.uldap
from univention.admin.hook import simpleHook

translation = univention.admin.localization.translation(
    'univention.admin.hooks.oxGroupHook',
)
_ = translation.translate


class oxGroupHook(simpleHook):
    type = 'oxGroupHook'

    @staticmethod
    def log_info(msg):
        univention.debug.debug(
            univention.debug.ADMIN,
            univention.debug.INFO,
            'oxGroupHook: %s' % msg,
        )

    @staticmethod
    def check_mailaddr(module):
        if module['mailAddress']:
            domain = module['mailAddress'].rsplit('@')[-1]
            filter_s = filter_format(
                '(&(objectClass=univentionMailDomainname)(cn=%s))',
                (domain,),
            )
            result = module.lo.searchDn(filter=filter_s)

            if not result:
                raise univention.admin.uexceptions.valueError(
                    _(
                        "The mail address' domain does not match any mail domain object.",
                    ),
                )
            else:
                oxGroupHook.log_info('ldap result: %s' % result)

    def hook_ldap_pre_create(self, module):
        self.log_info('_ldap_pre_create called')
        self.check_mailaddr(module)

    def hook_ldap_pre_modify(self, module):
        self.log_info('_ldap_pre_modify called')
        self.check_mailaddr(module)

    def hook_ldap_post_remove(self, obj):
        self.clear_referencing_deputies(obj)

    def clear_referencing_deputies(self, obj):
        """Search all shared accounts with permissions regarding obj and remove this entry"""
        if not isinstance(obj, univention.admin.handlers.groups.group.object):
            return

        access_filter = univention.admin.filter.expression(
            'oxLinkGroups',
            '%s with *' % obj["univentionObjectIdentifier"],
        )
        searchResultGroups = (
            univention.admin.handlers.oxmail.shared_account.lookup(
                None,
                obj.lo,
                access_filter,
                scope="sub",
            )
        )

        for entry in searchResultGroups:
            entry.open()
            linkedGroups = entry.get("groups")

            new_linkedGroups = [
                linkedGroup
                for linkedGroup in linkedGroups
                if linkedGroup[0] != obj["univentionObjectIdentifier"]
            ]
            if new_linkedGroups != linkedGroups:
                entry["groups"] = new_linkedGroups
                entry.modify(ignore_license=True)
