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


import datetime
import logging
from copy import deepcopy
from urllib.parse import urlparse

import univention.ox.provisioning.helpers
from univention.ox.backend_base import get_ox_integration_class
from univention.ox.provisioning.accessprofiles import (
    empty_rights_profile,
    get_access_profile,
)
from univention.ox.provisioning.helpers import Skip, get_context_id
from univention.ox.soap.config import (
    DEFAULT_IMAP_SERVER,
    DEFAULT_LANGUAGE,
    DEFAULT_SMTP_SERVER,
    LOCAL_TIMEZONE,
    get_context_admin_user,
)

User = get_ox_integration_class("SOAP", "User")
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
            text, exc1, exc2
        )
    )


def user_from_attributes(attributes, user_id=None):
    user = User(id=user_id)
    if attributes:
        context_id = get_context_id(attributes)
        user.context_id = context_id
        update_user(user, attributes)
    return user


def update_user(user, attributes):
    user.context_admin = False
    user.name = attributes.get("username")
    user.display_name = attributes.get("oxDisplayName")
    user.password = "dummy"
    user.given_name = attributes.get("firstname")
    user.sur_name = attributes.get("lastname")
    user.default_sender_address = attributes.get("mailPrimaryAddress")  # TODO: ???
    # user.assistant_name = attributes.get()
    user.branches = attributes.get("oxBranches")
    # user.business_category = attributes.get()
    # user.categories = attributes.get()
    user.cellular_telephone1 = attributes.get("oxMobileBusiness")
    user.city_business = attributes.get("city")
    user.city_home = attributes.get("oxCityHome")
    user.city_other = attributes.get("oxCityOther")
    user.commercial_register = attributes.get("oxCommercialRegister")
    user.company = attributes.get("organisation")
    user.country_business = attributes.get("oxCountryBusiness")
    user.country_home = attributes.get("oxCountryHome")
    user.country_other = attributes.get("oxCountryOther")
    # user.drive_user_folder_mode = attributes.get()
    # user.default_group = attributes.get()
    user.department = attributes.get("oxDepartment")
    user.email1 = attributes.get("mailPrimaryAddress")
    user.primary_email = user.email1
    user.imap_login = user.email1
    user.email2 = attributes.get("oxEmail2")
    user.email3 = attributes.get("oxEmail3")
    user.employee_type = attributes.get("employeeType")
    user.fax_business = attributes.get("oxFaxBusiness")
    user.fax_home = attributes.get("oxFaxHome")
    user.fax_other = attributes.get("oxFaxOther")
    # user.filestore_id = attributes.get()
    # user.filestore_name = attributes.get()
    # user.folder_tree = attributes.get()
    # user.gui_preferences_for_soap = attributes.get()
    user.gui_spam_filter_enabled = True
    # user.info = attributes.get()
    user.instant_messenger1 = attributes.get("oxInstantMessenger1")
    user.instant_messenger2 = attributes.get("oxInstantMessenger2")
    user.language = attributes.get("oxLanguage", DEFAULT_LANGUAGE)
    # user.mail_folder_confirmed_ham_name = attributes.get()
    # user.mail_folder_confirmed_spam_name = attributes.get()
    # user.mail_folder_drafts_name = attributes.get()
    # user.mail_folder_sent_name = attributes.get()
    # user.mail_folder_spam_name = attributes.get()
    # user.mail_folder_trash_name = attributes.get()
    # user.mail_folder_archive_full_name = attributes.get()
    user.manager_name = attributes.get("oxManagerName")
    user.marital_status = attributes.get("oxMarialStatus")
    user.middle_name = attributes.get("oxMiddleName")
    user.nickname = attributes.get("oxNickName")
    user.note = attributes.get("oxNote")
    user.number_of_children = attributes.get("oxNumOfChildren")
    user.number_of_employee = attributes.get("employeeNumber")
    # user.password_mech = attributes.get()
    # user.password_expired = attributes.get()
    user.position = attributes.get("oxPosition")
    user.postal_code_business = attributes.get("postcode")
    user.postal_code_home = attributes.get("oxPostalCodeHome")
    user.postal_code_other = attributes.get("oxPostalCodeOther")
    user.profession = attributes.get("oxProfession")
    user.sales_volume = attributes.get("oxSalesVolume")
    user.spouse_name = attributes.get("oxSpouseName")
    user.state_business = attributes.get("oxStateBusiness")
    user.state_home = attributes.get("oxStateHome")
    user.state_other = attributes.get("oxStateOther")
    user.street_business = attributes.get("street")
    user.street_home = attributes.get("oxStreetHome")
    user.street_other = attributes.get("oxStreetOther")
    user.suffix = attributes.get("oxSuffix")
    user.tax_id = attributes.get("oxTaxId")
    user.telephone_assistant = attributes.get("oxTelephoneAssistant")
    # user.telephone_callback = attributes.get()
    user.telephone_car = attributes.get("oxTelephoneCar")
    user.telephone_company = attributes.get("oxTelephoneCompany")
    user.telephone_ip = attributes.get("oxTelephoneIp")
    # user.telephone_isdn = attributes.get()
    user.telephone_other = attributes.get("oxTelephoneOther")
    # user.telephone_primary = attributes.get()
    # user.telephone_radio = attributes.get()
    user.telephone_telex = attributes.get("oxTelephoneTelex")
    user.telephone_ttytdd = attributes.get("oxTelephoneTtydd")
    user.timezone = attributes.get("oxTimeZone", LOCAL_TIMEZONE)
    user.title = attributes.get("title")
    # user.upload_file_size_limit = attributes.get()
    # user.upload_file_size_limitPerFile = attributes.get()
    user.url = attributes.get("oxUrl")
    user.used_quota = attributes.get("oxUserQuota")  # TODO: or max_quota?
    user.max_quota = attributes.get("oxUserQuota")  # TODO: or used_quota?
    # user.user_attributes = attributes.get()
    user.userfield01 = attributes.get("oxUserfield01")
    user.userfield02 = attributes.get("oxUserfield02")
    user.userfield03 = attributes.get("oxUserfield03")
    user.userfield04 = attributes.get("oxUserfield04")
    user.userfield05 = attributes.get("oxUserfield05")
    user.userfield06 = attributes.get("oxUserfield06")
    user.userfield07 = attributes.get("oxUserfield07")
    user.userfield08 = attributes.get("oxUserfield08")
    user.userfield09 = attributes.get("oxUserfield09")
    user.userfield10 = attributes.get("oxUserfield10")
    user.userfield11 = attributes.get("oxUserfield11")
    user.userfield12 = attributes.get("oxUserfield12")
    user.userfield13 = attributes.get("oxUserfield13")
    user.userfield14 = attributes.get("oxUserfield14")
    user.userfield15 = attributes.get("oxUserfield15")
    user.userfield16 = attributes.get("oxUserfield16")
    user.userfield17 = attributes.get("oxUserfield17")
    user.userfield18 = attributes.get("oxUserfield18")
    user.userfield19 = attributes.get("oxUserfield19")
    user.userfield20 = attributes.get("oxUserfield20")
    # user.primary_account_name = attributes.get()
    # user.convert_drive_user_folders = attributes.get()
    if attributes.get("roomNumber"):
        user.room_number = attributes.get("roomNumber")[0]
    else:
        user.room_number = None
    if attributes.get("mobileTelephoneNumber"):
        user.cellular_telephone2 = attributes.get("mobileTelephoneNumber")[0]
    else:
        user.cellular_telephone2 = None
    if attributes.get("pagerTelephoneNumber"):
        user.telephone_pager = attributes.get("pagerTelephoneNumber")[0]
    else:
        user.telephone_pager = None
    if attributes.get("oxAnniversary"):
        user.anniversary = str2isodate(attributes.get("oxAnniversary"))
    else:
        user.anniversary = None
    if attributes.get("birthday"):
        user.birthday = str2isodate(attributes.get("birthday"))
    else:
        user.birthday = None
    if len(attributes.get("phone", [])) >= 1:
        user.telephone_business1 = attributes.get("phone")[0]
    else:
        user.telephone_business1 = None
    if len(attributes.get("phone", [])) >= 2:
        user.telephone_business2 = attributes.get("phone")[1]
    else:
        user.telephone_business2 = None
    if len(attributes.get("homeTelephoneNumber", [])) >= 1:
        user.telephone_home1 = attributes.get("homeTelephoneNumber")[0]
    else:
        user.telephone_home1 = None
    if len(attributes.get("homeTelephoneNumber", [])) >= 2:
        user.telephone_home2 = attributes.get("homeTelephoneNumber")[1]
    else:
        user.telephone_home2 = None
    aliases = [user.email1] + attributes.get("mailAlternativeAddress", [])
    user.aliases = aliases
    if attributes.get("oxAccess", "none") != "none":
        user.mail_enabled = True
    else:
        user.mail_enabled = False

    imap_url = urlparse(DEFAULT_IMAP_SERVER)
    user.imap_port = imap_url.port  # 143
    user.imap_schema = imap_url.scheme + "://"  # "imap://"
    user.imap_server = attributes.get("mailHomeServer", imap_url.hostname)
    # user.imap_server_string = attributes.get()
    smtp_url = urlparse(DEFAULT_SMTP_SERVER)
    user.smtp_port = smtp_url.port  # 587
    user.smtp_schema = smtp_url.scheme + "://"  # "smtp://"
    user.smtp_server = attributes.get("mailHomeServer", smtp_url.hostname)
    # user.smtp_server_string = attributes.get()


def set_user_rights(user, obj):
    access_rights = empty_rights_profile()

    user_access = obj.attributes.get("oxAccess")

    if user_access:
        access_profile = get_access_profile(user_access)
        if access_profile is None:
            logger.warn(
                f"Cannot find access profile {user_access!r}. Leaving access rights untouched!"
            )
            return
    else:
        access_profile = []
    for access_right in access_profile:
        if access_right in access_rights:
            access_rights[access_right] = True
    logger.info(f"Changing user {user.id} to profile {user_access}")
    user.service(user.context_id).change_by_module_access(
        {"id": user.id}, access_rights
    )


def get_user_id(attributes):
    context_id = get_context_id(attributes)
    username = attributes.get("username")
    if username == get_context_admin_user(context_id):
        raise Skip(
            f"Not touching {username} in context {context_id}: Is context admin!"
        )
    logger.info(f"Searching for {username} in context {context_id}")
    users = User.list(context_id, pattern=username)
    if not users:
        return None
    assert len(users) == 1
    return users[0].id


def create_user(obj):
    logger.info(f"Creating {obj}")
    if obj.attributes.get("isOxUser", "Not") == "Not":
        logger.info(f"{obj} is no OX user. Deleting instead...")
        return delete_user(obj)
    if get_user_id(obj.attributes):
        if obj.old_attributes is None:
            obj.old_attributes = deepcopy(obj.attributes)
            logger.warning(
                "Found in DB but had no old attributes. Using new ones as old..."
            )
        logger.info(f"{obj} exists. Modifying instead...")
        return modify_user(obj)
    user = user_from_attributes(obj.attributes)
    user.create()
    set_user_rights(user, obj)
    logger.info("Looking for groups of this user to be created in the context id")
    for group in obj.attributes.get("groups", []):
        group_obj = univention.ox.provisioning.helpers.get_old_obj(group)
        if group_obj is None or group_obj.attributes is None:
            logger.warning(
                f"Dont know anything about {group}. Does it exist? Is it to be deleted? Skipping..."
            )
            continue
        if group_obj.attributes.get("isOxGroup", "Not") == "Not":
            logger.warning(f"{group} is no OX group. Skipping...")
            continue
        groupname = group_obj.attributes.get("name")
        groups = Group.list(user.context_id, pattern=groupname)
        if not groups:
            logger.info(
                f"Group {groupname} does not yet exist in {user.context_id}. Creating..."
            )
            group = Group(
                context_id=user.context_id,
                name=groupname,
                display_name=groupname,
                members=[user.id],
            )
            group.create()
        else:
            group = groups[0]
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
        logger.info("%s has no context ID. Creating instead...", obj)
        return create_user(obj)
    if not user_id:
        logger.info(f"{obj} does not yet exist. Creating instead...")
        return create_user(obj)
    if obj.old_attributes:
        if obj.old_attributes.get("isOxUser", "Not") == "Not":
            logger.warning(
                f"{obj} was no OX user before... that should not be the case. Modifying anyway..."
            )
        old_context = get_context_id(obj.old_attributes)
        new_context = get_context_id(obj.attributes)
        if old_context != new_context:
            logging.info(f"Changing context: {old_context} -> {new_context}")
            already_existing_user_id = get_user_id(obj.attributes)
            if already_existing_user_id:
                logger.warning(
                    f"{obj} was found in context {old_context} with ID {user_id} and in {new_context} with {already_existing_user_id}. This should not happen. Will delete in {old_context} and modify in {new_context}"  # noqa
                )
                delete_user(deepcopy(obj))
            else:
                create_user(obj)
                return delete_user(deepcopy(obj))
        user = user_from_attributes(obj.old_attributes, user_id)
        user.context_id = new_context
        update_user(user, obj.attributes)
    else:
        logger.info(f"{obj} has no old data. Resync?")
        user = user_from_attributes(obj.attributes, user_id)
    user.modify()
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
    user = user_from_attributes(obj.old_attributes, user_id)
    group_service = Group.service(user.context_id)
    soap_groups = group_service.list_groups_for_user({"id": user.id})
    user.remove()
    obj.attributes = None  # make obj.was_deleted() return True
    logger.info("User was deleted, searching for now empty groups")
    for soap_group in soap_groups:
        logger.info(
            f"Found group {soap_group.name} with {len(soap_group.members)} members"
        )
        soap_group.members.remove(user.id)
        if soap_group.members:
            logger.info(
                f"Thus, removing member {user.id} from group {soap_group.name}..."
            )
            group_service.change(soap_group)
        else:
            logger.info(f"Thus, deleting group {soap_group.id} in {user.context_id}...")
            group_service.delete(soap_group)
