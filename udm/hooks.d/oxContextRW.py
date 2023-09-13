# -*- coding: utf-8 -*-
#
# Copyright (C) 2017-2021 Univention GmbH
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

"""
By default the property 'oxContext' of the 'users/user', 'groups/group' and 'oxresources/oxresources'
modules is read-only. This hook configures UDM so that it is writable when used from the CLI.
The property will remain read-only in the UMC and probably the UDM REST API (TODO: verify this).
"""

import sys
import univention.debug
import univention.admin.modules
import univention.admin.uexceptions
import univention.admin.localization
from univention.admin.hook import simpleHook

translation = univention.admin.localization.translation(
    'univention.admin.hooks.d.ox')
_ = translation.translate


class oxContextRW(simpleHook):
    type = 'oxContextRW'

    def is_cli(self):
        return sys.modules.get('univention.management.console.modules.udm') is None

    @staticmethod
    def log_info(msg):
        univention.debug.debug(univention.debug.ADMIN,
                               univention.debug.INFO, 'oxContextRW: %s' % msg)

    def hook_open(self, module):
        if self.is_cli():
            self.log_info('_open: running via CLI')
            for module_name in ('users/user', 'groups/group', 'oxresources/oxresources'):
                imodule = univention.admin.modules.get(module_name)
                if imodule is None:
                    continue
                for iprop in imodule.property_descriptions:
                    if iprop in ('oxContext',):
                        imodule.property_descriptions[iprop].editable = True
                        # imodule.property_descriptions[iprop].may_change = True
                        self.log_info('_open: property %r found in module %r: switched to editable=True' % (
                            iprop, module_name))
        self.log_info('_open: done')
