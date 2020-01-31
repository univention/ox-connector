# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  admin module for the mail domain objects
#
# Copyright (C) 2004-2019 Univention GmbH
#
# http://www.univention.de/
#
# and
#
# iKu Systems & Services GmbH & Co. KG
# http://www.iku-systems.de/
#
# All rights reserved.
#
# This program is free software; you can redistribute it and/or modify
# it under the terms of the GNU General Public License version 2 as
# published by the Free Software Foundation.
#
# Binary versions of this file provided by Univention to you as
# well as other copyrighted, protected or trademarked materials like
# Logos, graphics, fonts, specific documentations and configurations,
# cryptographic keys etc. are subject to a license agreement between
# you and Univention.
#
# This program is distributed in the hope that it will be useful,
# but WITHOUT ANY WARRANTY; without even the implied warranty of
# MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
# GNU General Public License for more details.
#
# You should have received a copy of the GNU General Public License
# along with this program; if not, see <http://www.gnu.org/licenses/>.

import univention.admin.filter
import univention.admin.handlers
import univention.admin.allocators
import univention.admin.localization
from univention.admin.layout import Tab, Group

translation=univention.admin.localization.translation('univention.admin.handlers.oxmail.oxfetchmailsingle')
_=translation.translate

module='oxmail/oxfetchmailsingle'
operations=['add','edit','remove','search','move']
default_containers=[
	"cn=fetchmail,cn=mail",
]

childs=False
short_description=_('OX Mail: Fetchmail Single Drop')
long_description=''

property_descriptions={
	'cn': univention.admin.property(
			short_description=_('Name'),
			long_description='',
			syntax=univention.admin.syntax.string,
			include_in_default_search=1,
			multivalue=0,
			required=1,
			may_change=0,
			identifies=1
		),
	'localrecipient': univention.admin.property(
			short_description=_('Local recipient'),
			long_description='',
			syntax=univention.admin.syntax.UserID,
			multivalue=0,
			dontsearch=1,
			required=0,
			may_change=1,
			identifies=0
		),
	'remoteserver': univention.admin.property(
			short_description=_('Remote server'),
			long_description='',
			syntax=univention.admin.syntax.dnsName,
			multivalue=0,
			required=1,
			may_change=1,
			identifies=0
		),
	'protocol': univention.admin.property(
			short_description=_('Protocol'),
			long_description='',
			syntax=univention.admin.syntax.oxFetchmailProtocol,
			multivalue=0,
			required=1,
			may_change=1,
			identifies=0
		),
	'usessl': univention.admin.property(
			short_description=_('SSL'),
			long_description='',
			syntax=univention.admin.syntax.OkOrNot,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0
		),
	'remoteuser': univention.admin.property(
			short_description=_('Remote user'),
			long_description='',
			syntax=univention.admin.syntax.string,
			multivalue=0,
			required=1,
			may_change=1,
			identifies=0
		),
	'remotepassword': univention.admin.property(
			short_description=_('Remote password'),
			long_description='',
			syntax=univention.admin.syntax.userPasswd,
			multivalue=0,
			required=1,
			may_change=1,
			identifies=0
		),
	'leavemessagesonserver': univention.admin.property(
			short_description=_('Leave messages on server'),
			long_description='',
			syntax=univention.admin.syntax.OkOrNot,
			multivalue=0,
			required=0,
			may_change=1,
			identifies=0
		),
}

layout = [
	Tab( _( 'General' ), _( 'Basic settings' ), layout = [
		Group( _( 'General' ), layout = [
			'cn',
			'localrecipient',
			'remoteserver',
			'protocol',
			'usessl',
			'remoteuser',
			'remotepassword',
			'leavemessagesonserver',
		] ),
	] ),
]

mapping=univention.admin.mapping.mapping()
mapping.register('cn', 'cn', None, univention.admin.mapping.ListToString)
mapping.register('localrecipient', 'localRecipient', None, univention.admin.mapping.ListToString)
mapping.register('remoteserver', 'remoteServer', None, univention.admin.mapping.ListToString)
mapping.register('protocol', 'protocol', None, univention.admin.mapping.ListToString)
mapping.register('usessl', 'useSSL', None, univention.admin.mapping.ListToString)
mapping.register('remoteuser', 'remoteUser', None, univention.admin.mapping.ListToString)
mapping.register('remotepassword', 'remotePassword', None, univention.admin.mapping.ListToString)
mapping.register('leavemessagesonserver', 'leaveMessagesOnServer', None, univention.admin.mapping.ListToString)


class object(univention.admin.handlers.simpleLdap):
	module=module

	def _ldap_addlist(self):
		ocs=[]
		al=[]
		ocs.append('top')
		ocs.append('oxFetchmailSingleDrop')

		al.insert(0, ('objectClass', ocs))
		return al


def lookup(co, lo, filter_s, base='', superordinate=None, scope='sub', unique=0, required=0, timeout=-1, sizelimit=0):
	filter=univention.admin.filter.conjunction('&', [
		univention.admin.filter.expression('cn', '*'),
		univention.admin.filter.expression('objectClass', 'oxFetchmailSingleDrop')
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
	return 'oxFetchmailSingleDrop' in attr.get('objectClass', [])
