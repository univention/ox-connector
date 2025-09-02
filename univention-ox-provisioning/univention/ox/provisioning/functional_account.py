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
from univention.ox.provisioning.helpers import (
    get_context_id,
    get_obj_by_name_from_ox,
    get_db_id,
)

FunctionalAccount = get_ox_integration_class("SOAP", "SecondaryAccount")
logger = logging.getLogger("listener")


class InvalidSetting(Exception):
    """Raise when one app setting is invalid"""


def configure_functional_account_login(app_setting):
    try:
        functional_account_login_format = [
            f.span() for f in re.finditer(r"{{\w+}}", app_setting)
        ]
    except ValueError as exc:
        raise InvalidSetting(
            "Invalid format of functional account login "
            "template: {app_setting!r}",
        ) from exc
    return sorted(functional_account_login_format, reverse=True)


def get_functional_account_login(dn, fa):
    functional_account_login_format = configure_functional_account_login(
        FUNCTIONAL_ACCOUNT_LOGIN,
    )
    value = FUNCTIONAL_ACCOUNT_LOGIN
    obj = univention.ox.provisioning.helpers.get_old_obj(dn)
    for span in functional_account_login_format:
        attr_name = value[span[0] + 2 : span[1] - 2]
        if attr_name == "fa_entry_uuid":
            value = value.replace(value[span[0] : span[1]], fa.entry_uuid)
        elif attr_name == "fa_email_address":
            value = value.replace(
                value[span[0] : span[1]],
                fa.attributes["mailPrimaryAddress"],
            )
        elif attr_name == "entry_uuid":
            value = value.replace(value[span[0] : span[1]], obj.entry_uuid)
        elif attr_name == "dn":
            value = value.replace(
                value[span[0] : span[1]],
                obj.distinguished_name,
            )
        else:
            value = value.replace(
                value[span[0] : span[1]],
                obj.attributes[attr_name],
            )
    logger.info(f"format functional account login value ({value})")
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
    functional_account = get_obj_by_name_from_ox(
        FunctionalAccount,
        context_id,
        name,
    )
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
        # groups are disabled in umc,
        # this should be changed if it is enabled again.
        functional_account.groups = []
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
