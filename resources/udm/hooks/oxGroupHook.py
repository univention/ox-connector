# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  hook definitions
#
# Copyright (C) 2004-2019 Univention GmbH
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
from ldap.filter import filter_format

import univention.debug
import univention.admin.modules
import univention.admin.uexceptions
import univention.admin.localization
import univention.uldap
from univention.admin.hook import simpleHook

translation = univention.admin.localization.translation('univention.admin.hooks.d.ox')
_ = translation.translate


class oxGroupHook(simpleHook):
	type = 'oxGroupHook'
	# dummy function until translation method has been loaded in hook_open()
	_ = lambda x: x

	@staticmethod
	def log_info(msg):
		univention.debug.debug(univention.debug.ADMIN, univention.debug.INFO, 'admin.syntax.hook.oxGroupHook: %s' % msg)

	@staticmethod
	def check_mailaddr(module):
		if module['mailAddress']:
			domain = module['mailAddress'].rsplit('@')[-1]
			filter_s = filter_format('(&(objectClass=oxMailDomainServerSettings)(cn=%s))', (domain,))
			result = module.lo.searchDn(filter=filter_s)

			if not result:
				raise univention.admin.uexceptions.valueError(oxGroupHook._("The mail address' domain does not match any mail domain object."))
			else:
				oxGroupHook.log_info('ldap result: %s' % result)

	def hook_open(self, module):
		oxGroupHook._ = univention.admin.localization.translation('univention.admin.handlers.oxgrouphook').translate
		self.log_info('_open called')

	def hook_ldap_pre_create(self, module):
		self.log_info('_ldap_pre_create called')
		self.check_mailaddr(module)

	def hook_ldap_pre_modify(self, module):
		self.log_info('_ldap_pre_modify called')
		self.check_mailaddr(module)
