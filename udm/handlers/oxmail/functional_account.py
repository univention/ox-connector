# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for the functional account objects
#
# Copyright (C) 2021 Univention GmbH <http://www.univention.de/>
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

import univention.admin.filter
import univention.admin.handlers
import univention.admin.allocators
import univention.admin.localization
import univention.admin.uexceptions
from univention.admin.layout import Tab, Group

translation = univention.admin.localization.translation(
    'univention.admin.handlers.oxmail.functional_account')
_ = translation.translate

module = 'oxmail/functional_account'
operations = ['add', 'edit', 'remove', 'search', 'move']
default_containers = ["cn=functional_accounts,cn=open-xchange"]

childs = False
short_description = _('OX Mail: Functional Mailbox')
long_description = ''

options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'oxFunctionalAccount'],
    )
}

property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Name'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=1,
        multivalue=0,
        required=1,
        may_change=0,
        identifies=1
    ),
    'mailPrimaryAddress': univention.admin.property(
        short_description=_('Primary e-mail address'),
        long_description='',
        syntax=univention.admin.syntax.primaryEmailAddressValidDomain,
        include_in_default_search=1,
        may_change=0,
        required=1,
    ),
    'oxQuota': univention.admin.property(
        short_description=_('Quota [MBytes]'),
        long_description='',
        syntax=univention.admin.syntax.integer,
        multivalue=0,
        required=0,
        may_change=1,
        identifies=0
    ),
    'personal': univention.admin.property(
        short_description=_('Personal'),
        long_description='',
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
    ),
    'users': univention.admin.property(
        short_description=_('Users'),
        long_description='',
        syntax=univention.admin.syntax.UserDN,
        multivalue=True,
        copyable=True,
    ),
    'groups': univention.admin.property(
        short_description=_('Groups'),
        long_description='',
        syntax=univention.admin.syntax.GroupDN,
        multivalue=True,
    ),
}

layout = [
    Tab(_('General'), _('Functional Account settings'), layout=[
        Group(_('General'), layout=[
            'name',
            'mailPrimaryAddress',
            'oxQuota',
            'personal',
        ]),
        Group(_('Access Rights'), layout=[
            'users',
            # 'groups',
        ]),
    ]),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('mailPrimaryAddress', 'mailPrimaryAddress',
                 None, univention.admin.mapping.ListToLowerString)
mapping.register('oxQuota', 'oxQuota', None,
                 univention.admin.mapping.ListToString)
mapping.register('personal', 'oxPersonal', None,
                 univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
    module = module

    def open(self):
        super(object, self).open()
        self['users'] = []
        self['groups'] = []
        if self.exists():
            for member in self.oldattr.get('uniqueMember', []):
                if member.startswith(b'uid='):
                    self['users'].append(member.decode('utf-8'))
                else:
                    self['groups'].append(member.decode('utf-8'))
            self.save()

    def _ldap_modlist(self):
        ml = super(object, self)._ldap_modlist()
        new_members = [member.encode('utf-8')
                       for member in self['users'] + self['groups']]
        ml.append(('uniqueMember', self.oldattr.get(
            'uniqueMember', []), new_members))
        return ml

    def _ldap_pre_ready(self):
        # get lock for mailPrimaryAddress
        if not self.exists() or self.hasChanged('mailPrimaryAddress'):
            # ignore case in change of mailPrimaryAddress, we only store the lowercase address anyway
            if self['mailPrimaryAddress'] and self['mailPrimaryAddress'].lower() != (self.oldinfo.get('mailPrimaryAddress', None) or '').lower():
                try:
                    self.alloc.append(('mailPrimaryAddress', univention.admin.allocators.request(
                        self.lo, self.position, 'mailPrimaryAddress', value=self['mailPrimaryAddress'])))
                except univention.admin.uexceptions.noLock:
                    raise univention.admin.uexceptions.mailAddressUsed(
                        self['mailPrimaryAddress'])


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
