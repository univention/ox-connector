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

import logging
import ldap.dn
from typing import Dict, Any


from zeep.exceptions import Fault

_OX_VERSION = False

logger = logging.getLogger("listener")


class Skip(Exception):
    """Raise anywhere if you want to skip the processing of this object"""

    pass


class SkipContextAdmin(Skip):
    pass


def get_obj_by_name_from_ox(
    klass,
    context_id,
    name,
    raise_exception_on_zeep_exceptions_Fault=False,
):
    try:
        return klass.from_ox(context_id, name=name)
    except Fault as exc:
        if raise_exception_on_zeep_exceptions_Fault:
            raise
        if str(exc).startswith(
            "com.openexchange.admin.rmi.exceptions.NoSuchObjectException",
        ):
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


def update_group_queue(dn):
    raise NotImplementedError("Needs to be overwritten by another function")


def is_ox_group(attr: Dict[str, Any]) -> bool:
    value = attr.get("isOxGroup")
    return value in {"OK", True}


def is_ox_user(attr: Dict[str, Any]) -> bool:
    value = attr.get("isOxUser")
    return value in {"OK", True}


def normalized_dn(dn: str) -> str:
    """Returns the given DN in the format that it should be used (normalized, lowercase)"""
    if dn:
        return ldap.dn.dn2str(ldap.dn.str2dn(dn.lower()))


# def get_ox_version() -> [int]:
#     """Returns the version of the OX server. Note that
#     this on itself requires OX 8. Therefore, this function
#     may return None"""
#     global _OX_VERSION
#     if _OX_VERSION is not False:
#         return _OX_VERSION
#     UtilService = get_ox_soap_service_class("UtilService")
#     try:
#         version = UtilService().get_version()
#         logger.info("OX Version is: %s", version)
#         _OX_VERSION = [int(bit) for bit in version.split('.')]  # [8, 37, 69]
#     except Exception as exc:
#         _OX_VERSION = None
#         logger.warning("Cannot determine OX Version. Probably OX 7?")
#     return _OX_VERSION
