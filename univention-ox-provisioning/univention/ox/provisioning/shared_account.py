#
# Copyright 2026 Univention GmbH
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

from lancelog import logger
from copy import deepcopy
from urllib.parse import urlparse


from univention.ox.provisioning.helpers import (
    Skip,
    get_context_id,
    get_obj_by_name_from_ox,
)
from univention.ox.provisioning.groups import get_group_id
import univention.ox.provisioning.helpers

from univention.ox.soap.backend_base import get_ox_integration_class
from univention.ox.soap.types import Types

from univention.ox.soap.config import (
    DEFAULT_IMAP_SERVER,
    DEFAULT_LANGUAGE,
    DEFAULT_SMTP_SERVER,
    LOCAL_TIMEZONE,
    SHARED_ACCOUNT_IDENTIFIER,
)

SharedAccount = get_ox_integration_class("SOAP", "SharedAccount")


class ConvertUserToSharedAccountException(Exception):
    """Raised when converting cannot be performed"""

    pass


def is_enabled():
    Types()  # to automatically set OX_ENABLE_SHARED_ACCOUNT

    # We can only import it after calling Types, because Types can change this variable
    from univention.ox.soap.config import OX_ENABLE_SHARED_ACCOUNT

    return str(OX_ENABLE_SHARED_ACCOUNT).lower() == "true"


def _get_name(attributes):
    return (
        attributes.get("oxDbName")
        or attributes.get(SHARED_ACCOUNT_IDENTIFIER)
        or attributes.get("name")
    )


def update_shared_account(shared_account, attributes):
    shared_account.context_id = get_context_id(attributes)
    shared_account.name = _get_name(attributes)
    shared_account.display_name = attributes.get("displayName")
    shared_account.primaryEmail = attributes.get("mailPrimaryAddress")
    shared_account.email1 = shared_account.primaryEmail
    shared_account.password = "dummy"  # required by WSDL to be set. But not used; Shared Accounts cannot log in. And even if, we always expect LDAP integration, so a password in OX' database is always ignored

    shared_account.language = DEFAULT_LANGUAGE
    shared_account.timezone = LOCAL_TIMEZONE

    imap_url = urlparse(DEFAULT_IMAP_SERVER)
    shared_account.imap_port = imap_url.port  # 143
    shared_account.imap_schema = imap_url.scheme + "://"  # "imap://"
    shared_account.imap_server = imap_url.hostname

    smtp_url = urlparse(DEFAULT_SMTP_SERVER)
    shared_account.smtp_port = smtp_url.port  # 587
    shared_account.smtp_schema = smtp_url.scheme + "://"  # "smtp://"
    shared_account.smtp_server = smtp_url.hostname


def _get_permission(obj_id):
    shared_account_permission = univention.ox.provisioning.helpers.get_old_obj(
        None,
        obj_id=obj_id,
    )
    if not shared_account_permission:
        return
    mail_config = shared_account_permission.attributes.get("mail")
    calendar_config = shared_account_permission.attributes.get("calendar")
    capabilities = []
    for cap in [
        "sendAs",
        "sendOnBehalf",
        "snippets",
        "writeSnippets",
        "manageSieve",
        "writeJSlob",
    ]:
        if shared_account_permission.attributes.get(cap) in {"TRUE", True}:
            capabilities.append(cap)
    return mail_config, calendar_config, tuple(sorted(capabilities))


def create_permissions(shared_account, obj):
    from univention.ox.provisioning import get_group_objs

    logger.info("Creating permissions for shared account", shared_account=obj)

    univention.ox.provisioning.helpers.remove_complete_relation(
        obj.entry_uuid,
        "permitted",
    )
    permissions = {}
    required_permission_map = {}

    for user_uoid, permission_uoid in obj.attributes.get("users", []):
        univention.ox.provisioning.helpers.add_relation(
            obj.entry_uuid,
            "oxmail/shared_account",
            user_uoid,
            "users/user",
            "permitted",
        )
        univention.ox.provisioning.helpers.add_relation(
            obj.entry_uuid,
            "oxmail/shared_account",
            permission_uoid,
            "oxmail/shared_account_permission",
            "permitted",
        )

        if permission_uoid not in permissions:
            permission = _get_permission(permission_uoid)
            permissions[permission_uoid] = permission
        else:
            permission = permissions[permission_uoid]
        if not permission:
            logger.warning(
                "Permission reference found on shared account, but it is unknown. Skipping...",
                permission=permission_uoid,
                shared_account=obj,
            )
            continue

        user = univention.ox.provisioning.helpers.get_old_obj(
            None,
            obj_id=user_uoid,
        )
        if not user:
            logger.warning(
                "User reference found on shared account, but it is unknown. Skipping...",
                user=user_uoid,
                shared_account=obj,
            )
            continue
        db_id = user.attributes.get("oxDbId")
        context_id = user.attributes.get("oxContext")

        if not db_id:
            logger.warning(
                "User has no oxDbId to use for Shared Account Permissions. Skipping...",
                user=user_uoid,
            )
            continue

        users, groups = required_permission_map.get(
            (context_id, permission),
            ([], []),
        )
        users.append(db_id)
        required_permission_map[(context_id, permission)] = users, groups

    for group_uoid, permission_uoid in obj.attributes.get("groups", []):
        univention.ox.provisioning.helpers.add_relation(
            obj.entry_uuid,
            "oxmail/shared_account",
            group_uoid,
            "groups/group",
            "permitted",
        )
        univention.ox.provisioning.helpers.add_relation(
            obj.entry_uuid,
            "oxmail/shared_account",
            permission_uoid,
            "oxmail/shared_account_permission",
            "permitted",
        )

        if permission_uoid not in permissions:
            permission = _get_permission(permission_uoid)
            permissions[permission_uoid] = permission
        else:
            permission = permissions[permission_uoid]
        if not permission:
            logger.warning(
                "Permission reference found on shared account, but it is unknown. Skipping...",
                permission=permission_uoid,
                shared_account=obj,
            )
            continue

        group = univention.ox.provisioning.helpers.get_old_obj(
            None,
            obj_id=group_uoid,
        )
        if not group:
            logger.warning(
                "Group reference found on shared account, but it is unknown. Skipping...",
                group=group_uoid,
                shared_account=obj,
            )
            continue

        for group_obj in get_group_objs(group):
            db_id = get_group_id(group_obj)
            if not db_id:
                logger.warning(
                    "Group has no oxDbId to use for Shared Account Permissions. Skipping...",
                    group=group_uoid,
                )
                continue
            context_id = group_obj.attributes["oxContext"]

            users, groups = required_permission_map.get(
                (context_id, permission),
                ([], []),
            )
            groups.append(db_id)
            required_permission_map[(context_id, permission)] = (
                users,
                groups,
            )

    if not required_permission_map:
        required_permission_map[
            (shared_account.context_id, ("none", "none", ()))
        ] = ([], [])
    shared_account.set_permissions(
        {
            "context": context_id,
            "users": users,
            "groups": groups,
            "mail": permission[0],
            "calendar": permission[1],
            "capabilities": permission[2],
        }
        for (context_id, permission), (
            users,
            groups,
        ) in required_permission_map.items()
    )


def create_shared_account(obj):
    if not is_enabled():
        return
    logger.info("Creating object", object=obj)
    shared_account = SharedAccount()
    update_shared_account(shared_account, obj.attributes)
    if get_obj_by_name_from_ox(
        SharedAccount,
        shared_account.context_id,
        shared_account.name,
    ):
        obj.old_attributes = deepcopy(obj.attributes)
        logger.info("Object exists. Modifying instead...", object=obj)
        return modify_shared_account(obj)
    shared_account.create()
    obj.set_attr("oxDbId", shared_account.id)
    obj.set_attr("oxDbName", shared_account.name)
    create_permissions(shared_account, obj)


def modify_shared_account(obj):
    if not is_enabled():
        return
    logger.info("Modifying object", object=obj)
    shared_account = SharedAccount()
    old_shared_account = univention.ox.provisioning.helpers.get_old_obj(
        None,
        obj_id=obj.entry_uuid,
    )
    if old_shared_account and old_shared_account.object_type == "users/user":
        logger.info("... was a user before! Converting to shared account...")
        try:
            ox_context = get_context_id(obj.old_attributes)
        except Skip:
            raise ConvertUserToSharedAccountException(
                "Tasked to convert old user to new shared account. Cannot continue due to missing Context ID in user data.",
            )
        user_id = obj.old_attributes.get("oxDbId")
        if not user_id:
            raise ConvertUserToSharedAccountException(
                "Tasked to convert old user to new shared account. Cannot continue due to missing DB ID in user data.",
            )
        SharedAccount.service(ox_context).convert_user_to_shared_account(
            {"id": user_id},
        )
        shared_account.id = user_id
        logger.info(
            "... done, converted to SharedAccount. Now continuing setting attributes",
        )
    else:
        shared_account.id = obj.old_attributes.get("oxDbId")
    update_shared_account(shared_account, obj.attributes)
    if not shared_account.id:
        existing_obj = get_obj_by_name_from_ox(
            SharedAccount,
            shared_account.context_id,
            shared_account.name,
        )
        if existing_obj:
            shared_account.id = existing_obj.id
        else:
            logger.info(
                "Object does not yet exist. Creating instead...",
                object=obj,
            )
            return create_shared_account(obj)
    shared_account.modify()
    obj.set_attr("oxDbId", shared_account.id)
    obj.set_attr("oxDbName", shared_account.name)
    create_permissions(shared_account, obj)


def delete_shared_account(obj):
    if not is_enabled():
        return
    logger.info("Deleting object", object=obj)
    shared_account = SharedAccount()
    shared_account.id = obj.old_attributes.get("oxDbId")
    update_shared_account(shared_account, obj.old_attributes)
    if shared_account.id:
        shared_account.remove()
        logger.info(
            "Shared account was deleted",
            shared_account=shared_account.id,
        )


def modify_shared_account_permission(obj):
    for src_uuid in univention.ox.provisioning.helpers.search_src_of_relation(
        obj.entry_uuid,
        "permitted",
    ):
        # TODO: rename this function... it can re-evaluate all kinds of old objects
        univention.ox.provisioning.helpers.update_group_queue(src_uuid)
