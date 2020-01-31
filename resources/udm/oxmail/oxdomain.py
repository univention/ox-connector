# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for mail domain objects
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
from univention.config_registry import ConfigRegistry
from univention.admin.layout import Tab, Group

ucr = ConfigRegistry()
ucr.load()

translation=univention.admin.localization.translation('univention.admin.handlers.oxmail.oxdomain')
_=translation.translate

module='oxmail/oxdomain'
operations=['add','edit','remove','search','move']
default_containers=[
	"cn=domain,cn=mail",
]

childs=False
short_description=_('OX Mail: Mail Domain')
long_description=''

hostname = ucr.get('hostname')
domainname = ucr.get('domainname')
oxImapServerDefault='%s.%s' % (hostname, domainname)

property_descriptions={
	'name': univention.admin.property(
			short_description=_('Name'),
			long_description='',
			syntax=univention.admin.syntax.dnsName,
			include_in_default_search=1,
			multivalue=0,
			required=1,
			may_change=0,
			identifies=1
		),
	'oxImapServer': univention.admin.property(
			short_description=_('Imap server'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=1,
			may_change=1,
			identifies=0,
			default=oxImapServerDefault
		),
	'oxContextName': univention.admin.property(
			short_description=_('OX context name'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=1,
			may_change=1,
			identifies=0,
			default="context%s" % (ucr.get('ox/context/id', '10'))
		),
}

layout = [
	Tab( _( 'General' ), _( 'Basic Values' ), layout = [
		Group( _( 'General' ), layout = [
			'name',
		] ),
	] ),
]

mapping=univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('oxImapServer', 'oxImapServer', None, univention.admin.mapping.ListToString)
mapping.register('oxContextName', 'oxContextName', None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
	module=module

	def _ldap_addlist(self):
		ocs=[]
		al=[]
		ocs.append('top')
		ocs.append('univentionMailDomainname')
		ocs.append('oxMailDomainServerSettings')

		al.insert(0, ('objectClass', ocs))
		return al

	def _ldap_modlist(self):
		ml = univention.admin.handlers.simpleLdap._ldap_modlist(self)
		ocs = self.oldattr.get("objectClass", [])
		if not "oxMailDomainServerSettings" in ocs:
			oldOcs = [ x for x in ocs ]
			ocs.append("oxMailDomainServerSettings")
			ml.insert(0, ("objectClass", oldOcs, ocs))
		return ml


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', unique=0, required=0, timeout=-1, sizelimit=0):
	filter=univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression('cn', '*'),
		univention.admin.filter.expression('objectClass', 'univentionMailDomainname')
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
	return 'univentionMailDomainname' in attr.get('objectClass', [])
