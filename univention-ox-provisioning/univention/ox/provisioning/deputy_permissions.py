#
# Copyright 2025 Univention GmbH
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

from univention.ox.provisioning.helpers import (
    get_db_id,
)

from univention.ox.soap.backend_base import get_ox_integration_class
import univention.ox.soap.config

DeputyPermission = get_ox_integration_class("SOAP", "DeputyPermission")

logger = logging.getLogger("listener")


# Util = get_ox_integration_class("SOAP", "Util")
# def fitting_ox_version() -> bool:
#     # function get_version of Util is available since ox version 8.35.276
#     # also the deputy permission feature is feature complete in this version
#     try:
#         version = Util.service().get_version()
#     except Exception as exc:
#         logger.warning(
#             f"The Appsuite version is too small for using the deputy feature: {exc}"
#         )
#         return False
#     ret = float(version) >= float("8.35.276")
#     return ret


def is_enabled():
    return str(univention.ox.soap.config.OX_ENABLE_DEPUTY_PERMISSIONS).lower() in ["true"]


def get_permission_representation_from_oxDeputyPermissionGivenTo(
    permission, deputy_id
):
    """UDM: ["user01", "02400", "02400", ""]
    -> SOAP {userId: int, sendOnBehalfOf: bool, modulePermissions: list}
    """
    sendOnBehalfOf = permission[3] == "1"
    mail = permission[1]
    calendar = permission[2]
    mailPermission = {
        "moduleId": "mail",
        "admin": mail[0],
        "folderPermission": int(mail[1]),
        "readPermission": int(mail[2]),
        "writePermission": int(mail[3]),
        "deletePermission": int(mail[4]),
    }
    calendarPermission = {
        "moduleId": "calendar",
        "admin": calendar[0] == "1",
        "folderPermission": int(calendar[1]),
        "readPermission": int(calendar[2]),
        "writePermission": int(calendar[3]),
        "deletePermission": int(calendar[4]),
    }
    modulePermissions = [mailPermission, calendarPermission]
    ret = {
        "userId": deputy_id,
        "sendOnBehalfOf": sendOnBehalfOf,
        "modulePermissions": modulePermissions,
    }
    return ret


def set_deputy_permissions(obj, context_id):
    """Compare old and new obj regarding deputy permissions and do action
    If there was an context move we removed the permissions before in users.py
    """
    if not is_enabled():
        return

    user_id = obj.attributes.get("oxDbId") or get_db_id(obj.distinguished_name)
    if not user_id:
        logger.info(
            f"No user_id found for {obj.distinguished_name}. Unable to create deputy permissions."
        )
        return

    deputy_service = DeputyPermission.service(context_id)

    revoked = False
    if obj.old_attributes and obj.old_attributes.get("oxDeputyPermissionGivenTo", []):
        # we had set oxDeputyPermissionGivenTo, we need to revoke all
        # to have a fresh start
        delete_deputy_permissions(obj, context_id)
        revoked = True

    if permissions := obj.attributes.get("oxDeputyPermissionGivenTo", []):
        if not revoked:
            # we had no oxDeputyPermissionGivenTo previously
            # but we need to have a fresh start in case some exist from
            # granting manually
            delete_deputy_permissions(obj, context_id)
        for permission in permissions:
            deputy_dn = permission[0]
            deputy_user_id = get_db_id(deputy_dn)
            if not deputy_user_id:
                logger.info(
                    f"No user_id found for {deputy_dn}. Unable to create permission granted by {obj.distinguished_name}."
                )
                continue
            try:
                deputy_permission = (
                    get_permission_representation_from_oxDeputyPermissionGivenTo(
                        permission, deputy_user_id
                    )
                )
                db_id = deputy_service.grant(
                    user=user_id, deputy_permission=deputy_permission
                )
                logger.info(
                    f"Created deputy permission given to {deputy_dn} from {obj.distinguished_name} ({db_id})"
                )
            except Exception as e:
                logger.warning(
                    f"Error creating deputy permission given to {deputy_dn} from {obj.distinguished_name}: {e}"
                )
        try:
            deputy_service.block_manual(user_id)
        except Exception as e:
            logger.warning(
                f"Error blocking {obj.distinguished_name} from granting deputy permissions: {e}"
            )
        else:
            logger.info(
                f"{obj.distinguished_name} is now blocked from granting deputy permissions autonomously."
            )


def delete_deputy_permissions(obj, context_id):
    """Delete all deputy permissions regarding the user
    if user is removed or moved in context
    """
    if not is_enabled():
        return

    if obj.attributes and obj.attributes.get("oxDbId"):
        user_id = obj.attributes.get("oxDbId")
    else:
        user_id = get_db_id(obj.distinguished_name)
    if not user_id:
        logger.info(
            f"No user_id found for {obj.distinguished_name}. Unable to delete deputy permissions."
        )
        return

    deputy_service = DeputyPermission.service(context_id)

    try:
        deputy_service.revoke_all(user_id)
    except Exception as e:
        logger.warning(
            f"Error deleting all deputy permissions granted by {obj.distinguished_name}: {e}"
        )
    else:
        logger.info(
            f"Revoked all deputy permissions granted by {obj.distinguished_name}."
        )
        try:
            deputy_service.unblock_manual(user_id)
        except Exception as e:
            logger.warning(
                f"Error unblocking {obj.distinguished_name} from granting deputy permissions: {e}"
            )
        else:
            logger.info(
                f"{obj.distinguished_name} may now grant deputy permissions autonomously."
            )
