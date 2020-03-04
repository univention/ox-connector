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
from pathlib import Path

from univention.ox.soap.config import NoContextAdminPassword

from univention.ox.provisioning.helpers import Skip, get_context_id
from univention.ox.provisioning.users import create_user, modify_user, delete_user
from univention.ox.provisioning.groups import create_group, modify_group, delete_group
from univention.ox.provisioning.resources import (
    create_resource,
    modify_resource,
    delete_resource,
)
from univention.ox.provisioning.contexts import (
    create_context,
    modify_context,
    delete_context,
)


logger = logging.getLogger("listener")
TEST_LOG_FILE = Path("/tmp/test.log")


def run(get_old_user_obj, obj):  # noqa: C901
    """This is your main function. Implement all your logic here"""
    if obj.object_type == "oxmail/oxcontext":
        if obj.was_added():
            create_context(obj)
        elif obj.was_modified():
            modify_context(obj)
        elif obj.was_deleted():
            delete_context(obj)
    try:
        if obj.object_type == "users/user":
            if obj.was_added():
                create_user(obj)
            elif obj.was_modified():
                modify_user(obj)
            elif obj.was_deleted():
                delete_user(obj)
        if obj.object_type == "groups/group":
            for new_obj in get_group_objs(obj, get_old_user_obj):
                if new_obj.was_added():
                    create_group(new_obj)
                elif new_obj.was_modified():
                    modify_group(new_obj)
                elif new_obj.was_deleted():
                    delete_group(new_obj)
        if obj.object_type == "oxresources/oxresources":
            if obj.was_added():
                create_resource(obj)
            elif obj.was_modified():
                modify_resource(obj)
            elif obj.was_deleted():
                delete_resource(obj)
    except Skip as exc:
        logger.warning(f"Skipping: {exc}")
    except NoContextAdminPassword as exc:
        logger.warning(
            f"Could not find admin password for context {exc.args[0]}. Ignoring this task"
        )

    # logging for tests
    if TEST_LOG_FILE.exists():
        with TEST_LOG_FILE.open("a") as fp:
            fp.write(f"{obj.dn}\n")


def get_group_objs(obj, get_old_user_obj):  # noqa: C901
    users = []
    ignored_group = True
    if obj.old_attributes:
        users.extend(obj.old_attributes.get("users"))
        if obj.old_attributes.get("isOxGroup", "Not") != "Not":
            logger.info(f"Group {obj.old_attributes['name']} was OX Group")
            ignored_group = False
    if obj.attributes:
        users.extend(obj.attributes.get("users"))
        if obj.attributes.get("isOxGroup", "Not") != "Not":
            logger.info(f"Group {obj.attributes['name']} will be OX Group")
            ignored_group = False
    if ignored_group:
        return
    contexts = []
    for user in users:
        user_obj = get_old_user_obj(user)
        if user_obj is None:
            logger.info(
                f"Group wants {user} as member. But the user is unknown. Ignoring..."
            )
            continue
        try:
            context = get_context_id(user_obj.attributes)
        except Skip:
            continue
        if context not in contexts:
            contexts.append(context)
    for context in contexts:
        new_obj = deepcopy(obj)
        if new_obj.old_attributes:
            new_obj.old_attributes["oxContext"] = context
        if new_obj.attributes:
            new_obj.attributes["oxContext"] = context
        logger.info(f"{obj} will be processed with context {context}")
        yield new_obj
