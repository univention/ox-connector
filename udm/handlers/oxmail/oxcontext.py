# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for the mail domain objects
#
# Copyright (C) 2004-2021 Univention GmbH <https://www.univention.de/>
# and
#     iKu Systems & Services GmbH & Co. KG (https://www.iku-systems.de/)
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
# <https://www.gnu.org/licenses/>.

import ldap.filter
import univention.admin.handlers
import univention.admin.allocators
import univention.admin.localization
from univention.admin.layout import Tab, Group

translation = univention.admin.localization.translation('univention.admin.handlers.oxmail.oxcontext')
_ = translation.translate

module = 'oxmail/oxcontext'
operations = ['add', 'edit', 'remove', 'search', 'move']
default_containers = ['cn=open-xchange']

childs = False
short_description = _('OX Mail: OX context')
long_description = ''

options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'oxContext'],
    ),
}

property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Name'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
        required=True,
        may_change=False,
        identifies=True,
    ),
    'contextid': univention.admin.property(
        short_description=_('Context ID'),
        long_description='',
        syntax=univention.admin.syntax.integer,
        required=True,
        may_change=False,
    ),
    'oxQuota': univention.admin.property(
        short_description=_('Quota [MBytes]'),
        long_description='',
        syntax=univention.admin.syntax.integer,
    ),
}

layout = [
    Tab(_('General'), _('Basic Values'), layout=[
        Group(_('General'), layout=[
            'name',
            'contextid',
            'oxQuota',
        ]),
    ]),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('contextid', 'oxContextIDNum', None, univention.admin.mapping.ListToString)
mapping.register('oxQuota', 'oxQuota', None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
    module = module

    def _ldap_pre_remove(self):
        super(object, self)._ldap_pre_remove()

        # refuse deletion of context object if it is the only one
        searchResult = lookup(None, self.lo, None)
        if len(searchResult) <= 1:
            raise univention.admin.uexceptions.valueError(_('The deletion of the OX context object is not allowed!'))

        # refuse deletion of context object if users still exist
        user_filter = ldap.filter.filter_format('oxContext=%s', [str(self['contextid'])])
        searchResult = univention.admin.modules.lookup('users/user', None, self.lo, user_filter, scope='sub')
        if len(searchResult) >= 1:
            raise univention.admin.uexceptions.valueError(_('The deletion of the OX context object is not allowed as long as users are in it'))

        # refuse deletion of context object if users still exist
        resource_filter = ldap.filter.filter_format('oxContext=%s', [str(self['contextid'])])
        searchResult = univention.admin.modules.lookup('oxresources/oxresources', None, self.lo, resource_filter, scope='sub')
        if len(searchResult) >= 1:
            raise univention.admin.uexceptions.valueError(_('The deletion of the OX context object is not allowed as long as resources are in it'))


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
