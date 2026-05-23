#
# Univention Admin Modules
#  admin module for the mail domain objects
#
# Copyright (C) 2004-2020 Univention GmbH <http://www.univention.de/>
# and
#     iKu Systems & Services GmbH & Co. KG (http://www.iku-systems.de/)
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

import univention.admin.allocators
import univention.admin.filter
import univention.admin.handlers
import univention.admin.localization
from univention.admin.layout import Group, Tab

translation = univention.admin.localization.translation(
    "univention.admin.handlers.oxmail.shared_account_permission",
)
_ = translation.translate

module = "oxmail/shared_account_permission"
operations = ["add", "edit", "remove", "search"]
default_containers = ["cn=shared_account_permissions,cn=open-xchange"]

childs = False
short_description = _("OX Mail: Shared Account Permission")
long_description = ""

options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'oxSharedAccountPermission'],
    ),
}

property_descriptions = {
    "name": univention.admin.property(
        short_description=_("Name"),
        long_description="",
        syntax=univention.admin.syntax.uid,
        include_in_default_search=True,
        multivalue=False,
        required=True,
        may_change=True,
        identifies=True,
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
    "mail": univention.admin.property(
        short_description=_("Mail"),
        long_description="",
        syntax=univention.admin.syntax.oxDeputyPermissionTalking,
        multivalue=False,
        required=False,
        may_change=True,
        identifies=False,
    ),
    "calendar": univention.admin.property(
        short_description=_("Calendar"),
        long_description="",
        syntax=univention.admin.syntax.oxDeputyPermissionTalking,
        multivalue=False,
        required=False,
        may_change=True,
        identifies=False,
    ),
    "sendAs": univention.admin.property(
        short_description="sendAs",
        long_description=_(
            "Send emails directly as the shared account entity / Impersonate as shared account entity during scheduling operations in the account",
        ),
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=True,
        identifies=False,
    ),
    "sendOnBehalf": univention.admin.property(
        short_description="sendOnBehalf",
        long_description=_(
            "Send emails on behalf of the shared account entity / Act on behalf of the shared account entity during scheduling operations in the account",
        ),
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=True,
        identifies=False,
    ),
    "snippets": univention.admin.property(
        short_description="snippets",
        long_description=_(
            "Read-only access to shared account snippets from module io.ox/mail",
        ),
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=True,
        identifies=False,
    ),
    "writeSnippets": univention.admin.property(
        short_description="writeSnippets",
        long_description=_(
            "Read/write access to shared account snippets from module io.ox/mail (e.g. signatures)",
        ),
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=True,
        identifies=False,
    ),
    "manageSieve": univention.admin.property(
        short_description="manageSieve",
        long_description=_(
            "Manage mail filter rules for the shared account, i.e. its Sieve scripts",
        ),
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=True,
        identifies=False,
    ),
    "writeJSlob": univention.admin.property(
        short_description="writeJSlob",
        long_description=_(
            "Write access to specific JSlob data from the shared account (e.g. for changing shared configuration)",
        ),
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=True,
        identifies=False,
    ),
}

layout = [
    Tab(
        _("General"),
        _("Basic Values"),
        layout=[
            Group(_("General"), layout=["name", "displayName"]),
            Group(
                _("Permissions"),
                layout=[
                    "mail",
                    "calendar",
                ],
            ),
            Group(
                _("Capabilities"),
                layout=[
                    ["sendAs", "sendOnBehalf"],
                    ["snippets", "writeSnippets"],
                    ["manageSieve", "writeJSlob"],
                ],
            ),
        ],
    ),
]

mapping = univention.admin.mapping.mapping()
mapping.register("name", "cn", None, univention.admin.mapping.ListToString)
mapping.register(
    "displayName",
    "displayName",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "mail",
    "oxPermissionMail",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "calendar",
    "oxPermissionCalendar",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "sendAs",
    "oxSendAs",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "sendOnBehalf",
    "oxSendOnBehalf",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "snippets",
    "oxSnippets",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "writeSnippets",
    "oxWriteSnippets",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "manageSieve",
    "oxManageSieve",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "writeJSlob",
    "oxWriteJSlob",
    None,
    univention.admin.mapping.ListToString,
)


class object(univention.admin.handlers.simpleLdap):
    module = module

    def _ldap_pre_remove(self):
        super(object, self)._ldap_pre_remove()
        univention.admin.modules.update()

        access_filter = univention.admin.filter.expression(
            "oxLinkUsers",
            "* with %s" % self["univentionObjectIdentifier"],
        )
        searchResultUsers = univention.admin.modules.lookup(
            "oxmail/shared_account",
            self.co,
            self.lo,
            access_filter,
            scope="sub",
        )

        access_filter = univention.admin.filter.expression(
            "oxLinkGroups",
            "* with %s" % self["univentionObjectIdentifier"],
        )
        searchResultGroups = univention.admin.modules.lookup(
            "oxmail/shared_account",
            self.co,
            self.lo,
            access_filter,
            scope="sub",
        )

        if searchResultUsers or searchResultGroups:
            raise univention.admin.uexceptions.valueError(
                _(
                    "The deletion of the Shared Account Permission object is not allowed as long as any Shared Account references it",
                ),
            )


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
