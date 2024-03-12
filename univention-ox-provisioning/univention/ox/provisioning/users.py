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


import json
import datetime
import logging
from copy import deepcopy
from urllib.parse import urlparse
import imghdr
import base64

import univention.ox.provisioning.helpers
from univention.ox.provisioning.default_user_mapping import DEFAULT_USER_MAPPING
from univention.ox.soap.backend_base import get_ox_integration_class
from univention.ox.provisioning.accessprofiles import (
    empty_rights_profile,
    get_access_profile,
)
from univention.ox.provisioning.helpers import Skip, get_context_id, get_obj_by_name_from_ox
from univention.ox.soap.config import (
    DEFAULT_IMAP_SERVER,
    DEFAULT_LANGUAGE,
    DEFAULT_SMTP_SERVER,
    IMAP_LOGIN,
    LOCAL_TIMEZONE,
    get_context_admin_user,
    USER_IDENTIFIER,
)

User = get_ox_integration_class("SOAP", "User")
UserCopy = get_ox_integration_class("SOAP", "UserCopy")
Group = get_ox_integration_class("SOAP", "Group")
logger = logging.getLogger("listener")


def str2isodate(text):  # type: (str) -> str
    exc1 = exc2 = None
    try:
        the_date = datetime.datetime.strptime(text, "%Y-%m-%d")
        return "{:%Y-%m-%d}".format(the_date)
    except (TypeError, ValueError) as exc:
        exc1 = exc
    try:
        the_date = datetime.datetime.strptime(text, "%d.%m.%Y")
        return "{:%Y-%m-%d}".format(the_date)
    except (TypeError, ValueError) as exc:
        exc2 = exc
    raise ValueError(
        "Value {!r} in unknown date format or year before 1900 ({} {}).".format(
            text, exc1, exc2,
        ),
    )


def user_from_attributes(attributes, old_attributes, username, user_id=None, initial_values=False):
    user = User(id=user_id)
    if attributes:
        context_id = get_context_id(attributes)
        user.context_id = context_id
        update_user(user, attributes, old_attributes, username, initial_values)
    return user


def get_user_username(user):
    if USER_IDENTIFIER == "entryUUID":
        return user.entry_uuid
    else:
        return user.attributes.get(USER_IDENTIFIER)


def get_user_mapping():
    try:
        with open('/var/lib/univention-appcenter/apps/ox-connector/data/AttributeMapping.json', 'r') as fd:
            return json.loads(fd.read())
    except (OSError, ValueError, IOError):
        logger.info("Using default user attribute mapping")
        return DEFAULT_USER_MAPPING


def set_ox_property(user, ox_property, mapping, attributes):
    key = mapping.get("ldap_attribute")
    special_handling = mapping.get("special_handling")
    alternative_attributes = mapping.get("alternative_attributes")

    def image_attibute(x):
        if x:
            byte_image = base64.b64decode(x.encode('utf8'))
            content_type = imghdr.what(None, h=byte_image)
            if content_type == 'jpeg':
                content_type = 'image/jpeg'
            else:
                logger.warn(f"We only support jpeg images. Found {content_type!r}. Ignoring image...")
                content_type = None
            if content_type:
                setattr(user, ox_property+"ContentType", content_type)

        else:
            setattr(user, ox_property+"ContentType", "")
        return val

    def imap_server(x):
        imap_url = urlparse(DEFAULT_IMAP_SERVER)
        user.imap_port = imap_url.port  # 143
        user.imap_schema = imap_url.scheme + "://"  # "imap://"
        return x or imap_url.hostname

    def smtp_server(x):
        smtp_url = urlparse(DEFAULT_SMTP_SERVER)
        user.smtp_port = smtp_url.port  # 587
        user.smtp_schema = smtp_url.scheme + "://"  # "smtp://"
        return x or smtp_url.hostname

    def position_handle(x):
        pos = mapping.get("position")
        if x and pos:
            if len(x) > pos:
                return x[pos]
            else:
                return None
        return x

    def multivalue_handle(x):
        return x[0] if not mapping.get("multi_value") and isinstance(x, list) and x else x

    if not key:
        logger.info(f"ox property {ox_property} unset")
        return

    val = attributes.get(key)

    if not val and alternative_attributes:
        for attr in alternative_attributes:
            val = attributes.get(attr)
            if val:
                logger.info(f"Attribute {ox_property}. Using alternative ldap mapping {key} ...")
                break

    if not val and not mapping.get("nillable"):
        logger.warn(f"Attribute {ox_property} is None.")

    val = position_handle(val)
    val = multivalue_handle(val)

    handle =  {
        "DATE" : lambda x: str2isodate(x) if x else None,
        "IMAGE" : image_attibute,
        "IMAP_URL" : imap_server,
        "SMTP_URL" : smtp_server,
    }

    if special_handling != "DEFAULT":
        val = handle[special_handling](val)

    setattr(user, ox_property, val)

def update_user(user, attributes, old_attributes, username, initial_values=False):
    old_user = None
    if user.id and not initial_values:
        try:
            if old_attributes and get_context_id(old_attributes) != user.context_id:
                old_user = User.from_ox(get_context_id(old_attributes), obj_id=user.id)
            else:
                old_user = User.from_ox(user.context_id, obj_id=user.id)
        except Exception:
            pass

    user.context_admin = False
    user.name = username
    user.password = "dummy"
    user.gui_spam_filter_enabled = True

    attribute_mapping = get_user_mapping()
    for ox_property, mapping in attribute_mapping.items():
        set_ox_property(user, ox_property, mapping, attributes)


    user.primary_email = user.email1
    user.aliases = [user.email1] + (user.aliases or [])
    user.imap_login = IMAP_LOGIN.format(user.email1) if "{}" in IMAP_LOGIN else IMAP_LOGIN
    if old_user:
        user.default_sender_address = old_user.default_sender_address
    else:
        user.default_sender_address = user.primary_email
    if user.default_sender_address not in user.aliases:
        # The SOAP API will fail if the value of the default_sender_address is not one
        # of all the user's email addresses. Make sure we comply with this requirement
        user.default_sender_address = user.primary_email

    if initial_values:
        user.language = DEFAULT_LANGUAGE
    if initial_values:
        user.timezone = LOCAL_TIMEZONE

    if attributes.get("oxAccess", "none") != "none":
        user.mail_enabled = True
    else:
        user.mail_enabled = False



def set_user_rights(user, obj):
    access_rights = empty_rights_profile()

    user_access = obj.attributes.get("oxAccess")
    if user_access:
        access_profile = get_access_profile(user_access)
        if access_profile is None:
            logger.warning(
                f"Cannot find access profile {user_access!r}. Leaving access rights untouched!",
            )
            return
    else:
        access_profile = []
    for access_right in access_profile:
        if access_right in access_rights:
            access_rights[access_right] = True
    logger.info(f"Changing user {user.id} to profile {user_access}")

    user.service(user.context_id).change_by_module_access(
        {"id": user.id}, access_rights,
    )


def get_user_id(attributes, lookup_ox=True):
    if attributes.get("oxDbId"):
        return attributes["oxDbId"]
    if not lookup_ox:
        return
    context_id = get_context_id(attributes)
    username = attributes.get("username")
    if username == get_context_admin_user(context_id):
        raise Skip(
            f"Not touching {username} in context {context_id}: Is context admin!",
        )
    logger.info(f"Searching for {username} in context {context_id}")
    if not User.service(context_id).exists(User.service(context_id).Type(id=None, name=username)):
        return
    user = get_obj_by_name_from_ox(User, context_id, username)
    if user:
        return user.id


def create_user(obj, user_copy_service=False, user_id=None):
    logger.info(f"Creating {obj}")
    if obj.attributes.get("isOxUser", "Not") == "Not":
        logger.info(f"{obj} is no OX user. Deleting instead...")
        return delete_user(obj)
    try:
        if get_user_id(obj.attributes):
            if obj.old_attributes is None:
                obj.old_attributes = deepcopy(obj.attributes)
                logger.warning(
                    "Found in DB but had no old attributes. Using new ones as old...",
                )
            logger.info(f"{obj} exists. Modifying instead...")
            return modify_user(obj)
    except Skip:
        logger.warning(f"{obj} has no oxContext attribute. No modification. Consider adding an oxContext to it.")
        return
    user = user_from_attributes(obj.attributes, getattr(obj, 'old_attributes', None), get_user_username(obj), initial_values=True)
    if not user_copy_service:
        user.create()
    else:
        logger.info(f"Creating {obj} in context {user.context_id} using UserCopy")
        user_copy_service.copy_user(user={"id": user_id}, dest_ctx={"id": user.context_id})
        # Bug #56525 When changing the context and the username, the old
        # username is needed for the object search in the database because
        # the object hasn't been modified yet.
        user = get_obj_by_name_from_ox(User, user.context_id, obj.old_attributes.get("oxDbUsername") or obj.old_attributes.get("username"))
        update_user(user, obj.attributes, obj.old_attributes, get_user_username(obj))
        user.modify()
    obj.set_attr("oxDbId", user.id)
    obj.set_attr("oxDbUsername", user.name)
    set_user_rights(user, obj)
    logger.info("Looking for groups of this user to be created in the context id")
    for group in obj.attributes.get("groups", []):
        group_obj = univention.ox.provisioning.helpers.get_old_obj(group)
        if group_obj is None or group_obj.attributes is None:
            logger.warning(
                f"Dont know anything about {group}. Does it exist? Is it to be deleted? Skipping...",
            )
            continue
        if group_obj.attributes.get("isOxGroup", "Not") == "Not":
            logger.warning(f"{group} is no OX group. Skipping...")
            continue
        groupname = group_obj.attributes.get("name")
        group = get_obj_by_name_from_ox(Group, user.context_id, groupname)
        if not group:
            logger.info(
                f"Group {groupname} does not yet exist in {user.context_id}. Creating...",
            )
            group = Group(
                context_id=user.context_id,
                name=groupname,
                display_name=groupname,
                members=[user.id],
            )
            group.create()
        else:
            logger.info(f"Adding {user.id} to the members of {groupname}")
            if user.id not in group.members:
                group.members.append(user.id)
                group.modify()


def modify_user(obj):
    logger.info(f"Modifying {obj}")
    if obj.attributes.get("isOxUser", "Not") == "Not":
        logger.info(f"{obj} is no OX user. Deleting instead...")
        return delete_user(obj)
    try:
        user_id = get_user_id(obj.old_attributes)
    except Skip:
        logger.warning("Old %s has no context ID. Using new context ID instead...", obj)
        try:
            user_id = get_user_id(obj.attributes)
        except Skip:
            logger.warning(f"{obj} has no oxContext attribute. No modification. Consider adding an oxContext to it.")
            return
    if not user_id:
        logger.info(f"{obj} does not yet exist. Creating instead...")
        return create_user(obj)
    if obj.old_attributes:
        if obj.old_attributes.get("isOxUser", "Not") == "Not":
            logger.warning(
                f"{obj} was no OX user before... that should not be the case. Modifying anyway...",
            )
        try:
            old_context = get_context_id(obj.old_attributes)
        except Skip:
            old_context = get_context_id(obj.attributes)
            obj.old_attributes['oxContext'] = old_context
        try:
            new_context = get_context_id(obj.attributes)
        except Skip:
            logger.warning(
                f"{obj} has no oxContext. that should not be the case. Using old oxContext...",
            )
            obj.set_attr("oxContext", old_context)
            new_context = old_context
        if old_context != new_context:
            logging.info(f"Changing context: {old_context} -> {new_context}")
            already_existing_user_id = get_user_id(obj.attributes)
            if already_existing_user_id:
                logger.warning(
                    f"{obj} was found in context {old_context} with ID {user_id} and in {new_context} with {already_existing_user_id}. This should not happen. Will delete in {old_context} and modify in {new_context}"  # noqa
                )
                delete_user(deepcopy(obj))
            else:
                create_user(obj, user_copy_service=UserCopy().service(old_context), user_id=user_id)
                return delete_user(deepcopy(obj))
        user = user_from_attributes(obj.old_attributes, obj.old_attributes, obj.old_attributes.get("oxDbUsername") or obj.old_attributes.get("username"), user_id)
        user.context_id = new_context
        update_user(user, obj.attributes, obj.old_attributes, get_user_username(obj))
    else:
        logger.info(f"{obj} has no old data. Resync?")
        user = user_from_attributes(obj.attributes, None, get_user_username(obj), user_id)
    user.modify()
    obj.set_attr("oxDbId", user.id)
    obj.set_attr("oxDbUsername", user.name)
    set_user_rights(user, obj)


def delete_user(obj):
    logger.info(f"Deleting {obj}")
    if obj.old_attributes is None:
        logger.info("No attributes to work with. Doing nothing...")
        return
    user_id = get_user_id(obj.old_attributes)
    if not user_id:
        logger.info(f"{obj} does not exist. Doing nothing...")
        return
    user = user_from_attributes(obj.old_attributes, None, obj.old_attributes.get("oxDbUsername") or obj.old_attributes.get("username"), user_id)
    group_service = Group.service(user.context_id)
    soap_groups = group_service.list_groups_for_user({"id": user.id})
    user.remove()
    obj.attributes = None  # make obj.was_deleted() return True
    logger.info("User was deleted, searching for now empty groups")
    for soap_group in soap_groups:
        logger.info(
            f"Found group {soap_group.name} with {len(soap_group.members)} members",
        )
        soap_group.members.remove(user.id)
        if not soap_group.members:
            logger.info(f"Thus, deleting group {soap_group.id} in {user.context_id}...")
            group_service.delete(soap_group)
