# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for mailinglists
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
from ldap.filter import filter_format
import univention.admin.filter
import univention.admin.handlers
import univention.admin.allocators
import univention.admin.localization
from univention.admin.layout import Tab, Group

translation=univention.admin.localization.translation('univention.admin.handlers.oxmail.oxlists')
_=translation.translate

module='oxmail/oxlists'
operations=['add','edit','remove','search','move']
default_containers=[
	"cn=mailinglists,cn=mail",
]

childs=False
short_description=_('OX Mail: Mailing Lists')
long_description=''

property_descriptions={
	'name': univention.admin.property(
			short_description=_('Name'),
			long_description='',
			syntax=univention.admin.syntax.gid,
			include_in_default_search=1,
			multivalue=0,
			required=1,
			may_change=1,
			identifies=1
		),
	'description': univention.admin.property(
			short_description=_('Description'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0
		),
	'members': univention.admin.property(
			short_description=_('Members'),
			long_description='',
			syntax=univention.admin.syntax.emailAddress,
			multivalue=1,
			required=0,
			may_change=1,
			dontsearch=1,
			identifies=0
		),
	'mailAddress': univention.admin.property(
			short_description=_('Mail Address'),
			long_description='',
			syntax=univention.admin.syntax.emailAddress,
			multivalue=0,
			required=0,
			may_change=1,
			dontsearch=0,
			identifies=0
		)
}

layout = [
	Tab(_('General'),_('Basic Values'), layout = [
		Group( _( 'General' ), layout = [
			['name', 'description'],
			'mailAddress',
			'members',
		] ),
	] ),
]

mapping=univention.admin.mapping.mapping()
mapping.register('name', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('description', 'description', None, univention.admin.mapping.ListToString)
mapping.register('members', 'univentionOxMember')
mapping.register('mailAddress', 'mailPrimaryAddress', None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
	module=module

	def _check_mailaddress(self):
		if not self['mailAddress']:
			return
		domain = self['mailAddress'].rsplit('@')[-1]
		filter = filter_format('(&(objectClass=oxMailDomainServerSettings)(cn=%s))', (domain,))
		result = self.lo.searchDn(filter=filter)
		if not result:
			raise univention.admin.uexceptions.valueError, _("The mail address' domain does not match any mail domain object.")

	def _ldap_pre_create(self):
		super(object, self)._ldap_pre_create()
		self._check_mailaddress()

	def _ldap_post_create(self):
		super(object, self)._ldap_post_create()
		if self[ 'mailAddress' ]:
			univention.admin.allocators.confirm( self.lo, self.position, 'mailPrimaryAddress', self[ 'mailAddress' ] )

	def _ldap_pre_modify(self):
		super(object, self)._ldap_pre_modify()
		if self.hasChanged('mailAddress'):
			self._check_mailaddress()

	def _ldap_post_modify( self ):
		super(object, self)._ldap_post_modify()
		if self[ 'mailAddress' ] and self.hasChanged( 'mailAddress' ):
			univention.admin.allocators.confirm( self.lo, self.position, 'mailPrimaryAddress', self[ 'mailAddress' ] )

	def _ldap_addlist(self):
		ocs=['top']
		al=[]
		ocs.append('univentionOxGroup')
		# mail address MUST be unique
		if self[ 'mailAddress' ]:
			try:
				self.alloc.append( ( 'mailPrimaryAddress', self[ 'mailAddress' ] ) )
				univention.admin.allocators.request( self.lo, self.position, 'mailPrimaryAddress', value = self[ 'mailAddress' ] )
			except:
				univention.admin.allocators.release( self.lo, self.position, 'mailPrimaryAddress', value = self[ 'mailAddress' ] )
				raise univention.admin.uexceptions.mailAddressUsed

		al.insert(0, ('objectClass', ocs))
		return al

	def _ldap_modlist( self ):
		if self.hasChanged( 'mailAddress' ) and self[ 'mailAddress' ]:
			for i, _ in self.alloc:
				if i == 'mailPrimaryAddress':
					break
			else:
				try:
					univention.admin.allocators.request( self.lo, self.position, 'mailPrimaryAddress', value = self[ 'mailAddress' ] )
				except:
					univention.admin.allocators.release( self.lo, self.position, 'mailPrimaryAddress', value = self[ 'mailAddress' ] )
					raise univention.admin.uexceptions.mailAddressUsed
		return univention.admin.handlers.simpleLdap._ldap_modlist( self )


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', unique=0, required=0, timeout=-1, sizelimit=0):
	filter=univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression('objectClass', 'univentionOxGroup')
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
	return 'univentionOxGroup' in attr.get('objectClass', [])
