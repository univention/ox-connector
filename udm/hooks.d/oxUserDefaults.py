#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
"""
UDM-hook to set default values for user accounts not created using the ox
user template
"""
# Copyright 2016-2021 Univention GmbH
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

import traceback

from ldap.filter import filter_format

import univention.debug as ud
import univention.admin.modules
import univention.admin.uldap
import univention.config_registry
from univention.admin.hook import simpleHook
from univention.admin import property as uadmin_property

configRegistry = univention.config_registry.ConfigRegistry()
configRegistry.load()
ox_attrs_base = "cn=open-xchange,cn=custom attributes,cn=univention,%s" % configRegistry["ldap/base"]
ox_property_list = ("oxAccess",)

ucs_user_template_replace = uadmin_property("_replace")._replace


class oxUserDefaults(simpleHook):
	type = "oxUserDefaults"
	_ox_defaults = {}

	@classmethod
	def ox_defaults(cls, lo, pos):
		if not cls._ox_defaults:
			univention.admin.modules.update()
			ext_attr_module = univention.admin.modules.get('settings/extended_attribute')
			univention.admin.modules.init(lo, pos, ext_attr_module)
			cls._ox_defaults['isOxUser'] = 'Not'
			for attr in ox_property_list:
				attr_m = ext_attr_module.lookup(None, lo, scope='sub', base=ox_attrs_base, filter_s=filter_format('cn=%s', (attr,)))
				if attr_m:
					cls._ox_defaults[attr] = attr_m[0].info['default']
		return cls._ox_defaults

	def hook_open(self, module):
        if 'oxUserDefaults' not in module:
            module.oxUserDefaults = {}
        if not module.info:
            # UMC module init
			return
		for k, v in self.ox_defaults(module.lo, module.position).items():
			if k not in module.info:
				# OX-Bug #45937
				# module.save() is called after hook_open(), so module.oldinfo already contains
				# the modified state and UDM is not able to detect any modification if the default
				# values are kept. That's why we store the old value in module.oxUserDefaults
				# and modify module.oldinfo in hook_ldap_pre_modify(). When the module generates
				# the modlist, module.oldinfo contains the correct state.
				module.oxUserDefaults[k] = None
                module[k] = v

    def hook_ldap_pre_modify(self, module):
        for key, value in module.oxUserDefaults.items():
            if key in module.oldinfo and value is None:
                del module.oldinfo[key]
