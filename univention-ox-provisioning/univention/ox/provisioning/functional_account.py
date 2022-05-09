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
from univention.ox.provisioning.helpers import get_context_id, get_obj_by_name_from_ox, get_db_id

FunctionalAccount = get_ox_integration_class("SOAP", "SecondaryAccount")
logger = logging.getLogger("listener")


def functional_account_from_attributes(attributes, entry_uuid):
    context_id = get_context_id(attributes)
    functional_account = FunctionalAccount(context_id=context_id)
    update_functional_account(functional_account, attributes, entry_uuid)
    return functional_account


def update_functional_account(functional_account, attributes, entry_uuid):
    functional_account.name = attributes.get("name")
    functional_account.personal = attributes.get("personal")
    functional_account.email = attributes.get("mailPrimaryAddress")
    functional_account.login = entry_uuid
    functional_account.mail_endpoint_source = "primary"


def update_functional_account_members(functional_account, attributes):
    functional_account.users = [{"id": db_id} for dn in attributes.get("users") if (db_id := get_db_id(dn))]
    functional_account.groups = [{"id": db_id} for dn in attributes.get("groups") if (db_id := get_db_id(dn))]


def get_functional_account_id(attributes):
    context_id = get_context_id(attributes)
    name = attributes.get("name")
    functional_account = get_obj_by_name_from_ox(FunctionalAccount, context_id, name)
    if functional_account:
        return functional_account.id


def create_functional_account(obj):
    logger.info(f"Creating {obj}")
    logger.info("Start off by removing the old one (maybe remnants?)")
    if obj.old_attributes is None:
        obj.old_attributes = deepcopy(obj.attributes)
    delete_functional_account(deepcopy(obj))
    functional_account = functional_account_from_attributes(obj.attributes, obj.entry_uuid)
    update_functional_account_members(functional_account, obj.attributes)
    logger.info(f"Got {functional_account!r}")
    if not functional_account.users and not functional_account.groups:
        logger.info("Account is empty! Not creating...")
        return
    functional_account.create()


def modify_functional_account(obj):
    logger.info(f"Modifying {obj}")
    logger.info("Modify is like creating a new one...")
    create_functional_account(obj)


def delete_functional_account(obj):
    logger.info(f"Deleting {obj}")
    functional_account = functional_account_from_attributes(obj.old_attributes, obj.entry_uuid)
    functional_account.remove()
    obj.attributes = None  # make obj.was_deleted() return True
