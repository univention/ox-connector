#!/usr/bin/python3
# -*- coding: utf-8 -*-
#
# Univention Listener Converter
#  Listener integration
#
# Copyright 2021 Univention GmbH
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

# 3rd party
from univention.listener.handler import ListenerModuleHandler

# internal
from univention.ox.provisioning import run
from listener_trigger import TriggerObject

name = 'ox-listener-service'

# Currently we receive LDAP objects from UDL, while the OX Connector was
# designed to receive UDM objects. This means we need to map the LDAP
# objects to UDM objects. This is temporary, until the new provisioning is
# in place.

ldap_to_udm_keys_mapping = {
    # user
    "uid": {
        "new_key": "username",
        "is_multivalue": False
    },
    "givenName": {
        "new_key": "firstname",
        "is_multivalue": False
    },
    "sn": {
        "new_key": "lastname",
        "is_multivalue": False
    },
    "mailPrimaryAddress":
        {
            "new_key": "mailPrimaryAddress",
            "is_multivalue": False,
        },
    "l": {
        "new_key": "city",
        "is_multivalue": False
    },
    "postalCode": {
        "new_key": "postcode",
        "is_multivalue": False
    },
    "title": {
        "new_key": "title",
        "is_multivalue": False
    },
    # multivalue
    "roomNumber": {
        "new_key": "roomNumber",
        "is_multivalue": True,
    },
    "o": {
        "new_key": "organisation",
        "is_multivalue": False
    },
    "mailAlternativeAddress":
        {
            "new_key": "mailAlternativeAddress",
            "is_multivalue": False,
        },
    # multivalue
    "pagerTelephoneNumber":
        {
            "new_key": "pagerTelephoneNumber",
            "is_multivalue": True,
        },
    "univentionBirthday": {
        "new_key": "birthday",
        "is_multivalue": False
    },
    # multivalue
    "telephoneNumber":
        {
            "new_key": "mobileTelephoneNumber",
            "is_multivalue": True,
        },
    "univentionMailHomeServer":
        {
            "new_key": "mailHomeServer",
            "is_multivalue": False,
        },
    "oxContextIDNum": {
        "new_key": "oxContext",
        "is_multivalue": False
    },
    # multivalue
    "uniqueMember": {
        "new_key": "users",
        "is_multivalue": True
    },
}


# FIXME: this function does not work if there is only one entry in a multivalue
# field. It will return a string instead of a list of strings.
def unpack_values(values_list: list, is_multivalue: bool = False):
    """
    Unpack LDAP list of binary values to a list of strings.

    :param values_list: list of binary values

    :return: string if single value or list of strings
    """
    if len(values_list) == 1:
        if is_multivalue:
            return [values_list[0].decode()]
        return values_list[0].decode()
    string_values = []
    for v in values_list:
        # Handle exceptions such as trying to utf-8 decode the krb5Key
        try:
            string_values.append(v.decode())
        except UnicodeDecodeError:
            self.logger.warning('UDL Handler/unpack_values: UnicodeDecodeError for "%s"', v)
            continue
        except Exception:
            self.logger.exception('UDL Handler/unpack_values: Unhandled error for "%s"', v)
            raise
    return string_values


def unpack_dictionary(old: dict) -> dict:
    """
    Convert the LDAP object to a dictionary with unpacked string values.

    :param old: dict of LDAP object

    :return: dict with single string or list of strings values.
    """
    udm_object = {}
    for k, v in old.items():
        if v is None:
            continue
        if k in ldap_to_udm_keys_mapping:
            udm_object[ldap_to_udm_keys_mapping[k]['new_key']] = unpack_values(
                v, ldap_to_udm_keys_mapping[k]['is_multivalue']
            )
        else:
            udm_object[k] = unpack_values(v)
    return udm_object


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


class OxConnectorListenerModule(ListenerModuleHandler):
    def initialize(self):
        self.logger.info('ox-listener-service module initialize')

    def create(self, dn, new):
        self.logger.info('[ create ] dn: %r', dn)
        fake_udm_obj = format_as_udm_object(new)
        obj = TriggerObject(
            fake_udm_obj['id'],
            fake_udm_obj['udm_object_type'],
            fake_udm_obj['dn'],
            fake_udm_obj['object'],
            fake_udm_obj['options'],
            None,
        )
        obj.old_distinguished_name = new["dn"]
        obj.old_attributes = new["object"]
        obj.old_options = new["options"]
        obj._old_loaded = True
        try:
            run(obj)
        except Exception:
            self.logger.exception('UDL Handler/create: run failed')
            raise

    def modify(self, dn, old, new, old_dn):
        self.logger.info('[ modify ] dn: %r', dn)
        fake_udm_obj = format_as_udm_object(new)
        obj = TriggerObject(
            fake_udm_obj['id'],
            fake_udm_obj['udm_object_type'],
            fake_udm_obj['dn'],
            fake_udm_obj['object'],
            fake_udm_obj['options'],
            None,
        )
        obj.old_distinguished_name = old["dn"]
        obj.old_attributes = old["object"]
        obj.old_options = old["options"]
        obj._old_loaded = True
        try:
            run(obj)
        except Exception:
            self.logger.exception('UDL Handler/modify: run failed')
            raise
        if old_dn:
            self.logger.debug('it is (also) a move! old_dn: %r, old_dn')
        self.logger.debug('changed attributes %r', new)

    def remove(self, dn, old):
        self.logger.info('[ remove ] dn: %r', dn)
        obj.old_distinguished_name = old["dn"]
        obj.old_attributes = old["object"]
        obj.old_options = old["options"]
        obj._old_loaded = True

    class Configuration(ListenerModuleHandler.Configuration):
        name = name
        description = (
            'Handle LDAP-changes for various OX objects, users and groups'
        )
        # oxmail/oxcontext, oxresources/oxresources, users/user, groups/group, oxmail/accessprofile, oxmail/functional_account
        ldap_filter = '(|(univentionObjectType=users/user)(univentionObjectType=oxmail/oxcontext)(univentionObjectType=oxresources/oxresources)(univentionObjectType=groups/group)(univentionObjectType=oxmail/accessprofile)(univentionObjectType=oxmail/functional_account))'


# [EOF]
