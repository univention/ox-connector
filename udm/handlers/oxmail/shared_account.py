#
# Univention Admin Modules
#  admin module for the shared account objects
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
    'univention.admin.handlers.oxmail.shared_account',
)
_ = translation.translate

module = 'oxmail/shared_account'
operations = ['add', 'edit', 'remove', 'search', 'move']
default_containers = ["cn=shared_accounts,cn=open-xchange"]

childs = False
short_description = _("OX Mail: Shared Account")
long_description = ''

options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'oxSharedAccount'],
    ),
}

property_descriptions = {
    'name': univention.admin.property(
        short_description=_('Name'),
        long_description='',
        syntax=univention.admin.syntax.uid_umlauts,
        include_in_default_search=1,
        multivalue=0,
        required=1,
        may_change=1,
        identifies=1,
    ),
    "displayName": univention.admin.property(
        short_description=_("Display name"),
        long_description="",
        syntax=univention.admin.syntax.string,
        multivalue=False,
        required=True,
        may_change=True,
        identifies=False,
    ),
    'oxContext': univention.admin.property(
        short_description=_('Context ID'),
        long_description='',
        syntax=univention.admin.syntax.oxContextSelect,
        required=True,
        may_change=False,
    ),
    'mailPrimaryAddress': univention.admin.property(
        short_description=_('Primary e-mail address'),
        long_description='',
        syntax=univention.admin.syntax.primaryEmailAddressValidDomain,
        include_in_default_search=1,
        may_change=1,
        required=1,
    ),
    'users': univention.admin.property(
        short_description=_('Users'),
        long_description='',
        syntax=univention.admin.syntax.oxSharedAccountLinkUser,
        multivalue=True,
        copyable=True,
    ),
    'groups': univention.admin.property(
        short_description=_('Groups'),
        long_description='',
        syntax=univention.admin.syntax.oxSharedAccountLinkGroup,
        multivalue=True,
        copyable=True,
    ),
}

layout = [
    Tab(
        _('General'),
        _('Shared Account settings'),
        layout=[
            Group(
                _('General'),
                layout=[
                    'name',
                    'displayName',
                    'mailPrimaryAddress',
                    'oxContext',
                ],
            ),
            Group(
                _('Access Rights'),
                layout=[
                    'users',
                    'groups',
                ],
            ),
        ],
    ),
]


def mapKeyAndValue(old, encoding=()):
    """
    Map (["UOI", "UOI"]) list to ("UOI with UOI") list.
    """
    return [' with '.join(entry).encode(*encoding) for entry in old]


def unmapKeyAndValue(old, encoding=()):
    """
    Unmap ("UOI with UOI") list to (["UOI", "UOI"]) list.
    """
    return [entry.decode(*encoding).split(' with ', 1) for entry in old]


mapping = univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register(
    "displayName",
    "displayName",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    'mailPrimaryAddress',
    'mailPrimaryAddress',
    None,
    univention.admin.mapping.ListToLowerString,
)
mapping.register(
    'users',
    'oxLinkUsers',
    mapKeyAndValue,
    unmapKeyAndValue,
)
mapping.register(
    'groups',
    'oxLinkGroups',
    mapKeyAndValue,
    unmapKeyAndValue,
)
mapping.register(
    'oxContext',
    'oxContextIDNum',
    None,
    univention.admin.mapping.ListToString,
)


class object(univention.admin.handlers.simpleLdap):
    module = module
    default_containers_attribute_name = 'ox_shared_accounts'

    def _ldap_pre_create(self):
        if self.has_uoid_duplicates('users'):
            raise univention.admin.uexceptions.valueError(
                _(
                    "A user must not be repeated in the Shared Account",
                ),
            )

        if self.has_uoid_duplicates('groups'):
            raise univention.admin.uexceptions.valueError(
                _(
                    "A group must not be repeated in the Shared Account",
                ),
            )
        super(object, self)._ldap_pre_create()

    def _ldap_pre_modify(self):
        super(object, self)._ldap_pre_modify()

        if self.has_uoid_duplicates('users'):
            raise univention.admin.uexceptions.valueError(
                _(
                    "A user must not be repeated in the Shared Account",
                ),
            )

        if self.has_uoid_duplicates('groups'):
            raise univention.admin.uexceptions.valueError(
                _(
                    "A group must not be repeated in the Shared Account",
                ),
            )

    def _ldap_pre_ready(self):
        # get lock for mailPrimaryAddress
        if not self.exists() or self.hasChanged('mailPrimaryAddress'):
            # ignore case in change of mailPrimaryAddress, we only store the lowercase address anyway
            if (
                self['mailPrimaryAddress']
                and self['mailPrimaryAddress'].lower()
                != (self.oldinfo.get('mailPrimaryAddress', None) or '').lower()
            ):
                try:
                    self.alloc.append(
                        (
                            'mailPrimaryAddress',
                            univention.admin.allocators.request(
                                self.lo,
                                self.position,
                                'mailPrimaryAddress',
                                value=self['mailPrimaryAddress'],
                            ),
                        ),
                    )
                except univention.admin.uexceptions.noLock:
                    raise univention.admin.uexceptions.mailAddressUsed(
                        self['mailPrimaryAddress'],
                    )

    def has_uoid_duplicates(self, obj_property):
        """
        This function checks for duplicate uoids in a UDM property.
        This is used to check that no user/group is added twice to the shared account.
        """

        if self.hasChanged(obj_property):
            linked_uoid = [
                linked_entry[0]
                for linked_entry in self.info.get(obj_property, [])
            ]

            return len(linked_uoid) != len(set(linked_uoid))
        else:
            return False


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
