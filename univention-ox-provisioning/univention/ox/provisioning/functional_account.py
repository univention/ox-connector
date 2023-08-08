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
import re

from univention.ox.soap.backend_base import get_ox_integration_class
from univention.ox.soap.config import FUNCTIONAL_ACCOUNT_LOGIN
import univention.ox.provisioning.helpers
from univention.ox.provisioning.helpers import get_context_id, get_obj_by_name_from_ox, get_db_id, get_db_uid

FunctionalAccount = get_ox_integration_class("SOAP", "SecondaryAccount")
logger = logging.getLogger("listener")

class InvalidSetting(Exception):
    """Raise when one app setting is invalid"""

    pass


def configure_functional_account_login(app_setting):
    INVALID_FORMAT_ERR_MSG = "The format used for OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE app setting is invalid"
    MISSING_FA_ENTRY_UUID_ERR_MSG = "The functional account entry uuid is required in the OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE app setting"

    try:
        FUNCTIONAL_ACCOUNT_LOGIN_FORMAT = []
        prev_end = 0
        for f in re.finditer("({{\w+}})([:;+]?)*", app_setting):
            if f.span(0)[0] != prev_end:
                raise InvalidSetting(INVALID_FORMAT_ERR_MSG)
            prev_end = f.span(0)[1]
            FUNCTIONAL_ACCOUNT_LOGIN_FORMAT.append((f.group(1)[2:-2], f.group(0).lstrip(f.group(1))))
        if prev_end != len(app_setting):
            raise InvalidSetting(INVALID_FORMAT_ERR_MSG)
    except ValueError:
        raise InvalidSetting(INVALID_FORMAT_ERR_MSG)
    else:
        if not any(x[0] == "fa_entry_uuid" for x in FUNCTIONAL_ACCOUNT_LOGIN_FORMAT):
            raise InvalidSetting(MISSING_FA_ENTRY_UUID_ERR_MSG)
    return FUNCTIONAL_ACCOUNT_LOGIN_FORMAT


FUNCTIONAL_ACCOUNT_LOGIN_FORMAT = configure_functional_account_login(FUNCTIONAL_ACCOUNT_LOGIN)


def get_functional_account_login(dn, fa):
    value = ""
    obj = univention.ox.provisioning.helpers.get_old_obj(dn)
    for attribute, separator in FUNCTIONAL_ACCOUNT_LOGIN_FORMAT:
        if attribute == "fa_entry_uuid":
            value += fa.entry_uuid
        elif attribute == "entry_uuid":
            value += obj.entry_uuid
        elif attribute == "dn":
            value += obj.distinguished_name
        else:
            value += obj.attributes[attribute]
        value += separator
    return value


def functional_account_from_attributes(attributes):
    context_id = get_context_id(attributes)
    functional_account = FunctionalAccount(context_id=context_id)
    update_functional_account(functional_account, attributes)
    return functional_account


def update_functional_account(functional_account, attributes):
    functional_account.name = attributes.get("name")
    functional_account.personal = attributes.get("personal")
    functional_account.email = attributes.get("mailPrimaryAddress")
    functional_account.mail_endpoint_source = "primary"


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
    if len(obj.attributes.get("users")) == 0:
        logger.info("Account is empty! Not creating...")
        return
    for dn in obj.attributes.get("users"):    
        functional_account = functional_account_from_attributes(obj.attributes)
        functional_account.users = [get_db_id(dn)]
        functional_account.login = obj.entry_uuid
        functional_account.login = get_functional_account_login(dn, obj)
        functional_account.groups = [] # groups are disabled in umc, this should be changed if it is enabled again.
        if functional_account.users[0]:
            functional_account.create()


def modify_functional_account(obj):
    logger.info(f"Modifying {obj}")
    logger.info("Modify is like creating a new one...")
    create_functional_account(obj)


def delete_functional_account(obj):
    logger.info(f"Deleting {obj}")
    functional_account = functional_account_from_attributes(obj.old_attributes)
    functional_account.remove()
    obj.attributes = None  # make obj.was_deleted() return True
