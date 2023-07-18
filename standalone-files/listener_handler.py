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

# included
import os
import signal
import logging
import base64

# 3rd party
from univention.listener.handler import ListenerModuleHandler

# internal
from univention.ox.provisioning import helpers, run
from listener_trigger import TriggerObject, KeyValueStore

name = 'ox-listener-service'

# FIXME:
# Currently we receive LDAP objects from UDL, while the OX Connector was
# designed to receive UDM objects. This means we need to map the LDAP
# objects to UDM objects. This is temporary, until the new provisioning is
# in place.

ldap_to_udm_keys_mapping = {
    "uid": {
        "new_key": "username",
        "is_multivalue": False
    },
    "groups": {
        "new_key": "groups",
        "is_multivalue": True
    },
    "givenName": {
        "new_key": "firstname",
        "is_multivalue": False
    },
    "sn": {
        "new_key": "lastname",
        "is_multivalue": False
    },
    "mailPrimaryAddress": {
        "new_key": "mailPrimaryAddress",
        "second_new_key": "resourceMailAddress",
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
    "cn": {
        "new_key": "name",
        "is_multivalue": False,
    },
    "title": {
        "new_key": "title",
        "is_multivalue": False
    },
    "users": {
        "new_key": "users",
        "is_multivalue": True
    },
    "roomNumber": {
        "new_key": "roomNumber",
        "is_multivalue": True,
    },
    "o": {
        "new_key": "organisation",
        "is_multivalue": False
    },
    "mailAlternativeAddress": {
        "new_key": "mailAlternativeAddress",
        "is_multivalue": False,
    },
    "pagerTelephoneNumber": {
        "new_key": "pagerTelephoneNumber",
        "is_multivalue": True,
    },
    "univentionBirthday": {
        "new_key": "birthday",
        "is_multivalue": False
    },
    "telephoneNumber": {
        "new_key": "mobileTelephoneNumber",
        "is_multivalue": True,
    },
    "univentionMailHomeServer": {
        "new_key": "mailHomeServer",
        "is_multivalue": False,
    },
    # Some LDAP attributes are mapped to multiple UDM attributes.
    "oxContextIDNum": {
        "new_key": "contextid",
        "second_new_key": "oxContext",
        "is_multivalue": False
    },
    "oxResourceAdmin": {
        "new_key": "resourceadmin",
        "is_multivalue": False
    },
    "uniqueMember": {
        "new_key": "users",
        "is_multivalue": True
    },
    "oxRightCalendar": {
        "new_key": "calendar",
        "is_multivalue": False
    },
    "oxRightCollectemailaddresses": {
        "new_key": "collectemailaddresses",
        "is_multivalue": False
    },
    "oxRightContacts": {
        "new_key": "contacts",
        "is_multivalue": False
    },
    "oxRightDelegatetask": {
        "new_key": "delegatetask",
        "is_multivalue": False
    },
    "oxRightEditgroup": {
        "new_key": "editgroup",
        "is_multivalue": False
    },
    "oxRightEditpassword": {
        "new_key": "editpassword",
        "is_multivalue": False
    },
    "oxRightEditpublicfolders": {
        "new_key": "editpublicfolders",
        "is_multivalue": False
    },
    "oxRightEditresource": {
        "new_key": "editresource",
        "is_multivalue": False
    },
    "oxRightIcal": {
        "new_key": "ical",
        "is_multivalue": False
    },
    "oxRightMultiplemailaccounts": {
        "new_key": "multiplemailaccounts",
        "is_multivalue": False
    },
    "oxRightReadcreatesharedfolders": {
        "new_key": "readcreatesharedfolders",
        "is_multivalue": False
    },
    "oxRightSubscription": {
        "new_key": "subscription",
        "is_multivalue": False
    },
    "oxRightTasks": {
        "new_key": "tasks",
        "is_multivalue": False
    },
    "oxRightVcard": {
        "new_key": "vcard",
        "is_multivalue": False
    },
    "oxRightWebdav": {
        "new_key": "webdav",
        "is_multivalue": False
    },
    "oxRightWebmail": {
        "new_key": "webmail",
        "is_multivalue": False
    },
    "oxRightUsm": {
        "new_key": "usm",
        "is_multivalue": False
    },
    "oxRightActivesync": {
        "new_key": "activesync",
        "is_multivalue": False
    },
    "oxRightDeniedportal": {
        "new_key": "deniedportal",
        "is_multivalue": False
    },
    "oxRightGlobaladdressbookdisabled": {
        "new_key": "globaladdressbookdisabled",
        "is_multivalue": False
    },
    "oxRightInfostore": {
        "new_key": "infostore",
        "is_multivalue": False
    },
    "oxRightPublicfoldereditable": {
        "new_key": "publicfoldereditable",
        "is_multivalue": False
    },
    "oxRightSyncml": {
        "new_key": "syncml",
        "is_multivalue": False
    },
    "oxRightWebdavxml": {
        "new_key": "webdavxml",
        "is_multivalue": False
    }
}


logger = logging.getLogger("univention.ox")
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

# FIXME: ox-connector needs to keep track of the previous objects ox-context
# id and uid (username)
ox_contexts = KeyValueStore("contexts.db")
ox_db_id = KeyValueStore("ox_db_id.db")
usernames = KeyValueStore("usernames.db")


class FakeObject:

    def __init__(self, attributes):
        self.attributes = attributes


def _get_existing_object_ox_id(distinguished_name):
    """
    Get the object OX ID from the known objects, avoiding the old.db and
    storing JSON files. Used to overwrite `get_old_obj` in
    `univention-ox-provisioning/univention/ox/provisioning/helpers.py`.

    Args:
        distinguished_name (str): Distinguished name of the object

    Returns:
        FakeObject: Object with the `oxContext` in attributes, to avoid
                    loading an object from a JSON file and storing it.
    """
    object_ox_id = ox_contexts.get(distinguished_name)
    object_ox_db_id = ox_db_id.get(distinguished_name)
    object_ox_db_uid = usernames.get(distinguished_name)
    logger.info("Loading object OX ID from known objects")
    fake_obj = FakeObject({
        "oxContext": object_ox_id.decode("utf-8") if object_ox_id else None,
        "oxDbId": object_ox_db_id.decode("utf-8") if object_ox_db_id else None,
        "username": object_ox_db_uid.decode("utf-8") if object_ox_db_uid else None
    })
    logger.debug("old object retrieved: %s", fake_obj.attributes)
    return fake_obj


helpers.get_old_obj = _get_existing_object_ox_id


def unpack_values(values_list: list, is_multivalue: bool = False):
    """
    Unpack LDAP list of binary values to a list of strings.

    :param values_list: list of binary values

    :return: string if single value or list of strings
    """
    if len(values_list) == 1:
        if is_multivalue:
            return [values_list[0].decode()]
        try:
            return values_list[0].decode()
        except UnicodeDecodeError:
            logger.warning('unpack_values UnicodeDecodeError, trying base64 image')
            # Handle images
            return base64.b64encode(values_list[0]).decode()
    string_values = []
    for v in values_list:
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


def unpack_dictionary(old: dict) -> dict:
    """
    Convert the LDAP object to a dictionary with unpacked string values.

    :param old: dict of LDAP object

    :return: dict with single string or list of strings values.
    """
    udm_object = {}
    for k, v in old.items():
        # kerberos keys should not be mapped neither used
        if v is None or 'krb5' in k:
            continue
        if k in ldap_to_udm_keys_mapping:
            udm_object[ldap_to_udm_keys_mapping[k]['new_key']] = unpack_values(
                v, ldap_to_udm_keys_mapping[k]['is_multivalue']
            )
            # Some LDAP attributes are mapped to multiple UDM attributes
            if "second_new_key" in ldap_to_udm_keys_mapping[k].keys():
                udm_object[ldap_to_udm_keys_mapping[k]['second_new_key']] = unpack_values(
                    v, ldap_to_udm_keys_mapping[k]['is_multivalue'])
        else:
            udm_object[k] = unpack_values(v)

    # A groups key must be there on functional_account even if empty
    if unpack_values(old.get('univentionObjectType', [])) == 'oxmail/functional_account':
        udm_object['groups'] = udm_object.get('groups', [])
    # A users key must be there on groups even if empty
    if unpack_values(old.get('univentionObjectType', [])) == 'groups/group':
        udm_object['users'] = udm_object.get('users', [])
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

    class Configuration(ListenerModuleHandler.Configuration):
        name = name
        description = (
            'Handle LDAP-changes for various OX objects, users and groups'
        )
        # oxmail/oxcontext, oxresources/oxresources, users/user, groups/group, oxmail/accessprofile, oxmail/functional_account
        ldap_filter = "(|(univentionObjectType=users/user)(univentionObjectType=oxmail/oxcontext)(univentionObjectType=oxresources/oxresources)(univentionObjectType=groups/group)(univentionObjectType=oxmail/accessprofile)(univentionObjectType=oxmail/functional_account))" if os.path.exists('/tmp/initialized.lock') else "(|(univentionObjectType=oxmail/oxcontext)(univentionObjectType=oxmail/accessprofile))"

    def initialize(self):
        self.logger.info('ox-listener-service module initialize')
        self.logger.info(self.config.ldap_filter)

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
        obj.old_distinguished_name = None
        obj.old_attributes = None
        obj.old_options = None
        obj._old_loaded = True
        try:
            run(obj)
            if obj.attributes.get("oxContext") is not None:
                self.logger.info("Storing object OX ID in known objects")
                ox_contexts.set(dn, obj.attributes['oxContext'])
            if obj.attributes.get("oxDbId") is not None:
                self.logger.info("Storing object OX DB ID in known objects")
                ox_db_id.set(dn, obj.attributes['oxDbId'])
            if obj.attributes.get("username") is not None:
                self.logger.info("Storing object username in known objects")
                usernames.set(dn, obj.attributes['username'])
        except Exception as err:
            self.logger.exception('[ create ] create run failed')
            self.logger.warning(err)
            raise
        self.logger.debug('[ create ] end of create')


    def modify(self, dn, old, new, old_dn):
        self.logger.info('[ modify ] dn: %r', dn)
        fake_new_udm_obj = format_as_udm_object(new)
        obj = TriggerObject(
            fake_new_udm_obj['id'],
            fake_new_udm_obj['udm_object_type'],
            fake_new_udm_obj['dn'],
            fake_new_udm_obj['object'],
            fake_new_udm_obj['options'],
            None,
        )
        # Emulate the listener_trigger.load_old() method
        fake_old_udm_obj = format_as_udm_object(old)
        obj.old_distinguished_name = fake_old_udm_obj["dn"]
        obj.old_attributes = fake_old_udm_obj["object"]
        obj.old_options = fake_old_udm_obj["options"]
        obj._old_loaded = True
        try:
            run(obj)
            if (obj.attributes.get("oxContext") is not None and
                    obj.attributes.get("oxContext") != obj.old_attributes.get("oxContext")):
                self.logger.info(
                    "Updating object OX ID in known objects from %s to %s",
                    obj.old_attributes.get("oxContext"),
                    obj.attributes.get("oxContext")
                )
                ox_contexts.set(dn, obj.attributes['oxContext'])
            if (obj.attributes.get("oxDbId") is not None and obj.attributes.get("oxDbId") != obj.old_attributes.get("oxDbId")):
                self.logger.info(
                    "Updating object OX DB ID in known objects from %s to %s",
                    obj.old_attributes.get("oxDbId"),
                    obj.attributes.get("oxDbId")
                )
                ox_db_id.set(dn, obj.attributes['oxDbId'])
            if (obj.attributes.get("username") is not None and obj.attributes.get("username") != obj.old_attributes.get("username")):
                self.logger.info(
                    "Updating object username in known objects from %s to %s",
                    obj.old_attributes.get("username"),
                    obj.attributes.get("username")
                )
                usernames.set(dn, obj.attributes['username'])
        except Exception as err:
            self.logger.exception('[ modify ] modify run failed')
            self.logger.debug(err)
            raise
        if old_dn:
            self.logger.debug('it is (also) a move! old_dn: %r, old_dn')
        self.logger.debug('changed attributes %r', new)
        self.logger.debug('[ modify ] end of modify')

    def remove(self, dn, old):
        self.logger.info('[ remove ] dn: %r', dn)
        fake_old_udm_obj = format_as_udm_object(old)
        obj = TriggerObject(
            fake_old_udm_obj['id'],
            fake_old_udm_obj['udm_object_type'],
            fake_old_udm_obj['dn'],
            None,  # for listener_trigger.TriggerObject.was_deleted() method
            fake_old_udm_obj['options'],
            None,
        )
        obj.old_distinguished_name = fake_old_udm_obj["dn"]
        obj.old_attributes = fake_old_udm_obj["object"]
        obj.old_options = fake_old_udm_obj["options"]
        obj._old_loaded = True
        run(obj)
        if obj.old_attributes.get("oxContext") is not None:
            self.logger.info("Removing object OX ID from known objects")
            ox_contexts.set(dn, os.environ.get("DEFAULT_CONTEXT", "10"))
        # TODO: is deleting usernames and db_id from known objects needed?
        self.logger.debug('[ remove ] end of remove')



# [EOF]
