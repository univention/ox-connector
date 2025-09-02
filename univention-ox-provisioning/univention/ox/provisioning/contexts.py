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

from univention.ox.soap.backend_base import get_ox_integration_class
from univention.ox.provisioning.helpers import get_obj_by_name_from_ox

Context = get_ox_integration_class("SOAP", "Context")
logger = logging.getLogger("listener")


def context_from_attributes(attributes):
    context = Context(id=attributes["contextid"])
    update_context(context, attributes)
    return context


def update_context(context, attributes):
    context.max_quota = attributes.get("oxQuota")
    context.name = attributes["name"]


def context_exists(obj):
    if obj.attributes is None:
        # before delete
        context_id = obj.old_attributes["contextid"]
    else:
        # before create
        context_id = obj.attributes["contextid"]
    return bool(get_obj_by_name_from_ox(Context, context_id, None))


def create_context(obj):
    logger.info(f"Creating {obj}")
    if context_exists(obj):
        if obj.old_attributes is None:
            obj.old_attributes = deepcopy(obj.attributes)
            logger.warning(
                "Found in DB but had no old attributes. Using new ones as old...",
            )
        logger.info(f"{obj} exists. Modifying instead...")
        return modify_context(obj)
    context = context_from_attributes(obj.attributes)
    context.create()


def modify_context(obj):
    logger.info(f"Modifying {obj}")
    if obj.old_attributes:
        context = context_from_attributes(obj.old_attributes)
        update_context(context, obj.attributes)
    else:
        logger.info(f"{obj} has no old data. Resync?")
        context = context_from_attributes(obj.attributes)
    context.modify()


def delete_context(obj):
    logger.info(f"Deleting {obj}")
    if not context_exists(obj):
        logger.info(f"{obj} does not exist. Doing nothing...")
        return
    context = context_from_attributes(obj.old_attributes)
    context.remove()
    obj.attributes = None  # make obj.was_deleted() return True
