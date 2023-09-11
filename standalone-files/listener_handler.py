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

# included
import os
import logging

# 3rd party
from univention.listener.handler import ListenerModuleHandler

# internal
from univention.ox.provisioning import helpers, run
from listener_trigger import TriggerObject, KeyValueStore

from ox_mappings import format_as_udm_object

name = 'ox-listener-service'

# FIXME:
# Currently we receive LDAP objects from UDL, while the OX Connector was
# designed to receive UDM objects. This means we need to map the LDAP
# objects to UDM objects. This is temporary, until the new provisioning is
# in place.

logger = logging.getLogger("univention.ox")
logger.setLevel(os.environ.get("LOG_LEVEL", "INFO"))

# FIXME: ox-connector needs to locally keep track of the previous objects
# ox-context id and uid (username). This was previously not needed since it
# was requested to OX when needed, but it slowed down the processing.
# We are using their KeyValueStore (dbm.gnu) to store the values.
ox_contexts = KeyValueStore("contexts.db")
ox_db_id = KeyValueStore("ox_db_id.db")
usernames = KeyValueStore("usernames.db")


class FakeObject:
    """
    Object to fake load of the `old` stored object.

    Args:
        attributes (dict): Attributes of the object is the only field needed
                           and used by the `univention-ox-provisioning`
                           helpers.
    """

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
    fake_obj = FakeObject(
        {
            "oxContext": object_ox_id.decode("utf-8")
            if object_ox_id
            else None,
            "oxDbId": object_ox_db_id.decode("utf-8")
            if object_ox_db_id
            else None,
            "username": object_ox_db_uid.decode("utf-8")
            if object_ox_db_uid
            else None,
        },
    )
    logger.debug("old object retrieved: %s", fake_obj.attributes)
    return fake_obj


# Overwrite the `get_old_obj` function in the helpers module
helpers.get_old_obj = _get_existing_object_ox_id


class OxConnectorListenerModule(ListenerModuleHandler):
    class Configuration(ListenerModuleHandler.Configuration):
        name = name
        description = (
            'Handle LDAP-changes for various OX objects, users and groups'
        )
        # Univention Directory Listener is started twice: first time with a
        # filter that only matches the OX contexts and access profiles, then a
        # second time with the full filter wanted by the ox-connector. This
        # is due to Univention Directory Listener not sending the events in
        # order until the listener is initialized, causing issues when i.e
        # creating a user in a context that has not been provisioned yet.
        ldap_filter = (
            "(|"
            "(univentionObjectType=users/user)"
            "(univentionObjectType=oxmail/oxcontext)"
            "(univentionObjectType=oxresources/oxresources)"
            "(univentionObjectType=groups/group)"
            "(univentionObjectType=oxmail/accessprofile)"
            "(univentionObjectType=oxmail/functional_account)"
            ")"
            if os.path.exists('/tmp/initialized.lock')
            else "(|"
            "(univentionObjectType=oxmail/oxcontext)"
            "(univentionObjectType=oxmail/accessprofile))"
        )

    def initialize(self):
        self.logger.info('ox-listener-service module initialize')
        self.logger.info(
            "Using the following LDAP filter: %s",
            self.config.ldap_filter,
        )

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
        # Emulate the listener_trigger.load_old() method
        obj.old_distinguished_name = None
        obj.old_attributes = None
        obj.old_options = None
        obj._old_loaded = True
        try:
            run(obj)
            # Store the needed values to keep track of the objects locally.
            # For more details, see KeyValueStore objects FIXME above.
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
        if old_dn:
            self.logger.debug('it is (also) a move! old_dn: %r', old_dn)
        fake_new_udm_obj = format_as_udm_object(new)
        # Emulate the listener_trigger.load_old() method
        fake_old_udm_obj = format_as_udm_object(old)
        obj = TriggerObject(
            fake_new_udm_obj['id'],
            fake_new_udm_obj['udm_object_type'],
            fake_new_udm_obj['dn'],
            fake_new_udm_obj['object'],
            fake_new_udm_obj['options'],
            None,
        )
        obj.old_distinguished_name = fake_old_udm_obj["dn"]
        obj.old_attributes = fake_old_udm_obj["object"]
        obj.old_options = fake_old_udm_obj["options"]
        obj._old_loaded = True
        try:
            run(obj)
            # Store the needed values to keep track of the objects locally.
            # For more details, see KeyValueStore objects FIXME above.
            if obj.attributes:
                if obj.attributes.get("oxContext") is not None and (
                    obj.attributes.get("oxContext")
                    != obj.old_attributes.get("oxContext")
                ):
                    self.logger.info(
                        "Updating object OX ID in known objects from %s to %s",
                        obj.old_attributes.get("oxContext"),
                        obj.attributes.get("oxContext"),
                    )
                    ox_contexts.set(dn, obj.attributes['oxContext'])
                if obj.attributes.get("oxDbId") is not None and (
                    obj.attributes.get("oxDbId")
                    != obj.old_attributes.get("oxDbId")
                ):
                    self.logger.info(
                        "Updating object OX DB ID in known objects from %s to %s",
                        obj.old_attributes.get("oxDbId"),
                        obj.attributes.get("oxDbId"),
                    )
                    ox_db_id.set(dn, obj.attributes['oxDbId'])
                if obj.attributes.get("username") is not None and (
                    obj.attributes.get("username")
                    != obj.old_attributes.get("username")
                ):
                    self.logger.info(
                        "Updating object username in known objects from %s to %s",
                        obj.old_attributes.get("username"),
                        obj.attributes.get("username"),
                    )
                    usernames.set(dn, obj.attributes['username'])
        except Exception as err:
            self.logger.exception('[ modify ] modify run failed')
            self.logger.debug(err)
            raise
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
