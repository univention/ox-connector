#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Univention Listener Converter
#  Listener integration
#
# Copyright 2023 Univention GmbH
#
# https://www.univention.de/
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
# <https://www.gnu.org/licenses/>.
#

"""
This module contains the mapping of LDAP attributes to UDM attributes.

Though mappings should be used from UDM handlers, they are at the moment
quite entangled and require many dependencies. Due to the current complexity of
python versioning from Univention Directory Listener (built for python3.7) and
the ox-connector (built for python3.9), we are handling our own mappings here.
"""

import os
import base64
import logging


logger = logging.getLogger("univention.ox")
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

mappings = {
    "users/user": {
        "uid": {
            "new_keys": ["username"],
            "is_multivalue": False
        },
        "uidNumber": {
            "new_keys": ["uidNumber"],
            "is_multivalue": False
        },
        "givenName": {
            "new_keys": ["firstname"],
            "is_multivalue": False
        },
        "sn": {
            "new_keys": ["lastname"],
            "is_multivalue": False
        },
        "jpegPhoto": {
            "new_keys": ["jpegPhoto"],
            "is_multivalue": False,
        },
        "gecos": {
            "new_keys": ["gecos"],
            "is_multivalue": False
        },
        "title": {
            "new_keys": ["title"],
            "is_multivalue": False
        },
        "mailPrimaryAddress": {
            "new_keys": ["mailPrimaryAddress"],
            "is_multivalue": False,
        },
        "isOxUser": {
            "new_keys": ["isOxUser"],
            "is_multivalue": False,
        },
        "oxContextIDNum": {
            "new_keys": ["oxContext"],
            "is_multivalue": False,
        },
        "oxAccess": {
            "new_keys": ["oxAccess"],
            "is_multivalue": False,
        },
        "oxDisplayName": {
            "new_keys": ["oxDisplayName"],
            "is_multivalue": False,
        },
        "oxUserQuota": {
            "new_keys": ["oxUserQuota"],
            "is_multivalue": False,
        },
        "cn": {
            "new_keys": ["displayName"],
            "is_multivalue": False,
        },
        "description": {
            "new_keys": ["description"],
            "is_multivalue": False,
        },
        "o": {
            "new_keys": ["organisation"],
            "is_multivalue": False,
        },
        "employeeNumber": {
            "new_keys": ["employeeNumber"],
            "is_multivalue": False,
        },
        "employeeType": {
            "new_keys": ["employeeType"],
            "is_multivalue": False,
        },
        "univentionBirthday": {
            "new_keys": ["birthday"],
            "is_multivalue": False,
        },
        "street": {
            "new_keys": ["street"],
            "is_multivalue": False,
        },
        "mail": {
            "new_keys": ["e-mail"],
            "is_multivalue": True,
        },
        "postalCode": {
            "new_keys": ["postcode"],
            "is_multivalue": False,
        },
        "l": {
            "new_keys": ["city"],
            "is_multivalue": False,
        },
        "st": {
            "new_keys": ["country"],
            "is_multivalue": False,
        },
        "telephoneNumber": {
            "new_keys": ["phone"],
            "is_multivalue": True,
        },
        "roomNumber": {
            "new_keys": ["roomNumber"],
            "is_multivalue": True,
        },
        "departmentNumber": {
            "new_keys": ["departmentNumber"],
            "is_multivalue": True,
        },
        "groups": {
            "new_keys": ["groups"],
            "is_multivalue": True
        },
        "mailAlternativeAddress": {
            "new_keys": ["mailAlternativeAddress"],
            "is_multivalue": True,
        },
        "pager": {
            "new_keys": ["pagerTelephoneNumber"],
            "is_multivalue": True,
        },
        "homePhone": {
            "new_keys": ["homeTelephoneNumber"],
            "is_multivalue": True,
        },
        "mobile": {
            "new_keys": ["mobileTelephoneNumber"],
            "is_multivalue": True,
        },
        "univentionMailHomeServer": {
            "new_keys": ["mailHomeServer"],
            "is_multivalue": False,
        },
        "gidNumber": {
            "new_keys": ["gidNumber"],
            "is_multivalue": False,
        },
        "homeDirectory": {
            "new_keys": ["unixhome"],
            "is_multivalue": False,
        },
        "mailForwardCopyToSelf": {
            "new_keys": ["mailForwardCopyToSelf"],
            "is_multivalue": False,
        },
        "oxAnniversary": {
            "new_keys": ["oxAnniversary"],
            "is_multivalue": False,
        },
        "oxBranches": {
            "new_keys": ["oxBranches"],
            "is_multivalue": False,
        },
        "oxCityHome": {
            "new_keys": ["oxCityHome"],
            "is_multivalue": False,
        },
        "oxCityOther": {
            "new_keys": ["oxCityOther"],
            "is_multivalue": False,
        },
        "oxCommercialRegister": {
            "new_keys": ["oxCommercialRegister"],
            "is_multivalue": False,
        },
        "oxCountryBusiness": {
            "new_keys": ["oxCountryBusiness"],
            "is_multivalue": False,
        },
        "oxCountryHome": {
            "new_keys": ["oxCountryHome"],
            "is_multivalue": False,
        },
        "oxCountryOther": {
            "new_keys": ["oxCountryOther"],
            "is_multivalue": False,
        },
        "oxDepartment": {
            "new_keys": ["oxDepartment"],
            "is_multivalue": False,
        },
        "oxEmail2": {
            "new_keys": ["oxEmail2"],
            "is_multivalue": False,
        },
        "oxEmail3": {
            "new_keys": ["oxEmail3"],
            "is_multivalue": False,
        },
        "oxFaxBusiness": {
            "new_keys": ["oxFaxBusiness"],
            "is_multivalue": False,
        },
        "oxFaxHome": {
            "new_keys": ["oxFaxHome"],
            "is_multivalue": False,
        },
        "oxFaxOther": {
            "new_keys": ["oxFaxOther"],
            "is_multivalue": False,
        },
        "oxInstantMessenger1": {
            "new_keys": ["oxInstantMessenger1"],
            "is_multivalue": False,
        },
        "oxInstantMessenger2": {
            "new_keys": ["oxInstantMessenger2"],
            "is_multivalue": False,
        },
        "oxManagerName": {
            "new_keys": ["oxManagerName"],
            "is_multivalue": False,
        },
        "oxMarialStatus": {
            "new_keys": ["oxMarialStatus"],
            "is_multivalue": False,
        },
        "oxMiddleName": {
            "new_keys": ["oxMiddleName"],
            "is_multivalue": False,
        },
        "oxMobileBusiness": {
            "new_keys": ["oxMobileBusiness"],
            "is_multivalue": False,
        },
        "oxNickName": {
            "new_keys": ["oxNickName"],
            "is_multivalue": False,
        },
        "oxNote": {
            "new_keys": ["oxNote"],
            "is_multivalue": False,
        },
        "oxNumOfChildren": {
            "new_keys": ["oxNumOfChildren"],
            "is_multivalue": False,
        },
        "oxPosition": {
            "new_keys": ["oxPosition"],
            "is_multivalue": False,
        },
        "oxPostalCodeHome": {
            "new_keys": ["oxPostalCodeHome"],
            "is_multivalue": False,
        },
        "oxPostalCodeOther": {
            "new_keys": ["oxPostalCodeOther"],
            "is_multivalue": False,
        },
        "oxProfession": {
            "new_keys": ["oxProfession"],
            "is_multivalue": False,
        },
        "oxSalesVolume": {
            "new_keys": ["oxSalesVolume"],
            "is_multivalue": False,
        },
        "oxSpouseName": {
            "new_keys": ["oxSpouseName"],
            "is_multivalue": False,
        },
        "oxStateBusiness": {
            "new_keys": ["oxStateBusiness"],
            "is_multivalue": False,
        },
        "oxStateHome": {
            "new_keys": ["oxStateHome"],
            "is_multivalue": False,
        },
        "oxStateOther": {
            "new_keys": ["oxStateOther"],
            "is_multivalue": False,
        },
        "oxStreetHome": {
            "new_keys": ["oxStreetHome"],
            "is_multivalue": False,
        },
        "oxStreetOther": {
            "new_keys": ["oxStreetOther"],
            "is_multivalue": False,
        },
        "oxSuffix": {
            "new_keys": ["oxSuffix"],
            "is_multivalue": False,
        },
        "oxTaxId": {
            "new_keys": ["oxTaxId"],
            "is_multivalue": False,
        },
        "oxTelephoneAssistant": {
            "new_keys": ["oxTelephoneAssistant"],
            "is_multivalue": False,
        },
        "oxTelephoneCar": {
            "new_keys": ["oxTelephoneCar"],
            "is_multivalue": False,
        },
        "oxTelephoneCompany": {
            "new_keys": ["oxTelephoneCompany"],
            "is_multivalue": False,
        },
        "oxTelephoneIp": {
            "new_keys": ["oxTelephoneIp"],
            "is_multivalue": False,
        },
        "oxTelephoneOther": {
            "new_keys": ["oxTelephoneOther"],
            "is_multivalue": False,
        },
        "oxTelephoneTelex": {
            "new_keys": ["oxTelephoneTelex"],
            "is_multivalue": False,
        },
        "oxTelephoneTtydd": {
            "new_keys": ["oxTelephoneTtydd"],
            "is_multivalue": False,
        },
        "oxUrl": {
            "new_keys": ["oxUrl"],
            "is_multivalue": False,
        },
        "oxUserfield01": {
            "new_keys": ["oxUserfield01"],
            "is_multivalue": False,
        },
        "oxUserfield02": {
            "new_keys": ["oxUserfield02"],
            "is_multivalue": False,
        },
        "oxUserfield03": {
            "new_keys": ["oxUserfield03"],
            "is_multivalue": False,
        },
        "oxUserfield04": {
            "new_keys": ["oxUserfield04"],
            "is_multivalue": False,
        },
        "oxUserfield05": {
            "new_keys": ["oxUserfield05"],
            "is_multivalue": False,
        },
        "oxUserfield06": {
            "new_keys": ["oxUserfield06"],
            "is_multivalue": False,
        },
        "oxUserfield07": {
            "new_keys": ["oxUserfield07"],
            "is_multivalue": False,
        },
        "oxUserfield08": {
            "new_keys": ["oxUserfield08"],
            "is_multivalue": False,
        },
        "oxUserfield09": {
            "new_keys": ["oxUserfield09"],
            "is_multivalue": False,
        },
        "oxUserfield10": {
            "new_keys": ["oxUserfield10"],
            "is_multivalue": False,
        },
        "oxUserfield11": {
            "new_keys": ["oxUserfield11"],
            "is_multivalue": False,
        },
        "oxUserfield12": {
            "new_keys": ["oxUserfield12"],
            "is_multivalue": False,
        },
        "oxUserfield13": {
            "new_keys": ["oxUserfield13"],
            "is_multivalue": False,
        },
        "oxUserfield14": {
            "new_keys": ["oxUserfield14"],
            "is_multivalue": False,
        },
        "oxUserfield15": {
            "new_keys": ["oxUserfield15"],
            "is_multivalue": False,
        },
        "oxUserfield16": {
            "new_keys": ["oxUserfield16"],
            "is_multivalue": False,
        },
        "oxUserfield17": {
            "new_keys": ["oxUserfield17"],
            "is_multivalue": False,
        },
        "oxUserfield18": {
            "new_keys": ["oxUserfield18"],
            "is_multivalue": False,
        },
        "oxUserfield19": {
            "new_keys": ["oxUserfield19"],
            "is_multivalue": False,
        },
        "oxUserfield20": {
            "new_keys": ["oxUserfield20"],
            "is_multivalue": False,
        },
    },
    "groups/group": {
        "univentionGroupType": {
            "new_keys": ["adGroupType"],
            "is_multivalue": False,
        },
        "gidNumber": {
            "new_keys": ["gidNumber"],
            "is_multivalue": False,
        },
        "uniqueMember": {
            "new_keys": ["users"],
            "is_multivalue": True,
        },
        "isOxGroup": {
            "new_keys": ["isOxGroup"],
            "is_multivalue": False,
        },
        "cn": {
            "new_keys": ["name"],
            "is_multivalue": False,
        },
        "sambaGroupType": {
            "new_keys": ["sambaGroupType"],
            "is_multivalue": False,
        },
    },
    "oxresources/oxresources": {
        "cn": {
            "new_keys": ["name"],
            "is_multivalue": False,
        },
        "description": {
            "new_keys": ["description"],
            "is_multivalue": False,
        },
        "displayName": {
            "new_keys": ["displayname"],
            "is_multivalue": False,
        },
        "oxResourceAdmin": {
            "new_keys": ["resourceadmin"],
            "is_multivalue": False,
        },
        "oxContextIDNum": {
            "new_keys": ["oxContext"],
            "is_multivalue": False,
        },
        "mailPrimaryAddress": {
            "new_keys": ["resourceMailAddress"],
            "is_multivalue": False,
        },
    },
    "oxmail/oxcontext": {
        "cn": {
            "new_keys": ["name"],
            "is_multivalue": False,
        },
        "oxContextIDNum": {
            "new_keys": ["contextid"],
            "is_multivalue": False,
        },
        "oxQuota": {
            "new_keys": ["oxQuota"],
            "is_multivalue": False,
        },
    },
    "oxmail/accessprofile": {
        "cn": {
            "new_keys": ["name"],
            "is_multivalue": False,
        },
        "displayName": {
            "new_keys": ["displayName"],
            "is_multivalue": False,
        },
        "oxRightCollectemailaddresses": {
            "new_keys": ["collectemailaddresses"],
            "is_multivalue": False
        },
        "oxRightContacts": {
            "new_keys": ["contacts"],
            "is_multivalue": False
        },
        "oxRightDelegatetask": {
            "new_keys": ["delegatetask"],
            "is_multivalue": False
        },
        "oxRightEditgroup": {
            "new_keys": ["editgroup"],
            "is_multivalue": False
        },
        "oxRightEditpassword": {
            "new_keys": ["editpassword"],
            "is_multivalue": False
        },
        "oxRightEditpublicfolders": {
            "new_keys": ["editpublicfolders"],
            "is_multivalue": False
        },
        "oxRightEditresource": {
            "new_keys": ["editresource"],
            "is_multivalue": False
        },
        "oxRightIcal": {
            "new_keys": ["ical"],
            "is_multivalue": False
        },
        "oxRightMultiplemailaccounts": {
            "new_keys": ["multiplemailaccounts"],
            "is_multivalue": False
        },
        "oxRightReadcreatesharedfolders": {
            "new_keys": ["readcreatesharedfolders"],
            "is_multivalue": False
        },
        "oxRightSubscription": {
            "new_keys": ["subscription"],
            "is_multivalue": False
        },
        "oxRightCalendar": {
            "new_keys": ["calendar"],
            "is_multivalue": False
        },
        "oxRightTasks": {
            "new_keys": ["tasks"],
            "is_multivalue": False
        },
        "oxRightVcard": {
            "new_keys": ["vcard"],
            "is_multivalue": False
        },
        "oxRightWebdav": {
            "new_keys": ["webdav"],
            "is_multivalue": False
        },
        "oxRightWebmail": {
            "new_keys": ["webmail"],
            "is_multivalue": False
        },
        "oxRightUsm": {
            "new_keys": ["usm"],
            "is_multivalue": False
        },
        "oxRightActivesync": {
            "new_keys": ["activesync"],
            "is_multivalue": False
        },
        "oxRightDeniedportal": {
            "new_keys": ["deniedportal"],
            "is_multivalue": False
        },
        "oxRightGlobaladdressbookdisabled": {
            "new_keys": ["globaladdressbookdisabled"],
            "is_multivalue": False
        },
        "oxRightInfostore": {
            "new_keys": ["infostore"],
            "is_multivalue": False
        },
        "oxRightPublicfoldereditable": {
            "new_keys": ["publicfoldereditable"],
            "is_multivalue": False
        },
        "oxRightSyncml": {
            "new_keys": ["syncml"],
            "is_multivalue": False
        },
        "oxRightWebdavxml": {
            "new_keys": ["webdavxml"],
            "is_multivalue": False
        },
    },
    "oxmail/functional_account": {
        "cn": {
            "new_keys": ["name"],
            "is_multivalue": False,
        },
        "mailPrimaryAddress": {
            "new_keys": ["mailPrimaryAddress"],
            "is_multivalue": False,
        },
        "oxQuota": {
            "new_keys": ["quota"],
            "is_multivalue": False,
        },
        "oxPersonal": {
            "new_keys": ["personal"],
            "is_multivalue": False,
        },
        "oxContextIDNum": {
            "new_keys": ["oxContext"],
            "is_multivalue": False,
        },
        "uniqueMember": {
            "new_keys": ["users"],
            "is_multivalue": True,
            "required": True,
        }
    },
}


# TODO: the new provisioning system should send UDM objects instead of LDAP
def format_as_udm_object(ldap_object: dict) -> dict:
    """
    Format LDAP object as UDM object.

    :param ldap_object: dict of LDAP object

    :return: dict of UDM object
    """
    return {
        'dn':
            unpack_values(ldap_object.get('entryDN', [])),
        'id':
            unpack_values(ldap_object.get('entryUUID', [])),
        'object':
            unpack_dictionary(ldap_object),
        'options': ['default'],
        'udm_object_type':
            unpack_values(ldap_object.get('univentionObjectType', [])),
    }


def unpack_values(values, is_multivalue: bool = False):
    """
    Unpack LDAP list of binary values to a list of strings.

    :param values_list: list of binary values

    :return: string if single value or list of strings
    """
    if len(values) == 1:
        if is_multivalue:
            return [values[0].decode()]
        try:
            return values[-1].decode()
        except UnicodeDecodeError:
            logger.warning(
                'unpack_values UnicodeDecodeError, trying base64 image'
            )
            # Handle images
            return base64.b64encode(values[0]).decode()
    string_values = []
    for v in values:
        # Handle exceptions such as trying to utf-8 decode the krb5Key
        try:
            string_values.append(v.decode())
        except UnicodeDecodeError as err:
            logger.warning('unpack_values UnicodeDecodeError %s', err)
            logger.debug('value: %s', v)
            continue
        except Exception as err:
            logger.exception('unpack_values failed with "%s"', err)
            logger.debug('value: %s', v)
            raise
    return string_values


def unpack_dictionary(ldap_object: dict) -> dict:
    """
    Convert the LDAP object to a dictionary with unpacked string values.

    :param ldap_object: dict of LDAP object

    :return: dict with single string or list of strings values.
    """
    object_type = unpack_values(ldap_object.get('univentionObjectType'))
    object_mappings = mappings[object_type]
    udm_object = {}
    for k, v in ldap_object.items():
        if k not in object_mappings:
            continue
        for new_key in object_mappings[k]['new_keys']:
            udm_object[new_key] = unpack_values(
                v, object_mappings[k].get('is_multivalue', False)
            )
    if object_type == "oxmail/functional_account":
        udm_object['groups'] = udm_object.get('groups', [])
        udm_object['users'] = udm_object.get('users', [])
    if object_type == "groups/group":
        udm_object['users'] = udm_object.get('users', [])
    return udm_object
