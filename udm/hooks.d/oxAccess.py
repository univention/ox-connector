# -*- coding: utf-8 -*-
#
# Univention Admin Modules
#  hook definitions
#
# Copyright (C) 2004-2021 Univention GmbH
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

import re
import datetime
from ldap.filter import filter_format
import univention.debug
import univention.admin.modules
import univention.admin.uexceptions
import univention.admin.localization
import univention.uldap
import univention.config_registry
from univention.admin.hook import simpleHook

translation = univention.admin.localization.translation('univention.admin.hooks.d.ox')
_ = translation.translate


class oxAccess(simpleHook):
    type = 'oxAccess'
    # dummy function until translation method has been loaded in hook_open()
    _ = lambda x: x

    @staticmethod
    def log_info(msg):
        univention.debug.debug(univention.debug.ADMIN, univention.debug.INFO, 'oxAccess: %s' % msg)

    @staticmethod
    def check_syntax(module):
        if module['username']:
            username = module['username']
            oxAccess.log_info('username: %s' % username)
            unicode_username = username.decode("UTF-8") if isinstance(username, bytes) else username
            p1 = re.compile(r'(?u)(^[a-zA-Z])[a-zA-Z0-9._-]*([a-zA-Z0-9]$)')
            p2 = re.compile(r'(?u)^\w([\w -.]*\w)?$')
            return p1.match(unicode_username) and p2.match(unicode_username)
        return False

    @staticmethod
    def check_oxaccess(module):
        return module['isOxUser'] == 'OK'

    @staticmethod
    def getOxResources(module):
        oxAccess.log_info('getOxResources')
        return module.oldattr.get('oxResourceMailAddress')

    @staticmethod
    def check_mailaddr(module):
        if module['mailPrimaryAddress']:
            domain = module['mailPrimaryAddress'].rsplit('@')[-1]
            filter_s = filter_format('(&(objectClass=univentionMailDomainname)(cn=%s))', (domain,))
            result = module.lo.searchDn(filter=filter_s)

            if not result:
                raise univention.admin.uexceptions.valueError(oxAccess._("The mail address' domain does not match any mail domain object."))
            else:
                oxAccess.log_info('ldap result: %s' % result)
        else:
            raise univention.admin.uexceptions.valueError(oxAccess._("The primary mail address is required for Open-Xchange users. Currently the users' primary mail address is not set."))

    @staticmethod
    def check_date(datestring):
        oxAccess.log_info('Verfying date value: %s' % datestring)
        if '-' in datestring:
            year, month, day = map(int, datestring.split('-'))
        else:
            day, month, year = map(int, datestring.split('.'))
        date = datetime.date(year, month, day)
        iso = date.isoformat()
        oxAccess.log_info('Value of oxAccess: %s' % iso)

    def check_syntax_date(self, module):
        if module['oxAnniversary']:
            try:
                self.check_date(module['oxAnniversary'])
            except ValueError:
                raise univention.admin.uexceptions.valueError(oxAccess._('Anniversary must be in format \'YYYY-MM-DD\' or \'TT-MM-JJJJ\''))

    @staticmethod
    def check_firstname(module):
        return bool(module['firstname'])

    def hook_open(self, module):
        if module.module != 'users/user':
            return
        oxAccess._ = univention.admin.localization.translation('univention.admin.handlers.oxaccess').translate
        self.log_info('_open called')

    def hook_ldap_pre_create(self, module):
        if module.module != 'users/user':
            return
        self.log_info('_ldap_pre_create called')

        hasOxAccess = self.check_oxaccess(module)
        self.log_info('oxaccess: %s' % hasOxAccess)

        # disable OX integration if mail address has not been specified --> allow to create users via CLI
        if hasOxAccess and not module.info.get('mailPrimaryAddress'):
            module['isOxUser'] = 'Not'
            hasOxAccess = self.check_oxaccess(module)

        self.check_syntax_date(module)
        if hasOxAccess:
            # if not self.check_syntax(module):
            #     raise univention.admin.uexceptions.valueError, 'Username must only contain numbers, letters and dots!'

            configRegistry = univention.config_registry.ConfigRegistry()
            configRegistry.load()
            contextadmin = 'oxadmin-context%s' % (configRegistry.get('ox/context/id', '10'),)
            if contextadmin == 'oxadmin-context10':
                contextadmin = 'oxadmin'

            if module['username'] != contextadmin:
                self.check_mailaddr(module)
            if not self.check_firstname(module):
                raise univention.admin.uexceptions.valueError(oxAccess._('First name has to be set for open-xchange users.'))

    def hook_ldap_pre_modify(self, module):
        if module.module != 'users/user':
            return
        self.log_info('_ldap_pre_modify called')
        hasOxAccess = self.check_oxaccess(module)
        self.log_info('oxaccess: %s' % hasOxAccess)

        self.check_syntax_date(module)
        if hasOxAccess:
            # if not self.check_syntax(module):
            #     raise univention.admin.uexceptions.valueError, 'Username must only contain numbers, letters and dots!'
            self.check_mailaddr(module)
            if not self.check_firstname(module):
                raise univention.admin.uexceptions.valueError(oxAccess._('First name has to be set for open-xchange users.'))

    def hook_ldap_pre_remove(self, module):
        if module.module != 'users/user':
            return
        self.log_info('_ldap_pre_remove called')
        resources = self.getOxResources(module)
        if resources:
            raise univention.admin.uexceptions.valueError(oxAccess._('The user %s cannot be removed because he is admin of the following resources: %s') % (module.oldinfo.get('username', '???'), b', '.join(resources).decode('utf-8')))
