#!/usr/bin/python2.7
# -*- coding: utf-8 -*-
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

import univention.uldap
import univention.admin.modules

# determine current lookup filter from users/user
univention.admin.modules.update()
usersmod = univention.admin.modules.get("users/user")
user_filter = str(usersmod.lookup_filter(filter_s='(|(mailPrimaryAddress=*)(mailAlternativeAddress=*))'))

lo = univention.uldap.getMachineConnection(ldap_master=False)

mailDomains = {}
domainToCreate = {}

# get mail domain
for res in lo.search(filter='(objectClass=oxMailDomainServerSettings)', attr=['cn']):
	cn = res[1].get("cn", [""])[0]
	if cn:
		mailDomains[cn] = True

# get mail addresses
for res in lo.search(filter=user_filter, attr=['mailPrimaryAddress', 'mailAlternativeAddress']):
	myAddresses = []
	myAddresses.append(res[1].get("mailPrimaryAddress", [""])[0])
	for i in res[1].get("mailAlternativeAddress", [""]):
		if i:
			myAddresses.append(i)
	for address in myAddresses:
		if "@" in address:
			dummy, domain = address.rsplit("@", 1)
			if not mailDomains.get(domain):
				domainToCreate[domain] = True

# list missing mail domains
for domain in domainToCreate:
	print domain
