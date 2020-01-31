# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for the mail domain objects
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
import univention.admin.handlers
import univention.admin.allocators
import univention.admin.localization
from univention.admin.layout import Tab, Group

translation=univention.admin.localization.translation('univention.admin.handlers.oxmail.oxcontext')
_=translation.translate

module='oxmail/oxcontext'
operations=['add','edit','remove','search','move']
default_containers=[
	"cn=folder,cn=mail",
	"cn=mailinglists,cn=mail",
	"cn=fetchmail,cn=mail",
	"cn=domain,cn=mail",
]

childs=False
short_description=_('OX Mail: OX context')
long_description=''

property_descriptions={
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
	'hostname': univention.admin.property(
			short_description=_('Hostname'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=1,
			may_change=1,
			identifies=0
		),
	'oxintegrationversion': univention.admin.property(
			short_description=_('OX integration version'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=1,
			may_change=1,
			identifies=0
		),
	'oxguiversion': univention.admin.property(
			short_description=_('OX GUI version'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0
		),
	'oxadmindaemonversion': univention.admin.property(
			short_description=_('OX admindaemon version'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0
		),
	'oxgroupwareversion': univention.admin.property(
			short_description=_('OX groupware version'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0
		),
	'contextid': univention.admin.property(
			short_description=_('Context ID'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=1,
			may_change=0,
			identifies=0
		),
	'oxDBServer': univention.admin.property(
			short_description=_('OX Database Server'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=1,
			may_change=1,
			identifies=0
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
}

layout = [
	Tab(_('General'),_('Basic Values'), layout = [
		Group( _( 'General' ), layout = [
			'name',
			'hostname',
			'oxQuota',
		] ),
	] ),
]

mapping=univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('hostname', 'oxHomeServer', None, univention.admin.mapping.ListToString)
mapping.register('contextid', 'oxContextIDNum', None, univention.admin.mapping.ListToString)
mapping.register('oxQuota', 'oxQuota', None, univention.admin.mapping.ListToString)
mapping.register('oxintegrationversion', 'oxIntegrationVersion', None, univention.admin.mapping.ListToString)
mapping.register('oxguiversion', 'oxGuiVersion', None, univention.admin.mapping.ListToString)
mapping.register('oxgroupwareversion', 'oxGroupwareVersion', None, univention.admin.mapping.ListToString)
mapping.register('oxadmindaemonversion', 'oxAdminDaemonVersion', None, univention.admin.mapping.ListToString)
mapping.register('oxDBServer', 'oxDBServer', None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
	module=module

	def _ldap_pre_remove(self):
		super(object, self)._ldap_pre_remove()
		# refuse deletion of context object if it is the only one
		searchResult = lookup(self.co, self.lo, None)
		if len(searchResult) <= 1:
			raise univention.admin.uexceptions.valueError, _('The deletion of the OX context object is not allowed!')

	def _ldap_addlist(self):
		ocs=[]
		al=[]
		ocs.append('top')
		ocs.append('oxContext')

		al.insert(0, ('objectClass', ocs))
		return al


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', unique=0, required=0, timeout=-1, sizelimit=0):
	filter=univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression('cn', '*'),
		univention.admin.filter.expression('objectClass', 'oxContext')
		])

	if filter_s:
		filter_p=univention.admin.filter.parse(filter_s)
		univention.admin.filter.walk(filter_p, univention.admin.mapping.mapRewrite, arg=mapping)
		filter.expressions.append(filter_p)

	res=[]
	for dn, attrs in lo.search(unicode(filter), base, scope, [], unique, required, timeout, sizelimit):
		res.append( object( co, lo, None, dn, attributes = attrs ) )
	return res


def identify(dn, attr, canonical=0):
	return 'oxContext' in attr.get('objectClass', [])
