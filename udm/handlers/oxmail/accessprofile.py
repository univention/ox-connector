# -*- coding: utf-8 -*-
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
    "univention.admin.handlers.oxmail.accessprofile"
)
_ = translation.translate

module = "oxmail/accessprofile"
operations = ["add", "edit", "remove", "search"]
default_containers = ["cn=accessprofiles,cn=open-xchange"]

childs = False
short_description = _("OX Mail: OX access profile")
long_description = ""

options = {
    'default': univention.admin.option(
        short_description=short_description,
        default=True,
        objectClasses=['top', 'oxAccessProfile'],
    )
}

property_descriptions = {
    "name": univention.admin.property(
        short_description=_("Name"),
        long_description="",
        syntax=univention.admin.syntax.string,
        include_in_default_search=True,
        multivalue=False,
        required=True,
        may_change=False,
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
    "usm": univention.admin.property(
        short_description=_("USM"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "activesync": univention.admin.property(
        short_description=_("activeSync"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "calendar": univention.admin.property(
        short_description=_("calendar"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "collectemailaddresses": univention.admin.property(
        short_description=_("collectEmailAddresses"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "contacts": univention.admin.property(
        short_description=_("contacts"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "delegatetask": univention.admin.property(
        short_description=_("delegateTask"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "deniedportal": univention.admin.property(
        short_description=_("deniedPortal"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "editgroup": univention.admin.property(
        short_description=_("editGroup"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "editpassword": univention.admin.property(
        short_description=_("editPassword"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "editpublicfolders": univention.admin.property(
        short_description=_("editPublicFolders"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "editresource": univention.admin.property(
        short_description=_("editResource"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "globaladdressbookdisabled": univention.admin.property(
        short_description=_("globalAddressBookDisabled"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "ical": univention.admin.property(
        short_description=_("ical"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "infostore": univention.admin.property(
        short_description=_("infostore"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "multiplemailaccounts": univention.admin.property(
        short_description=_("multipleMailAccounts"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "publicfoldereditable": univention.admin.property(
        short_description=_("publicFolderEditable"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "readcreatesharedfolders": univention.admin.property(
        short_description=_("readCreateSharedFolders"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "subscription": univention.admin.property(
        short_description=_("subscription"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "syncml": univention.admin.property(
        short_description=_("syncml"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "tasks": univention.admin.property(
        short_description=_("tasks"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "vcard": univention.admin.property(
        short_description=_("vcard"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "webdav": univention.admin.property(
        short_description=_("webdav"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "webdavxml": univention.admin.property(
        short_description=_("webdavXml"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
        identifies=False,
    ),
    "webmail": univention.admin.property(
        short_description=_("webmail"),
        long_description="",
        syntax=univention.admin.syntax.TrueFalseUp,
        multivalue=False,
        required=False,
        may_change=False,
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
                _("Rights"),
                layout=[
                    ["activesync", "calendar"],
                    ["collectemailaddresses", "contacts"],
                    ["delegatetask", "deniedportal"],
                    ["editgroup", "editpassword"],
                    ["editpublicfolders", "editresource"],
                    ["globaladdressbookdisabled", "ical"],
                    ["infostore", "multiplemailaccounts"],
                    ["publicfoldereditable", "usm"],
                    ["readcreatesharedfolders", "subscription"],
                    ["syncml", "tasks"],
                    ["vcard", "webdav"],
                    ["webdavxml", "webmail"],
                ],
            ),
        ],
    ),
]

mapping = univention.admin.mapping.mapping()
mapping.register("name", "cn", None, univention.admin.mapping.ListToString)
mapping.register(
    "displayName", "displayName", None, univention.admin.mapping.ListToString
)
mapping.register("usm", "oxRightUsm", None,
                 univention.admin.mapping.ListToString)
mapping.register(
    "activesync", "oxRightActivesync", None, univention.admin.mapping.ListToString
)
mapping.register(
    "calendar", "oxRightCalendar", None, univention.admin.mapping.ListToString
)
mapping.register(
    "collectemailaddresses",
    "oxRightCollectemailaddresses",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "contacts", "oxRightContacts", None, univention.admin.mapping.ListToString
)
mapping.register(
    "delegatetask", "oxRightDelegatetask", None, univention.admin.mapping.ListToString
)
mapping.register(
    "deniedportal", "oxRightDeniedportal", None, univention.admin.mapping.ListToString
)
mapping.register(
    "editgroup", "oxRightEditgroup", None, univention.admin.mapping.ListToString
)
mapping.register(
    "editpassword", "oxRightEditpassword", None, univention.admin.mapping.ListToString
)
mapping.register(
    "editpublicfolders",
    "oxRightEditpublicfolders",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "editresource", "oxRightEditresource", None, univention.admin.mapping.ListToString
)
mapping.register(
    "globaladdressbookdisabled",
    "oxRightGlobaladdressbookdisabled",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register("ical", "oxRightIcal", None,
                 univention.admin.mapping.ListToString)
mapping.register(
    "infostore", "oxRightInfostore", None, univention.admin.mapping.ListToString
)
mapping.register(
    "multiplemailaccounts",
    "oxRightMultiplemailaccounts",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "publicfoldereditable",
    "oxRightPublicfoldereditable",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "readcreatesharedfolders",
    "oxRightReadcreatesharedfolders",
    None,
    univention.admin.mapping.ListToString,
)
mapping.register(
    "subscription", "oxRightSubscription", None, univention.admin.mapping.ListToString
)
mapping.register("syncml", "oxRightSyncml", None,
                 univention.admin.mapping.ListToString)
mapping.register("tasks", "oxRightTasks", None,
                 univention.admin.mapping.ListToString)
mapping.register("vcard", "oxRightVcard", None,
                 univention.admin.mapping.ListToString)
mapping.register("webdav", "oxRightWebdav", None,
                 univention.admin.mapping.ListToString)
mapping.register(
    "webdavxml", "oxRightWebdavxml", None, univention.admin.mapping.ListToString
)
mapping.register(
    "webmail", "oxRightWebmail", None, univention.admin.mapping.ListToString
)


class object(univention.admin.handlers.simpleLdap):
    module = module

    def _ldap_pre_remove(self):
        super(object, self)._ldap_pre_remove()
        access_filter = univention.admin.filter.expression(
            "oxAccess", self["name"])
        searchResult = univention.admin.modules.lookup(
            "users/user", self.co, self.lo, access_filter, scope="sub"
        )
        if len(searchResult) >= 1:
            raise univention.admin.uexceptions.valueError(_(
                "The deletion of the OX access profile object is not allowed as long as users reference it"
            ))


lookup = object.lookup
lookup_filter = object.lookup_filter
identify = object.identify
