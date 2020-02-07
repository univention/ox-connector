#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
"""
Convert mail domains between UCS and Open-Xchange.
"""
#
# Copyright (C) 2012-2019 Univention GmbH
#
# http://www.univention.de/
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

import sys
from optparse import OptionParser, OptionGroup
from univention.config_registry import ConfigRegistry
import univention.admin.modules
import univention.admin.config
import univention.admin.uldap

class Converter(object):
	def __init__(self):
		self.options = None
		self.ucr = ConfigRegistry()
		self.ucr.load()
		self.config = None
		self.access = None
		self.position = None
		self.ret = 0

		self.contextId = int(self.ucr.get('ox/context/id', 10))

	def main(self):
		self.parse_cmdline()

		self.get_ldap()
		if self.options.to_ucs:
			ret = self.ox2ucs()
		else:
			module = self.setup_module()
			ret = self.ucs2ox(module)

		return ret

	def parse_cmdline(self):
		usage = "%prog [options] {--ucs2ox | ox2ucs}"
		description = sys.modules[__name__].__doc__
		parser = OptionParser(usage=usage, description=description)
		parser.add_option(
			'--verbose', '-v',
			action='store_true', dest='verbose', help='Enable verbode output')
		parser.add_option(
			'--context', '-c',
			action='store', type='int', dest='context', default=self.contextId,
			help='Specify context ID [default: %default]')

		group = OptionGroup(parser, "LDAP bind credentials")
		group.add_option(
			'--binddn',
			action='store', dest='binddn', help='LDAP bind dn for UDM CLI operation')
		group.add_option(
			'--bindpwd',
			action='store', dest='bindpwd', help='LDAP bind password for bind dn')
		group.add_option(
			'--bindpwdfile',
			action='store', dest='bindpwdfile', help='file with LDAP bind password for bind dn')
		parser.add_option_group(group)

		group = OptionGroup(parser, "Mode")
		group.add_option(
			'--ucs2ox',
			action='store_false', dest='to_ucs', help='Convert UCS mail domains to OX [default]')
		group.add_option(
			'--ox2ucs',
			action='store_true', dest='to_ucs', help='Convert OX mail domains to UCS')
		parser.add_option_group(group)

		(self.options, _args) = parser.parse_args()

	def get_ldap(self):
		self.config = univention.admin.config.config(host=self.ucr["ldap/server/name"])
		if self.options.bindpwd:
			bindpwd = self.options.bindpwd
		elif self.options.bindpwdfile:
			with open(self.options.bindpwdfile) as fp:
				bindpwd = fp.read().strip()
		else:
			bindpwd = None

		if self.options.binddn and bindpwd is not None:
			self.access = univention.admin.uldap.access(
				host=self.ucr["ldap/master"],
				port=int(self.ucr.get('ldap/master/port', '7389')),
				base=self.ucr['ldap/base'],
				binddn=self.options.binddn,
				bindpw=bindpwd,
				start_tls=1)
			self.position = univention.admin.uldap.position(self.ucr['ldap/base'])
		else:
			self.access, self.position = univention.admin.uldap.getAdminConnection()

	def setup_module(self):
		univention.admin.modules.update()
		module = univention.admin.modules.get("oxmail/oxdomain")
		univention.admin.modules.init(self.access, self.position, module)
		return module

	def ucs2ox(self, module):
		self.debug("Converting UCR mail domains to OX mail domains...")
		oxContextName = "context%d" % (self.options.context,)
		oxImapServer = '%(hostname)s.%(domainname)s' % self.ucr

		for obj in module.lookup(self.config, self.access, None):
			obj.open()
			if not obj.get("oxImapServer"):
				obj["oxImapServer"] = oxImapServer
				obj["oxContextName"] = oxContextName
				self.debug('Updading %s' % obj.dn)
				try:
					obj.modify()
				except Exception as ex:
					self.error('Failed to modify %s: %s' % (obj.dn, ex))
		self.debug("Done.")

	def ox2ucs(self):
		self.debug("Converting OX mail domains to UCS mail domains...")
		for dn, attrs in self.access.search(
			filter='(objectClass=oxMailDomainServerSettings)',
			attr=['objectClass', 'oxImapServer', 'oxContextName', 'univentionObjectType']
		):
			classes = attrs.get('objectClass', [])
			changes = [
				('objectClass', classes, [x for x in classes if x != 'oxMailDomainServerSettings']),
				('oxImapServer', attrs.get('oxImapServer', []), []),
				('oxContextName', attrs.get('oxContextName', []), []),
				('univentionObjectType', attrs.get('univentionObjectType', []), ['mail/domain']),
			]
			try:
				self.debug('Updating %s' % dn)
				self.access.modify(dn, changes, ignore_license=1)
			except Exception as ex:
				self.error('Failed to modify %s: %s' % (dn, ex))
		self.debug("Done.")

	def debug(self, msg):
		if self.options.verbose:
			print >> sys.stderr, msg

	def error(self, msg):
		print >> sys.stderr, msg
		self.ret = 1


def main():
	c = Converter()
	c.main()
	sys.exit(c.ret)


if __name__ == '__main__':
	main()
