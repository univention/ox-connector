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


from lancelog import logger
from copy import deepcopy

from univention.ox.soap.backend_base import get_ox_integration_class
import univention.ox.provisioning.helpers
from univention.ox.provisioning.helpers import (
    get_db_id,
    get_obj_by_name_from_ox,
    is_ox_group,
)
from univention.ox.soap.config import GROUP_IDENTIFIER

Group = get_ox_integration_class("SOAP", "Group")


def group_from_attributes(attributes, group_name, group_id=None):
    group = Group(id=group_id)
    if attributes:
        context_id = attributes["oxContext"]
        group.context_id = context_id
        update_group(group, attributes, group_name)
    return group


def _get_name(attributes):
    return (
        attributes.get("oxDbGroupname")
        or attributes.get(GROUP_IDENTIFIER)
        or attributes.get("name")
    )


def get_group_name(group):
    if GROUP_IDENTIFIER == "entryUUID":
        return group.entry_uuid
    else:
        return _get_name(group.attributes)


def update_group(group, attributes, group_name):
    group.name = group_name
    group.display_name = group.name
    if not is_ox_group(attributes):
        # no need to search anything...
        # specifically skip "Domain Users"... this would be expensive
        return
    members = []
    logger.info("Retrieving members...")
    for user in attributes.get("users"):
        try:
            user_id = get_db_id(user)
            if user_id:
                logger.info("found user", id=user_id)
                members.append(user_id)
        except Exception:
            logger.warning(
                "skipping user. Object not found in listener/old directory.",
                user=user,
            )
    group.members = members


def get_group_id(obj):
    if obj.old_attributes is not None:
        # before delete
        context_id = obj.old_attributes["oxContext"]
        groupname = _get_name(obj.old_attributes)
    else:
        # before create
        context_id = obj.attributes["oxContext"]
        groupname = get_group_name(obj)
    # ignore groups with name "users" (Bug #35821)
    if groupname.lower() == "users":
        logger.info('Ignoring group', group=groupname)
        return None
    group = get_obj_by_name_from_ox(Group, context_id, groupname)
    if group:
        return group.id


def create_group(obj):
    logger.info("Creating object", object=obj)
    if not is_ox_group(obj.attributes):
        logger.info("Object is no OX group. Deleting instead...", object=obj)
        return delete_group(obj)
    if get_group_id(obj):
        if obj.old_attributes is None:
            obj.old_attributes = deepcopy(obj.attributes)
            logger.warning(
                "Found in DB but had no old attributes. Using new ones as old...",
            )
        logger.info("Object exists. Modifying instead...", object=obj)
        return modify_group(obj)
    group = group_from_attributes(obj.attributes, get_group_name(obj))
    if not group.members:
        logger.info("Object is empty. Deleting instead...", object=obj)
        return delete_group(obj)
    # ignore groups with name "users" (Bug #35821)
    if group.name == "users":
        return
    group.create()
    obj.set_attr("oxDbGroupname", group.name)
    for src_uuid in univention.ox.provisioning.helpers.search_src_of_relation(
        obj.entry_uuid,
        "permitted",
    ):
        # TODO: rename this function... it can re-evaluate all kinds of old objects
        univention.ox.provisioning.helpers.update_group_queue(src_uuid)


def modify_group(obj):
    logger.info("Modifying object", object=obj)
    if not is_ox_group(obj.attributes):
        logger.info("Object is no OX group. Deleting instead...", object=obj)
        return delete_group(obj)
    group_id = get_group_id(obj)
    if not group_id:
        logger.info(
            "Object does not yet exist. Creating instead...",
            object=obj,
        )
        return create_group(obj)
    if obj.old_attributes:
        if not is_ox_group(obj.old_attributes):
            logger.info(
                "Object was no OX group before... that should not be the case. Modifying anyway...",
                object=obj,
            )
        group = group_from_attributes(
            obj.old_attributes,
            _get_name(obj.old_attributes),
            group_id,
        )
        update_group(group, obj.attributes, get_group_name(obj))
    else:
        logger.info("Object has no old data. Resync?", object=obj)
        group = group_from_attributes(
            obj.attributes,
            get_group_name(obj),
            group_id,
        )
    if not group.members:
        logger.info("Object is empty. Deleting instead...", object=obj)
        return delete_group(obj)
    group.modify()
    obj.set_attr("oxDbGroupname", group.name)


def delete_group(obj):
    logger.info("Deleting object", object=obj)
    group_id = get_group_id(obj)
    if not group_id:
        logger.info("Object does not exist. Doing nothing...", object=obj)
        return
    group = group_from_attributes(
        obj.old_attributes,
        _get_name(obj.old_attributes),
        group_id,
    )
    group.remove()
    obj.attributes = None  # make obj.was_deleted() return True
