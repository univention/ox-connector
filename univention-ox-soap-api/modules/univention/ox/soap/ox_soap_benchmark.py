# -*- coding: utf-8 -*-
#
# Benchmark OX' SOAP API interface
#
# Copyright 2018-2020 Univention GmbH
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

#
# Client for OX' SOAP API
# API docs: http://oxpedia.org/wiki/index.php?title=Open-Xchange_Provisioning_using_SOAP
#

#
# INSTALL
#
# Debain Stretch: python-zeep 0.23.0-1
# Debain Buster:  python-zeep 2.4.0-1   # <-- we want this
#
# UCS 4.2:
#
# univention-install virtualenv libxslt-dev libxml2-dev libz-dev
# virtualenv --system-site-packages venv_zeep
# . venv_zeep/bin/activate
# pip install zeep
#

from __future__ import absolute_import
import time
from collections import defaultdict
from zeep import Client as ZeepClient
from zeep.cache import InMemoryCache
from zeep.transports import Transport
from univention.ox.listener_tools import get_credentials_for_context, get_master_credentials


WS_BASE_URL = 'http://127.0.0.1/webservices'
WS_CONTEXT_URL = '{}/OXContextService?wsdl'.format(WS_BASE_URL)
WS_GROUP_URL = '{}/OXGroupService?wsdl'.format(WS_BASE_URL)
WS_USER_URL = '{}/OXUserService?wsdl'.format(WS_BASE_URL)

transport = Transport(cache=InMemoryCache())

client_context = ZeepClient(WS_CONTEXT_URL, transport=transport)
client_group = ZeepClient(WS_GROUP_URL, transport=transport)
client_user = ZeepClient(WS_USER_URL, transport=transport)

credentials_type = client_context.wsdl.types.get_type('{http://dataobjects.rmi.admin.openexchange.com/xsd}Credentials')
context_type = client_context.wsdl.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}Context')
user_type = client_context.wsdl.types.get_type('{http://dataobjects.soap.admin.openexchange.com/xsd}User')

master_creds = credentials_type(*get_master_credentials())
users = defaultdict(dict)
simple_users = {}
groups = {}
context_objs = dict((c.id, c) for c in client_context.service.listAll(auth=master_creds))
context_creds = dict((c_id, credentials_type(*get_credentials_for_context(c_id))) for c_id in context_objs.keys())

print('Found contexts: {}'.format(', '.join(str(c_id) for c_id in context_objs.keys())))

t0 = time.time()
for context_id, context_obj in context_objs.items():
    print('Retrieving all groups of context {}...'.format(context_id))
    groups[context_id] = client_group.service.listAll(ctx=context_obj, auth=context_creds[context_id])
    print('... found {} groups.'.format(len(groups[context_id])))
print('Total time for group retrieval: {:.2f} seconds.'.format(time.time() - t0))

t0 = time.time()
for context_id, context_obj in context_objs.items():
    print('Retrieving all user IDs in context {}...'.format(context_id))
    simple_users[context_id] = client_user.service.listAll(ctx=context_obj, auth=context_creds[context_id])
    print('... found {} users.'.format(len(simple_users[context_id])))
print('Retrieved {} user IDs in {:.2f} seconds.'.format(sum(len(g) for g in simple_users.values()), time.time() - t0))

t1 = time.time()
for context_id, context_obj in context_objs.items():
    print('Retrieving {} complete user objects in context {}...'.format(len(simple_users[context_id]), context_id))
    for user_id in [u.id for u in simple_users[context_id]]:
        users[context_id][user_id] = client_user.service.getData(
            ctx=context_obj,
            user=user_type(id=user_id),
            auth=context_creds[context_id],
        )
print('Retrieved {} complete user objects in {:.2f} seconds.'.format(sum(len(g) for g in users.values()), time.time() - t1))
print('Total time for user retrieval: {:.2f} seconds.'.format(time.time() - t0))
