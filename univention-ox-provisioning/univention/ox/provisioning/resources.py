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


import logging
from copy import deepcopy

from univention.ox.backend_base import get_ox_integration_class
from univention.ox.provisioning.helpers import get_context_id

Resource = get_ox_integration_class("SOAP", "Resource")
logger = logging.getLogger("listener")


def resource_from_attributes(attributes, resource_id=None):
    context_id = get_context_id(attributes)
    resource = Resource(id=resource_id, context_id=context_id)
    update_resource(resource, attributes)
    return resource


def update_resource(resource, attributes):
    resource.name = attributes.get("name")
    resource.description = attributes.get("description")
    resource.display_name = attributes.get("displayname")
    resource.email = attributes.get("resourceMailAddress")


def get_resource_id(attributes):
    context_id = get_context_id(attributes)
    name = attributes.get("name")
    resources = Resource.list(context_id, pattern=name)
    if not resources:
        return None
    assert len(resources) == 1
    return resources[0].id


def create_resource(obj):
    logger.info(f"Creating {obj}")
    if get_resource_id(obj.attributes):
        if obj.old_attributes is None:
            obj.old_attributes = deepcopy(obj.attributes)
            logger.warning("Found in DB but had no old attributes. Using new ones as old...")
        logger.info(f"{obj} exists. Modifying instead...")
        return modify_resource(obj)
    resource = resource_from_attributes(obj.attributes)
    resource.create()


def modify_resource(obj):
    logger.info(f"Modifying {obj}")
    resource_id = get_resource_id(obj.old_attributes)
    if not resource_id:
        logger.info(f"{obj} does not yet exist. Creating instead...")
        return create_resource(obj)
    if obj.old_attributes:
        old_context = get_context_id(obj.old_attributes)
        new_context = get_context_id(obj.attributes)
        if old_context != new_context:
            logging.info(f"Changing context: {old_context} -> {new_context}")
            already_existing_resource_id = get_resource_id(obj.attributes)
            if already_existing_resource_id:
                logger.warning(
                    f"{obj} was found in context {old_context} with ID {resource_id} and in {new_context} with {already_existing_resource_id}. This should not happen. Will delete in {old_context} and modify in {new_context}"  # noqa
                )
                delete_resource(deepcopy(obj))
            else:
                create_resource(obj)
                return delete_resource(deepcopy(obj))
        resource = resource_from_attributes(obj.old_attributes, resource_id)
        update_resource(resource, obj.attributes)
    else:
        logger.info(f"{obj} has no old data. Resync?")
        resource = resource_from_attributes(obj.attributes, resource_id)
    resource.modify()


def delete_resource(obj):
    logger.info(f"Deleting {obj}")
    resource_id = get_resource_id(obj.old_attributes)
    if not resource_id:
        logger.info(f"{obj} does not exist. Doing nothing...")
        return
    resource = resource_from_attributes(obj.old_attributes, resource_id)
    resource.remove()
    obj.attributes = None  # make obj.was_deleted() return True
