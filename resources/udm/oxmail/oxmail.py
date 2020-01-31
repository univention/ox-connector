# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for mail objects
#
# Copyright (C) 2004-2019 Univention GmbH <http://www.univention.de/>
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

import univention.admin.filter
import univention.admin.localization

from univention.admin.layout import Tab
import univention.admin.handlers
import univention.admin.handlers.oxmail.oxdomain
import univention.admin.handlers.oxmail.oxcontext
import univention.admin.handlers.oxmail.oxfolder
import univention.admin.handlers.oxmail.oxlists
import univention.admin.handlers.oxmail.oxfetchmailsingle
import univention.admin.handlers.oxmail.oxfetchmailmulti

translation=univention.admin.localization.translation('univention.admin.handlers.oxmail.oxmail')
_=translation.translate

module='oxmail/oxmail'

childs=True
short_description=_('OX Mail')
long_description=''
operations=['search']
default_containers=[
	"cn=folder,cn=mail",
	"cn=mailinglists,cn=mail",
	"cn=fetchmail,cn=mail",
	"cn=domain,cn=mail",
]

childmodules = [
	"oxmail/oxfolder",
	"oxmail/oxlists",
	"oxmail/oxfetchmailsingle",
	"oxmail/oxfetchmailmulti",
	"oxmail/oxdomain",
]

virtual=1
options={}
property_descriptions={
	'name': univention.admin.property(
			short_description=_('Name'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			include_in_default_search=1,
			options=[],
			required=1,
			may_change=1,
			identifies=1
		)
}

layout = [ Tab( _( 'General' ), _( 'Basic settings' ), [ "name" ] ) ]

mapping=univention.admin.mapping.mapping()


class object(univention.admin.handlers.simpleLdap):
	module=module


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', unique=0, required=0, timeout=-1, sizelimit=0):
	ret=[]
	ret+=univention.admin.handlers.oxmail.oxdomain.lookup(
		co, lo, filter_s, base, superordinate, scope, unique, required, timeout, sizelimit)
	ret+=univention.admin.handlers.oxmail.oxfolder.lookup(
		co, lo, filter_s, base, superordinate, scope, unique, required, timeout, sizelimit)
	ret+=univention.admin.handlers.oxmail.oxlists.lookup(
		co, lo, filter_s, base, superordinate, scope, unique, required, timeout, sizelimit)
	ret+=univention.admin.handlers.oxmail.oxfetchmailmulti.lookup(
		co, lo, filter_s, base, superordinate, scope, unique, required, timeout, sizelimit)
	ret+=univention.admin.handlers.oxmail.oxfetchmailsingle.lookup(
		co, lo, filter_s, base, superordinate, scope, unique, required, timeout, sizelimit)
	ret+=univention.admin.handlers.oxmail.oxcontext.lookup(
		co, lo, filter_s, base, superordinate, scope, unique, required, timeout, sizelimit)
	return ret


def identify(dn, attr, canonical=0):
	pass
