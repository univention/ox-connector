# -*- coding: utf-8 -*-
#
# Copyright 2020 Univention GmbH
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

from zeep.exceptions import Fault


class Skip(Exception):
    """Raise anywhere if you want to skip the processing of this object"""

    pass


def get_obj_by_name_from_ox(klass, context_id, name):
    try:
        return klass.from_ox(context_id, name=name)
    except Fault as exc:
        if str(exc).startswith("com.openexchange.admin.rmi.exceptions.NoSuchObjectException"):
            return None
        if str(exc).startswith("No such "):
            return None
        if str(exc).startswith(f"Context {context_id} does not exist"):
            # this is for searching contexts by id.
            # users in a non-existing context will through a different Fault
            return None
        raise


def get_context_id(attributes):
    context_id = attributes.get("oxContext")
    if context_id is None:
        raise Skip("Object has no oxContext attribute!")
    return context_id


def get_old_obj(dn):
    raise NotImplementedError("Needs to be overwritten by another function")


def get_db_id(dn):
    obj = get_old_obj(dn)
    if obj:
        return obj.attributes.get("oxDbId")

def get_db_username(dn):
    obj = get_old_obj(dn)
    if obj:
        return obj.attributes.get("oxDbId")

def get_db_uid(dn):
    obj = get_old_obj(dn)
    if obj:
        return obj.attributes.get("username")
