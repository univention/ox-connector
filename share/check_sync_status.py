#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Copyright (C) 2023 Univention GmbH
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

import asyncio
import dbm.gnu
import glob
import json
import os
import shutil
import subprocess
import sys
from argparse import ArgumentParser
from contextlib import contextmanager
from datetime import date, datetime
from pathlib import Path

import univention.ox.provisioning.helpers
from tests import udm_rest
from univention.ox.provisioning.helpers import get_context_id, get_db_id, get_obj_by_name_from_ox
from univention.ox.soap.backend_base import get_ox_integration_class
from univention.ox.soap.config import DEFAULT_CONTEXT

User = get_ox_integration_class("SOAP", "User")
Group = get_ox_integration_class("SOAP", "Group")
Resource = get_ox_integration_class("SOAP", "Resource")
Context = get_ox_integration_class("SOAP", "Context")
FunctionalAccount = get_ox_integration_class("SOAP", "SecondaryAccount")

udm = None


UDM_MODULE_TO_OX_SOAP_SERVICE = {
    "users/user" : User,
    "groups/group": Group,
    "oxmail/functional_account": FunctionalAccount,
    "oxresources/oxresources": Resource,
    "oxmail/oxcontext": Context
}

DATA_DIR = Path("/var/lib/univention-appcenter/apps/ox-connector/data")
NEW_FILES_DIR = DATA_DIR / "listener"
OLD_FILES_DIR = NEW_FILES_DIR / "old"

class KeyValue(object):
    def __init__(self, name):
        self.db_fname = str(NEW_FILES_DIR / name)
    @contextmanager
    def open(self):
        """Open DBM-Database and yield the handler"""
        with dbm.gnu.open(self.db_fname, "cs") as data_base:
            yield data_base
    def get(self, key):
        """Read value from DBM-Database"""
        with self.open() as data_base:
            return data_base.get(key)

mapping = KeyValue("old.db")

def _get_old_object(distinguished_name):
    path_to_old_user = mapping.get(distinguished_name)
    if not path_to_old_user:
        return None
    path_to_old_user = Path(path_to_old_user.decode("utf-8"))
    if not path_to_old_user.exists():
        return None
    with path_to_old_user.open() as file_handler:
        return json.load(file_handler)
    return None

def get_old_listener_object(dn):
    """ retrieve an object from the listener/old directory. """
    return _get_old_object(dn)

def _normalize_user(user):
    user_attributes = {
        'aliases': 'aliases',
        'anniversary': 'oxAnniversary',
        'birthday': 'birthday',
        'branches': 'oxBranches',
        'cellular_telephone1': 'oxMobileBusiness',
        'cellular_telephone2': 'mobileTelephoneNumber',
        'city_business': 'city',
        'city_home': 'oxCityHome',
        'city_other': 'oxCityOther',
        'commercial_register': 'oxCommercialRegister',
        'company': 'organisation',
        'country_business': 'oxCountryBusiness',
        'country_home': 'oxCountryHome',
        'country_other': 'oxCountryOther',
        'department': 'oxDepartment',
        'display_name': 'oxDisplayName', # 'displayName',
        'email1': 'mailPrimaryAddress',
        'email2': 'oxEmail2',
        'email3': 'oxEmail3',
        'employee_type': 'employeeType',
        'fax_business': 'oxFaxBusiness',
        'fax_home': 'oxFaxHome',
        'fax_other': 'oxFaxOther',
        'given_name': 'firstname',
        'imap_server': 'mailHomeServer',
        'instant_messenger1': 'oxInstantMessenger1',
        'instant_messenger2': 'oxInstantMessenger2',
        'manager_name': 'oxManagerName',
        'marital_status': 'oxMarialStatus',
        'max_quota': 'oxUserQuota',
        'middle_name': 'oxMiddleName',
        'nickname': 'oxNickName',
        'note': 'oxNote',
        'number_of_children': 'oxNumOfChildren',
        'number_of_employee': 'employeeNumber',
        'position': 'oxPosition',
        'postal_code_business': 'postcode',
        'postal_code_home': 'oxPostalCodeHome',
        'postal_code_other': 'oxPostalCodeOther',
        'primary_email': 'mailPrimaryAddress',
        'profession': 'oxProfession',
        'room_number': 'roomNumber',
        'sales_volume': 'oxSalesVolume',
        'smtp_server': 'mailHomeServer',
        'spouse_name': 'oxSpouseName',
        'state_business': 'oxStateBusiness',
        'state_home': 'oxStateHome',
        'state_other': 'oxStateOther',
        'street_business': 'street',
        'street_home': 'oxStreetHome',
        'street_other': 'oxStreetOther',
        'suffix': 'oxSuffix',
        'sur_name': 'lastname',
        'tax_id': 'oxTaxId',
        'telephone_assistant': 'oxTelephoneAssistant',
        'telephone_business1': 'phone',
        'telephone_business2': 'phone',
        'telephone_car': 'oxTelephoneCar',
        'telephone_company': 'oxTelephoneCompany',
        'telephone_home1': 'homeTelephoneNumber',
        'telephone_home2': 'homeTelephoneNumber',
        'telephone_ip': 'oxTelephoneIp',
        'telephone_other': 'oxTelephoneOther',
        'telephone_pager': 'pagerTelephoneNumber',
        'telephone_telex': 'oxTelephoneTelex',
        'telephone_ttytdd': 'oxTelephoneTtydd',
        'title': 'title',
        'url': 'oxUrl',
        'used_quota': 'oxUserQuota',
        'userfield01': 'oxUserfield01',
        'userfield02': 'oxUserfield02',
        'userfield03': 'oxUserfield03',
        'userfield04': 'oxUserfield04',
        'userfield05': 'oxUserfield05',
        'userfield06': 'oxUserfield06',
        'userfield07': 'oxUserfield07',
        'userfield08': 'oxUserfield08',
        'userfield09': 'oxUserfield09',
        'userfield10': 'oxUserfield10',
        'userfield11': 'oxUserfield11',
        'userfield12': 'oxUserfield12',
        'userfield13': 'oxUserfield13',
        'userfield14': 'oxUserfield14',
        'userfield15': 'oxUserfield15',
        'userfield16': 'oxUserfield16',
        'userfield17': 'oxUserfield17',
        'userfield18': 'oxUserfield18',
        'userfield19': 'oxUserfield19',
        'userfield20': 'oxUserfield20',
        'image1': 'jpegPhoto',
    }
    attrs = { user_attributes[key] : value for key, value in user.__dict__.items() if user_attributes.get(key) }
    attrs["oxContext"] = user.context_id
    attrs["oxDbId"] = user.id
    attrs["username"] = user.name
    return attrs

def _normalize_functional_account(fa):
    return fa

def _normalize_context(context):
    context_attributes = {
        'max_quota': 'oxQuota',
    }
    attrs = { context_attributes[key] : value for key, value in context.__dict__.items() if context_attributes.get(key) }
    attrs["name"] = context.name
    attrs["contextid"] = str(context.context_id)
    attrs["oxQuota"] = str(attrs["oxQuota"])
    return attrs


def _normalize_resource(resource):
    resource_attributes = {
        #'available': 'available',
        'description': 'description',
        'display_name': 'displayname',
        'email': 'resourceMailAddress',
    }
    attrs = { resource_attributes[key] : value for key, value in resource.__dict__.items() if resource_attributes.get(key) }
    attrs["name"] = resource.name
    attrs["oxContext"] = str(resource.context_id)
    return attrs

def _normalize_group(group):
    group_attributes = {
        'display_name': 'displayname',
        'members': 'users',
    }
    attrs = { group_attributes[key] : value for key, value in group.__dict__.items() if group_attributes.get(key) }
    attrs["name"] = group.name

    return attrs


def normalize_ox_attributes(attributes, module):
    """ set a common name to attributes. """
    _normalize_fns = {
        "users/user" : _normalize_user,
        "groups/group" : _normalize_group,
        "oxmail/oxcontext" : _normalize_context,
        "oxresources/oxresources" : _normalize_resource,
        "oxmail/functional_account" : _normalize_functional_account
    }
    return _normalize_fns[module](attributes)

def _get_ox_group(_1, _2, name):
    ret = None
    for ctx in Context.list():
        obj = get_obj_by_name_from_ox(Group, ctx.context_id, name)
        if obj:
            if not ret:
                ret = obj
                ret.members = [(v, ctx.context_id) for v in ret.members]
            else:
                ret.members += [(v, ctx.context_id) for v in obj.members]
                ret.id = ret.id + [obj.id] if isinstance(ret.id, list) else [ret.id, obj.id]
                ret.context_id = ret.context_id + [obj.context_id] if isinstance(ret.context_id, list) else [ret.context_id, obj.context_id]
    return ret

def _get_ox_functional_account(_1, _2, name):
    ret = {}
    for ctx in Context.list():
        objs = [x for x in FunctionalAccount.list(ctx.context_id) if x.name == name]
        for obj in objs:
            ret["mailPrimaryAddress"] = obj.primaryAddress
            ret["name"] = obj.name
            ret["personal"] = obj.personal
            if not ret.get("users"):
                ret["users"] = [(obj.userId, ctx.context_id)]
                ret["context_id"] = [obj.contextId]
                ret["id"] = [obj.id]
            else:
                ret["users"].append((obj.userId, ctx.context_id))
                ret["context_id"].append(obj.contextId)
                ret["id"].append(obj.id)

    return ret

def get_ox_object(module, id, context=None):
    """ retrieve an object from the ox database """
    _get_from_ox = {
        "users/user" : get_obj_by_name_from_ox,
        "groups/group" : _get_ox_group,
        "oxmail/oxcontext" : get_obj_by_name_from_ox,
        "oxresources/oxresources" : get_obj_by_name_from_ox,
        "oxmail/functional_account" : _get_ox_functional_account
    }
    return _get_from_ox[module](UDM_MODULE_TO_OX_SOAP_SERVICE[module], context, id)

def search_ox_user_duplicates(name):
    ret = []
    for ctx in Context.list():
        if get_obj_by_name_from_ox(User, ctx.context_id, name):
            ret.append(ctx.context_id)
    return ret

def get_udm_object(module, dn):
    """ retrieve an object from udm. """
    try:
        return udm.get(module).get(dn)
    except udm_rest.UnprocessableEntity:
        return None

def _common_repr(key, val, is_ox=False):
    if isinstance(val, (int, date)):
        return str(val)
    elif val == []:
        return None
    elif key == 'oxUserQuota' and val is None:
        return '-1'
    elif key in ('isOxUser', 'ixOxGroup') and (val == 'OK' or is_ox):
        return 'True'
    else:
        return val

def get_diff(module, file_obj, ox_obj, udm_obj):

    _specific_ignored_attributes = {
        "users/user" : set(['oxDbUsername', 'e-mail', 'description', 'displayName', 'mailForwardAddress', 'FetchMailSingle' , 'mailForwardCopyToSelf', 'locked', 'FetchMailMulti', 'uidNumber', 'primaryGroup', 'serviceprovider', 'gidNumber', 'sambaUserWorkstations', 'postOfficeBox', 'unlockTime', 'gecos', 'oxTimeZone', 'oxLanguage', 'sambaRID', 'lockedTime', 'unlock', 'homeSharePath', 'mailUserQuota', 'pwdChangeNextLogin', 'unixhome', 'password', 'disabled', 'shell', 'accountActivationDate', 'groups', 'sambaPrivileges', 'roomNumber']),
        "groups/group" : set(['oxDbGroupname', 'sambaRID', 'allowedEmailGroups', 'sambaGroupType', 'isOxGroup', 'hosts', 'displayname', 'nestedGroup', 'memberOf', 'gidNumber', 'sambaPrivileges', 'adGroupType', 'serviceprovidergroup', 'objectFlag', 'allowedEmailUsers', 'groups']),
        "oxmail/oxcontext" : set([]),
        "oxresources/oxresources" : set(['resourceadmin']),
        "oxmail/functional_account" : set(['groups'])
    }

    ignored_attributes = set(['objectFlag', 'umcProperty']) | _specific_ignored_attributes[module]
    keys = set(file_obj.keys()) | set(ox_obj.keys()) | set(udm_obj.keys())
    ok = True
    for key in keys - ignored_attributes:
        v_file = _common_repr(key, file_obj.get(key))
        v_ox = _common_repr(key, ox_obj.get(key), is_ox=True)
        v_udm = _common_repr(key, udm_obj.get(key))
        if module == "oxmail/functional_account" and key in ('context_id', 'id'):
            continue
        elif module in ("oxmail/functional_account", "groups/group") and key == 'users':
            v_file = sorted(res["object"]["username"] for dn in v_file if (res:= get_old_listener_object(dn)) and res["object"]["isOxUser"] == "OK" and not res["object"]["username"].startswith("oxadmin"))
            v_udm = sorted(res.properties["username"] for dn in v_udm if (res:= get_udm_object("users/user", dn)) and res.properties["isOxUser"] == True and not res.properties["username"].startswith("oxadmin"))
            ox_usernames = []
            for (id, ctx) in v_ox:
                soap_service = User.service(ctx)
                obj = soap_service.get_data(soap_service.Type(id=id, name=None))
                if obj:
                    ox_usernames.append(obj.name)
            v_ox = sorted(ox_usernames)
            if v_file != v_ox or v_file != v_udm:
                print(f"DIFF({key}): old listener value: {v_file}, ox value: {v_ox}, udm value: {v_udm}")
                ok = False
        elif key == "oxAccess":
            if v_file != v_udm:
                print(f"DIFF({key}): old listener value: {v_file}, udm value: {v_udm}")
                ok = False
        elif key == "aliases":
            v_file = [file_obj.get("mailPrimaryAddress")] + file_obj.get("mailAlternativeAddress", [])
            v_udm = [udm_obj.get("mailPrimaryAddress")] + udm_obj.get("mailAlternativeAddress", [])
            if v_file != v_ox or v_file != v_udm:
                print(f"DIFF({key}): old listener value: {v_file}, ox value: {v_ox}, udm value: {v_udm}")
        elif key == "oxDbId" and v_file != v_ox:
            if v_file:
                print(f"DIFF({key}): old listener value: {v_file}, ox value: {v_ox}. Replace the 'oxDbId' field in the old listener file with the current ox value.")
                ok = False
        elif v_file != v_ox or (v_file != v_udm and key != "oxDbId"):
            print(f"DIFF({key}): old listener value: {v_file}, ox value: {v_ox}, udm value: {v_udm}")
            ok = False
    return ok


def resync_old_obj(dn, module):
    old_file = mapping.get(dn)
    new_name = str(NEW_FILES_DIR / f"{datetime.now().strftime('%Y-%m-%d-%H-%M-%S-%f')}.json")
    if module == "users/user":
        with open(old_file) as fd:
            json_data = json.load(fd)
        if json_data.get("object").get("oxDbId"):
            del json_data["object"]["oxDbId"]
        with open(old_file, "w") as fd:
            json.dump(json_data, fd, sort_keys=True, indent=4)
        with open(new_name, "w") as fd:
            json.dump(json_data, fd, sort_keys=True, indent=4)
    else:
        shutil.copy(old_file, new_name)
    print(f"Object {dn} has been scheduled to be resynced with file {new_name} and should be processed in the next connector loop.")


def search_and_compare_by_dn(args):
    print(f"Search object with dn: {args.dn}")

    check_diff = True
    file_object = get_old_listener_object(args.dn)
    uid = args.dn.split(",")[0] #ldap.explode_rdn(args.dn)[0]
    name = uid.split("=")[1] #ldap.dn.str2dn(uid)[0][0][1]
    module = args.udm_module or (file_object.get("udm_object_type") if file_object else None)
    if not module:
        print("Error: can't find udm module. Specify it with --udm_module")
        sys.exit(1)

    context = args.ox_context or (file_object.get("object", {}).get("oxContext") if file_object else None)
    if not context and module == "users/user":
        print("Error: can't find ox context. Specify it with --ox_context")
        sys.exit(1)

    udm_object = get_udm_object(module, args.dn)

    if not udm_object:
        print("Error: Object not found in udm. The object with the specified dn does not exits. It possibly has been deleted or moved.")
        sys.exit(1)

    if module == "users/user":
        ox_name = file_object.get("object", {}).get("oxDbUsername") or name
    elif module == "groups/group":
        ox_name = file_object.get("object", {}).get("oxDbGroupname") or name
    else:
        ox_name = name
    ox_object = get_ox_object(module, ox_name, context)

    if module == "users/user" and not udm_object.properties['isOxUser']:
        print("The object is not an OX user (udm property 'isOxUser'). Enable it to synchronize.")
        return
    if module == "groups/group" and not udm_object.properties['isOxGroup']:
        print("The object is not an OX group (udm property 'isOxGroup'). Enable it to synchronize.")
        return

    if not ox_object:
        if module == 'users/user':
            print(f"User {name} not found in ox database in context {context}. Looking in other contexts...")
            ids = search_ox_user_duplicates(name)
            if len(ids) > 0:
                print(f"User found in contexts {ids}. Check if the object is still in the listener queue. If it is not there you have to manually move the object from the ox database using the ox cli tools (Tip: use the cli tool 'usercopy' to preserve user info) and remove appearances in old contexts after that.")
                if args.resync:
                    print("Resync not possible.")
                    args.resync = False
            else:
                print("The object wasn't synced yet, it was manually removed from the database or there was a problem during the provisioning.")
        else:
            print(f"Object not found in ox database.")
        check_diff = False

    if not file_object:
        print("Object not found in /old directory. The object wasn't synchronized yet or the directory was removed.")
        check_diff = False

    result = get_diff(module, file_object.get("object", {}), normalize_ox_attributes(ox_object, module), udm_object.properties) if check_diff else False
    if result:
        print("Success: Data of the object is consistent between OX, UDM and listener files.")
    elif args.resync:
        if not file_object:
            uuid = udm_object.representation['uuid']
            print("Can't resync using old listener file. It doesn't exist. You can trigger a resync running the following command from your ucs system.\n\n"
"cat > /var/lib/univention-appcenter/listener/ox-connector/$(date +%Y-%m-%d-%H-%M-%S-%N).json <<- EOF\n"
"{\n"
f'    "entry_uuid": "{uuid}",\n'
f'    "dn": "{args.dn}",\n'
f'    "object_type": "{module}",\n'
f'    "command": "modify"\n'
"}\n"
"EOF")
            sys.exit(1)
        resync_old_obj(args.dn, module)
    else:
        print("Warning: Data inconsistencies detected. Object data differs between OX, UDM and listener files.\nResync object data by running this command again with the --resync flag.")

def main():
    parser = ArgumentParser()
    parser.add_argument('--dn', required=True, help='Check the object with the specified dn.')
    parser.add_argument('--udm_module', help="Object's udm module. Required if the property is missing in the old/ directory object.")
    parser.add_argument('--ox_context', help="Object's ox context. Required if the property is missing in the old/ directory object.")
    parser.add_argument('--resync', action='store_true', help="Resync object data by creating a new file in the listener. Resynchronizing groups will only work if its users are correctly provisioned.")
    parser.add_argument('--udm_admin_account', help="UDM user used for connection.", required=True)
    parser.add_argument('--udm_password_file', help="UDM password file.", required=True)
    parser.add_argument('--udm_host', help="UDM host.", required=True)

    args = parser.parse_args()

    #First run health check.
    check = json.loads(subprocess.run(['/usr/local/share/ox-connector/resources/get_current_error.py'], capture_output=True, text=True).stdout)
    if check["errors"] != '0':
        err = check.get("message")
        print(f"Warning: The OX Connector is not properly working: {err}")

    if len(glob.glob("/var/lib/univention-appcenter/apps/ox-connector/data/listener/*.json")) > 0:
        print(f"Warning: The OX Connector queue is not empty. There may be data inconsistencies if the queried object is still in the queue.")


    with open(args.udm_password_file) as f:
        global udm
        udm = udm_rest.UDM(f"{args.udm_host}/univention/udm/", args.udm_admin_account, f.read().strip())

    if args.dn:
        search_and_compare_by_dn(args)
    else:
        sys.exit(1)


main()
