# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for resources objects
#
# Copyright (C) 2004-2021 Univention GmbH
#
# https://www.univention.de/
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

from ldap.filter import filter_format

import univention.debug as ud
import univention.admin.filter
import univention.admin.handlers
import univention.admin.uexceptions
import univention.admin.allocators
import univention.admin.localization
import univention.admin.uldap
from univention.admin.layout import Tab, Group


translation = univention.admin.localization.translation('univention.admin.handlers.oxresources.oxresources')
_ = translation.translate

module = 'oxresources/oxresources'
childs = False
short_description = _('Open-Xchange: Resource')
long_description = ''
operations = ['add', 'edit', 'remove', 'search', 'move']
default_containers = ["cn=oxresources,cn=open-xchange"]

ldap_search_oxuser = univention.admin.syntax.LDAP_Search(  # FIXME/TODO: move to syntax.d otherwise it's not usable in UMC
        filter='(&(objectClass=oxUserObject)(isOxUser=OK))',
        attribute=['users/user: uid'],
        value='users/user: uidNumber')

options = {
        'default': univention.admin.option(
                short_description=short_description,
                default=True,
                objectClasses=['top', 'oxResourceObject'],
        )
}

property_descriptions = {
        'name': univention.admin.property(
                short_description=_('Name'),
                long_description=_('Internal name of resource'),
                syntax=univention.admin.syntax.string_numbers_letters_dots_spaces,
                required=True,
                may_change=False,
                identifies=True
        ),
        'description': univention.admin.property(
                short_description=_('Description'),
                long_description=_('Description for resource object'),
                syntax=univention.admin.syntax.string,
        ),
        'displayname': univention.admin.property(
                short_description=_('Display Name'),
                long_description=_('Name of resource that will be shown in Open-Xchange'),
                syntax=univention.admin.syntax.string,
                required=True,
                default='<name>'
        ),
        'resourceadmin': univention.admin.property(
                short_description=_('Resource manager'),
                long_description=_('User who will manage this resource'),
                syntax=ldap_search_oxuser,
                required=True,
        ),
        'resourceMailAddress': univention.admin.property(
                short_description=_('Resource e-mail address'),
                long_description=_('Unique e-mail adress that will be assigned to this resource'),
                syntax=univention.admin.syntax.emailAddress,
                required=True,
        ),
}


layout = [
        Tab(_('General'), _('General settings'), layout=[
                Group(_('General'), layout=[
                        ['name', 'displayname'],
                        ['resourceadmin', 'description'],
                        ['resourceMailAddress']
                ]),
        ]),
]

mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('description', 'description', None, univention.admin.mapping.ListToString)
mapping.register('displayname', 'displayName', None, univention.admin.mapping.ListToString)
mapping.register('resourceadmin', 'oxResourceAdmin', None, univention.admin.mapping.ListToString)
mapping.register('resourceMailAddress', 'mailPrimaryAddress', None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
    module = module

    def _addMailAddressToResourceAdmin(self):
        # Find user object(s) where oxResourceMailAddress should be added
        # The filter tests for (!(oxResourceMailAddress=%s)) to avoid duplicate entries in case of existing inconsitency.
        searchResult = self.lo.searchDn(filter=filter_format('(&(objectClass=oxUserObject)(uidNumber=%s)(isOxUser=OK)(!(oxResourceMailAddress=%s)))', (self['resourceadmin'], self['resourceMailAddress'])))
        for userDn in searchResult:
            ud.debug(ud.ADMIN, ud.INFO, "Adding oxResourceMailAddress %s to %s" % (self['resourceMailAddress'], userDn))
            self.lo.modify(userDn, [('oxResourceMailAddress', [], [self['resourceMailAddress'].encode('utf-8')])])

    def _removeMailAddressesFromResourceAdmins(self):
        # Find user object(s) where OLD oxResourceMailAddress is set and ...
        if not self.oldinfo.get('resourceMailAddress'):
            return
        searchResult = self.lo.searchDn(filter=filter_format('(&(objectClass=oxUserObject)(isOxUser=OK)(oxResourceMailAddress=%s))', (self.oldinfo.get('resourceMailAddress'),)))
        for userDn in searchResult:
            # ... remove it from user object
            ud.debug(ud.ADMIN, ud.INFO, "Removing oxResourceMailAddress %s from %s" % (self.oldinfo.get('resourceMailAddress'), userDn))
            self.lo.modify(userDn, [('oxResourceMailAddress', [self.oldinfo.get('resourceMailAddress').encode('utf-8')], [])])

    def _ldap_addlist(self):
        # try to allocate unique mail address for the new resource
        try:
            self.alloc.append(('mailPrimaryAddress', self['resourceMailAddress']))
            univention.admin.allocators.request(self.lo, self.position, 'mailPrimaryAddress', value=self['resourceMailAddress'])
        except univention.admin.uexceptions.noLock:
            ud.debug(ud.ADMIN, ud.WARN, "Allocation of resourceMailAddress %s failed in addlist" % self['resourceMailAddress'])
            self.cancel()
            raise univention.admin.uexceptions.mailAddressUsed()
        return super(object, self)._ldap_addlist()

    def _check_mailaddress(self):
        domain = self['resourceMailAddress'].rsplit('@')[-1]
        filter = filter_format('(&(objectClass=univentionMailDomainname)(cn=%s))', (domain,))
        result = self.lo.search(filter=filter)
        if not result:
            raise univention.admin.uexceptions.valueError(_("The mail address' domain does not match any mail domain object."))

    def _ldap_pre_create(self):
        super(object, self)._ldap_pre_create()
        self._check_mailaddress()

    def _ldap_post_create(self):
        super(object, self)._ldap_post_create()
        self._addMailAddressToResourceAdmin()
        # confirm allocated resourceMailAddress
        univention.admin.allocators.confirm(self.lo, self.position, 'mailPrimaryAddress', self['resourceMailAddress'])

    def _ldap_modlist(self):
        ml = super(object, self)._ldap_modlist()

        # try to allocate unique mail address for the new resource if adress has been changed by user
        if self.hasChanged('resourceMailAddress'):
            for i, _ in self.alloc:
                if i == 'mailPrimaryAddress':
                    break
            else:
                try:
                    self.alloc.append(('mailPrimaryAddress', self['resourceMailAddress']))
                    univention.admin.allocators.request(self.lo, self.position, 'mailPrimaryAddress', value=self['resourceMailAddress'])
                except univention.admin.uexceptions.noLock:
                    ud.debug(ud.ADMIN, ud.WARN, "Allocation of resourceMailAddress %s failed in modlist" % self['resourceMailAddress'])
                    self.cancel()
                    raise univention.admin.uexceptions.mailAddressUsed()

        return ml

    def _ldap_pre_modify(self):
        super(object, self)._ldap_pre_modify()
        if self.hasChanged('mailPrimaryAddress'):
            self._check_mailaddress()

    def _ldap_post_modify(self):
        super(object, self)._ldap_post_modify()
        if self.hasChanged('resourceMailAddress') or self.hasChanged('resourceadmin'):
            self._removeMailAddressesFromResourceAdmins()
            self._addMailAddressToResourceAdmin()

        if self.hasChanged('resourceMailAddress'):
            if self['resourceMailAddress']:
                univention.admin.allocators.confirm(self.lo, self.position, 'mailPrimaryAddress', self['resourceMailAddress'])
            else:
                univention.admin.allocators.release(self.lo, self.position, 'mailPrimaryAddress', self.oldinfo['resourceMailAddress'])

    def _ldap_post_remove(self):
        super(object, self)._ldap_post_remove()
        self._removeMailAddressesFromResourceAdmins()


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
