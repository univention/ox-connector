# -*- coding: utf-8 -*-
#
# Client for OX' SOAP API
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
# Provision Open-Xchange using SOAP: http://oxpedia.org/wiki/index.php?title=Open-Xchange_Provisioning_using_SOAP
# API docs: http://software.open-xchange.com/products/appsuite/doc/SOAP/admin/OX-Admin-SOAP.html
# WSDL: http://<IP>/webservices/OXContextService?wsdl
#

from __future__ import absolute_import
from .config import get_credentials_for_context, get_master_credentials, OX_SOAP_SERVER
from .types import Types


class ClientCredentials(object):
    _context_admin_credentials = dict()
    _context_objs = dict()
    _types = None

    def __init__(self, server=OX_SOAP_SERVER, context_id=10, username=None, password=None):
        # type: (Optional[str], Optional[int], Optional[str], Optional[str]) -> None

        self.server = server
        self.context_id = int(context_id)
        self.username = username
        self.password = password

    @property
    def master_credentials(self):
        user, pw = get_master_credentials()
        return self.types.Credentials(login=user, password=pw)

    @property
    def context_admin_credentials(self):
        if self.context_id not in self._context_admin_credentials:
            self._context_admin_credentials[self.context_id] = self.types.Credentials(*get_credentials_for_context(self.context_id))
        return self._context_admin_credentials[self.context_id]

    @property
    def credentials(self):
        if self.username and self.password:
            return self.types.Credentials(self.username, self.password)
        else:
            return self.context_admin_credentials

    @property
    def context_obj(self):
        if self.context_id not in self._context_objs:
            self._context_objs[self.context_id] = self.types.Context(id=self.context_id)
        return self._context_objs[self.context_id]

    @property
    def types(self):
        if not self._types:
            self.__class__._types = Types(self.server)
        return self._types
