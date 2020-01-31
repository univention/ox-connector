# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for mail imap folders
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
import ldap.dn
import univention.admin.filter
import univention.admin.handlers
import univention.admin.allocators
import univention.admin.localization
from univention.admin.layout import Tab, Group

import univention.debug as ud

translation=univention.admin.localization.translation('univention.admin.handlers.oxmail.oxfolder')
_=translation.translate

module='oxmail/oxfolder'
operations=['add','edit','remove','search','move']
default_containers=[
	"cn=folder,cn=mail",
]

childs=False
short_description=_('OX Mail: IMAP Folder')
long_description=''

ldap_search_maildomain = univention.admin.syntax.LDAP_Search(
	filter = '(objectClass=univentionMailDomainname)',
	attribute = [ 'oxmail/oxdomain: name' ],
	value='oxmail/oxdomain: name' )

property_descriptions={
	'name': univention.admin.property(
			short_description=_('Name'),
			long_description='',
			syntax=univention.admin.syntax.ox_mail_folder_name,
			include_in_default_search=1,
			multivalue=0,
			required=1,
			may_change=0,
			identifies=1
		),
	'mailDomain': univention.admin.property(
			short_description=_('Mail Domain'),
			long_description='',
			syntax=ldap_search_maildomain,
			multivalue=0,
			required=1,
			may_change=0,
			identifies=1
		),
	'sharedFolderUserACL': univention.admin.property(
			short_description=_('User ACL'),
			long_description='',
			syntax=univention.admin.syntax.SharedFolderUserACL,
			multivalue=1,
			required=0,
			may_change=1,
			identifies=0,
		),
	'sharedFolderGroupACL': univention.admin.property(
			short_description=_('Group ACL'),
			long_description='',
			syntax=univention.admin.syntax.SharedFolderGroupACL,
			multivalue=1,
			required=0,
			may_change=1,
			identifies=0,
		),
	'mailUserQuota': univention.admin.property(
			short_description=_('Maximum Quota in MB'),
			long_description='',
			syntax=univention.admin.syntax.integer,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0,
		),
	'userNamespace': univention.admin.property(
			short_description=_( 'Should Be Visible For Outlook' ),
			long_description=_( "Outlook does not display folders outside of the 'user' namespace." ),
			syntax=univention.admin.syntax.TrueFalseUp,
			multivalue=0,
			required=0,
			may_change=0,
			identifies=0,
			default=''
		),

	'mailPrimaryAddress': univention.admin.property(
			short_description=_('Mail Address'),
			long_description='',
			syntax=univention.admin.syntax.emailAddress,
			multivalue=0,
			required=0,
			dontsearch=0,
			may_change=1,
			identifies=0,
		),

}

layout = [
	Tab(_('General'),_('General settings'), layout = [
		Group( _( 'General' ), layout = [
			['name', 'mailDomain'],
			'mailUserQuota',
			'mailPrimaryAddress'
		] ),
	] ),
	Tab( _( 'Access Rights'),_('Access rights for shared folder'), layout = [
		Group( _( 'Access Rights' ), layout = [
			'sharedFolderUserACL',
			'sharedFolderGroupACL',
		] ),
	] ),
]

mapping=univention.admin.mapping.mapping()
mapping.register('mailUserQuota', 'cyrus-userquota', None, univention.admin.mapping.ListToString)
mapping.register('mailDomain', 'oxDomainName', None, univention.admin.mapping.ListToString)
mapping.register('mailPrimaryAddress', 'mailPrimaryAddress', None, univention.admin.mapping.ListToString)
mapping.register('userNamespace', 'univentionOxUserNamespace', None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
	userNamespace = 'FALSE'
	module=module

	def open(self):
		univention.admin.handlers.simpleLdap.open(self)
		if self.dn:
			cn=self.oldattr.get('cn',[])
			if cn:
				self['name']=cn[0].split('@')[0]
				self['mailDomain']=cn[0].split('@')[1]

			# fetch values for ACLs
			acls=self.oldattr.get('acl',[])
			self['sharedFolderUserACL']=[]
			self['sharedFolderGroupACL']=[]
			if acls:
				for acl in acls:
					if acl.find( '@' ) > 0 or acl.startswith( 'anyone' ):
						self['sharedFolderUserACL'].append( acl.rsplit( ' ', 1 ) )
					else:
						self['sharedFolderGroupACL'].append( acl.rsplit( ' ', 1 ) )
		self.save()

	def _check_mailaddress(self):
		if not self['mailPrimaryAddress']:
			return
		domain = self['mailPrimaryAddress'].rsplit('@')[-1]
		filter = filter_format('(&(objectClass=oxMailDomainServerSettings)(cn=%s))', (domain,))
		result = self.lo.searchDn(filter=filter)
		if not result:
			raise univention.admin.uexceptions.valueError, _("The mail address' domain does not match any mail domain object.")

	def _ldap_pre_create(self):
		super(object, self)._ldap_pre_create()
		self._check_mailaddress()

	def _ldap_dn(self):
		return '%s,%s' % (ldap.dn.dn2str([[('cn', '%s@%s' % (self.info['name'], self.info['mailDomain']), ldap.AVA_STRING)]]), self.position.getDn())

	def _ldap_post_create(self):
		super(object, self)._ldap_post_create()
		if self[ 'userNamespace' ] == 'TRUE':
			address = '%s@%s' % ( self[ 'name' ], self[ 'mailDomain' ] )
			univention.admin.allocators.release( self.lo, self.position, 'mailPrimaryAddress', value = address )
		if self[ 'mailPrimaryAddress' ]:
			univention.admin.allocators.release( self.lo, self.position, 'mailPrimaryAddress', value = self[ 'mailPrimaryAddress' ] )

	def _ldap_addlist(self):
		ocs=[]
		al=[]

		if self[ 'mailPrimaryAddress' ]:
			al.append(('univentionOxSharedFolderDeliveryAddress', 'univentioninternalpostuser+shared/%s@%s' % ( self [ 'name' ], self[ 'mailDomain' ] ) ) )

			address = '%s@%s' % ( self[ 'name' ], self[ 'mailDomain' ] )
			if self[ 'mailPrimaryAddress' ] != address:
				try:
					self.alloc.append( ( 'mailPrimaryAddress', self[ 'mailPrimaryAddress' ] ) )
					univention.admin.allocators.request( self.lo, self.position, 'mailPrimaryAddress', value = self[ 'mailPrimaryAddress' ] )
				except:
					univention.admin.allocators.release( self.lo, self.position, 'mailPrimaryAddress', value = self[ 'mailPrimaryAddress' ] )
					raise univention.admin.uexceptions.mailAddressUsed

		ocs.append('oxSharedFolder')

		al.insert(0, ('objectClass', ocs))
		al.append(('cn', "%s@%s" % (self.info['name'], self.info['mailDomain'])))

		return al

	def _ldap_pre_modify(self):
		super(object, self)._ldap_pre_modify()
		if self.hasChanged('mailPrimaryAddress'):
			self._check_mailaddress()

	def _ldap_post_modify(self):
		super(object, self)._ldap_post_modify()
		if self[ 'mailPrimaryAddress' ]:
			univention.admin.allocators.release( self.lo, self.position, 'mailPrimaryAddress', value = self[ 'mailPrimaryAddress' ] )

	def _ldap_modlist(self):
		# we get a list of modifications to be done (called 'ml' down below)
		# this lists looks like this:
		# [('oxHomeServer', [u'ugs-master.hosts.invalid'], u'ugs-master.hosts.invalid'), ('cyrus-userquota', u'100', u'101')]
		# we can modify those entries to conform to the LDAP schema

		ml=univention.admin.handlers.simpleLdap._ldap_modlist(self)

		if self.hasChanged( 'mailPrimaryAddress' ) and self[ 'mailPrimaryAddress' ]:
			for i, _ in self.alloc:
				if i == 'mailPrimaryAddress':
					break
			else:
				ml.append( ( 'univentionOxSharedFolderDeliveryAddress',
							self.oldattr.get( 'univentionOxSharedFolderDeliveryAddress', [] ),
							[ 'univentioninternalpostuser+shared/%s@%s' % ( self[ 'name' ], self[ 'mailDomain' ] ) ] ) )

				address = '%s@%s' % ( self[ 'name' ], self[ 'mailDomain' ] )
				if self[ 'mailPrimaryAddress' ] != address:
					try:
						self.alloc.append( ( 'mailPrimaryAddress', self[ 'mailPrimaryAddress' ] ) )
						univention.admin.allocators.request( self.lo, self.position, 'mailPrimaryAddress', value = self[ 'mailPrimaryAddress' ] )
					except:
						univention.admin.allocators.release( self.lo, self.position, 'mailPrimaryAddress', value = self[ 'mailPrimaryAddress' ] )
						raise univention.admin.uexceptions.mailAddressUsed
		if not self[ 'mailPrimaryAddress' ]:
			ml.append( ( 'univentionOxSharedFolderDeliveryAddress', self.oldattr.get( 'univentionOxSharedFolderDeliveryAddress', [] ), [] ) )

		rewrite_acl = False
		new_acls_tmp = []
		for attr in [ 'sharedFolderUserACL', 'sharedFolderGroupACL' ]:
			ud.debug( ud.ADMIN, ud.INFO, 'ACLs: %s' % str( self[ attr ] ) )
			if self.hasChanged( attr ):
				rewrite_acl = True
				# re-use regular expressions from syntax definitions
				if attr=='sharedFolderUserACL':
					_sre = univention.admin.syntax.UserMailAddress.regex
				else:
					_sre = univention.admin.syntax.GroupName.regex
				for acl in self[ attr ]:
					if _sre.match( acl[ 0 ] ):
						new_acls_tmp.append( ' '.join( acl ) )
			else:
				for acl in self[attr]:
					new_acls_tmp.append( ' '.join( acl ) )

		if rewrite_acl:
			for (a, b, c) in ml:
				if a in ['sharedFolderUserACL', 'sharedFolderGroupACL']:
					ml.remove((a, b, c))
			ml.append( ( 'acl', self.oldattr.get( 'acl', [] ), new_acls_tmp ) )

		return ml


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', unique=0, required=0, timeout=-1, sizelimit=0):
	filter=univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression('cn', '*'),
		univention.admin.filter.expression('objectClass', 'oxSharedFolder')
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
	return 'oxSharedFolder' in attr.get('objectClass', [])
