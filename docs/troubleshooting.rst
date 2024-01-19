.. SPDX-FileCopyrightText: 2021-2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _app-troubleshooting:

***************
Troubleshooting
***************

When you encounter problems with the operation of the :program:`OX Connector`
app, this section provides information where you can look closer into and to
get an impression about what's going wrong.

.. _log-files:

Log files
=========

The :program:`OX Connector` app produces different logging information in
different places.

.. index::
   pair: listener converter; log file

Listener Converter: :file:`/var/log/univention/listener_modules/ox-connector.log`
   Contains log information from the :term:`Listener Converter` about create,
   update and delete actions of objects.

   It also shows warnings and errors when the OX Connector configuration isn't
   correct, or the connector can't establish a connection to the :term:`SOAP
   API`.

.. index::
   single: log file; app center

App Center: :file:`/var/log/univention/appcenter.log`
   Contains log information around activities in the App Center.

   The App Center writes OX Connector relevant information to this file, when
   you run app lifecycle tasks like install, update and uninstall or when you
   change the app settings.

.. index::
   single: log file; domain join

Domain join: :file:`/var/log/univention/join.log`
   Contains log information from the join processes. When the App Center install
   OX Connector, the app also joins the domain.

.. _health-check:

Health check
============

.. index::
   pair: listener converter; health check
   pair: listener; health check

First, have a look at the log file for the :term:`Listener Converter` and look
for warnings and errors, see :ref:`log-files`.

The OX Connector has a good health when the number of files for provisioning
for the :term:`Listener` and the :term:`Listener Converter` is low. For a quick
verification, run the following command on the UCS system with the OX Connector
installed:

.. code-block:: console
   :caption: Verify the number of unprocessed files for the :term:`Listener`.

   $ DIR_LISTENER="/var/lib/univention-appcenter/listener/ox-connector"
   $ ls -1 "$DIR_LISTENER"/*.json 2> /dev/null | wc -l
   0

.. code-block:: console
   :caption: Verify the number of unprocessed files for the :term:`Listener Converter`.

   $ DIR_CONVERTER="/var/lib/univention-appcenter/apps/ox-connector/data/listener"
   $ ls -1 "$DIR_CONVERTER"/*.json 2> /dev/null | wc -l
   0

The :term:`Listener Converter` logs consecutive errors in the log file, for
example:

.. code-block:: text

   INFO    This is consecutive error #{some number}

Such entries indicate that the provisioning has issues with processing the
queue. For more information, see :ref:`trouble-queue`.

You can use the script `get_current_error.py` to automate the health check
on your preferred monitoring system.

.. code-block:: console

   univention-app shell ox-connector /usr/local/share/ox-connector/resources/get_current_error.py

This script outputs a json with some information about the current state of the OX Connector.

If there is an error:

.. code-block:: console

   {'errors': '10', 'message': "HTTPSConnectionPool(host='ucs11.ucs.net', port=443): Max retries exceeded with url: /webservices/OXContextService?wsdl (Caused by NewConnectionError('<urllib3.connection.HTTPSConnection object at 0x7f7b1083a610>: Failed to establish a new connection: [Errno 111] Connection refused'))", 'filename': '/var/lib/univention-appcenter/apps/ox-connector/data/listener/2023-12-11-11-22-22-856263.json'}

If the ox-connector is working:

.. code-block:: console

   {'errors': '0'}

The script `get_current_error.py` can easily be integrated into a Nagios plugin script, as shown in the following example:

.. code-block:: bash

    #!/bin/bash

    nagiosCheck () {
        result=$(/var/lib/univention-appcenter/apps/ox-connector/data/resources/get_current_error.py)
        status=$(echo ${result} | jq ' if .errors == "0" then 0 else 1 end')

        case $status in
        0)
            echo "OK: No errors found."
            exit 0
            ;;
        1)
            error_msg=$(echo ${result} | jq ' .message ')
            error_file=$(echo ${result} | jq ' .filename ')
            echo "WARNING: ${error_msg}. This error is caused by the listener file ${error_file}"
            exit 1
            ;;
        esac
    }

    nagiosCheck


.. _provision-stopped:

Provisioning stops working
==========================

.. index::
   single: provisioning; stopped
   single: provisioning; faulty item

When the provisioning stopped working, a previous change in |UDM| is a
probable reason and the OX Connector doesn't know how to proceed. The connector
retries the action over and over again until an administrator repairs the cause
manually.

First, see the :ref:`log-files` and look for warnings and errors. If it's not a
temporary problem like for example network connectivity, the fix requires manual
action.

As a last resort, the administrator can delete the flawed file. The log file
reveals the flawed file and its path, see :ref:`queue-delete-one`.

.. _trouble-queue:

Queuing
=======

.. index::
   single: provisioning; queue
   see: queue; provisioning

The queue for provisioning consists of JSON files. :ref:`app-how-it-works`
describes the connector's data processing. Administrators can manually intervene
with the queue in the following cases.

.. _queue-delete-one:

Delete one item from the queue
------------------------------

Administrators can remove an item in the queue, if the connector can't process
it and interrupts the provisioning process. The connector retries to
provision this item and continually fails.

To find and remove the problematic item from the queue, follow these steps:

#. Open the log file of the :term:`Listener Converter`. For the log file
   location, see :ref:`log-files`.

#. Find the filename of the item that the *Listener Converter* retries to
   provision. For example, the log file shows:

   .. code-block:: text

      Error while processing /var/lib/univention-appcenter/apps/ox-connector/data/listener/$timestamp.json

   ``$timestamp`` has the format ``%Y-%m-%d-%H-%M-%S``.

#. Remove the problematic item:

   .. code-block:: console

      $ rm /var/lib/univention-appcenter/apps/ox-connector/data/listener/$timestamp.json

.. _queue-reprovision-one:

Re-provision one specific UDM object
------------------------------------

The OX Connector allows to re-provision one UDM object to OX App Suite. The
following snippet provisions one user object:

.. code-block:: bash
   :caption: Re-provision one UDM object

   DN="uid=user100,cn=users,$(ucr get ldap/base)"
   ENTRY_UUID="$(univention-ldapsearch -b "$DN" + | grep entryUUID | awk '{ print $2 }')"
   cat > /var/lib/univention-appcenter/listener/ox-connector/$(date +%Y-%m-%d-%H-%M-%S).json <<- EOF
   {
       "entry_uuid": "$ENTRY_UUID",
       "dn": "$DN",
       "object_type": "users/user",
       "command": "modify"
   }
   EOF

.. _queue-reprovision-all:

Re-provision all data
---------------------

.. warning::

   Depending on the number of users and groups in the UCS LDAP directory, this
   task may take a lot of time.

   **Reprovisioning all data isn't recommended.**

The following command reads all |UDM| objects from the |UCS| LDAP directory and
adds them to the provisioning queue:

.. code-block:: console
   :caption: Re-provisioning all UDM objects to OX App Suite

   $ univention-directory-listener-ctrl resync ox-connector

The re-provisioning won't run any *delete* operations, because the Listener
only adds existing UDM objects to the queue.

.. caution::

   The OX Connector may decide to delete objects based on data in the JSON
   files. For example ``isOxGroup = Not`` in a group object.

.. _cache-rebuild:

Rebuild cache
=============

.. index::
   single: cache; rebuild

The *internal ID* of objects in the database of OX App Suite can become
corrupted, for example after a backup restore of the database. For more
information about the cache, see :ref:`cache-internal-id`.

To rebuild the cache, run the following commands:

.. code-block:: console
   :caption: Rebuild cache for *internal ID*

   $ univention-app shell ox-connector
   /oxp # update-ox-db-cache --delete
   /oxp # update-ox-db-cache

.. versionchanged:: 2.0.0

   Rebuild the cache after an update to version 2.0.0, because previous
   versions didn't maintain the cache for the *internal ID*.

   Otherwise, the OX Connector app falls back into the much slower mechanism and
   runs a database query per user during the provisioning.

.. tip::

   Retrieve all users per context in one request
      Rebuilding the cache may take a long time and depends on the amount of
      users in the OX App Suite database.

      :command:`update-ox-db-cache --build-cache` can speed up the rebuild,
      because it retrieves all users of a context with one request.

.. warning::

   .. index::
      single: cache; memory consumption
      single: cache; system load

   Memory consumption
      On the UCS system with the OX Connector, the rebuild process may use up to
      1 GB memory per 10,000 users in the database for OX App Suite.

   System load
      Furthermore, the process may generate a lot of load on the OX App Suite
      system and the OX Connector app.

Duplicated *displaynames*
=========================

In OX Connector version 2.2.0 the UDM property *oxDisplayName* does not have a
unique constraint anymore.

If duplicate values are used, but OX is not prepared for that, the *SOAP API* calls will
fail with the following exception.

.. code-block:: console

   2023-05-30 11:59:31 WARNING Traceback (most recent call last):
   2023-05-30 11:59:31 WARNING   File "/tmp/univention-ox-connector.listener_trigger", line 324, in run_on_files
   2023-05-30 11:59:31 WARNING     f(obj)
   2023-05-30 11:59:31 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/provisioning/__init__.py", line 86, in run
   2023-05-30 11:59:31 WARNING     modify_user(obj)
   2023-05-30 11:59:31 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/provisioning/users.py", line 420, in modify_user
   2023-05-30 11:59:31 WARNING     user.modify()
   2023-05-30 11:59:31 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/soap/backend.py", line 477, in modify
   2023-05-30 11:59:31 WARNING     super(SoapUser, self).modify()
   2023-05-30 11:59:31 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/soap/backend.py", line 180, in modify
   2023-05-30 11:59:31 WARNING     self.service(self.context_id).change(obj)
   2023-05-30 11:59:31 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/soap/services.py", line 536, in change
   2023-05-30 11:59:31 WARNING     return self._call_ox('change', usrdata=user)
   2023-05-30 11:59:31 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/soap/services.py", line 163, in _call_ox
   2023-05-30 11:59:31 WARNING     return getattr(service, func)(**kwargs)
   2023-05-30 11:59:31 WARNING   File "/usr/lib/python3.9/site-packages/zeep/proxy.py", line 46, in __call__
   2023-05-30 11:59:31 WARNING     return self._proxy._binding.send(
   2023-05-30 11:59:31 WARNING   File "/usr/lib/python3.9/site-packages/zeep/wsdl/bindings/soap.py", line 135, in send
   2023-05-30 11:59:31 WARNING     return self.process_reply(client, operation_obj, response)
   2023-05-30 11:59:31 WARNING   File "/usr/lib/python3.9/site-packages/zeep/wsdl/bindings/soap.py", line 229, in process_reply
   2023-05-30 11:59:31 WARNING     return self.process_error(doc, operation)
   2023-05-30 11:59:31 WARNING   File "/usr/lib/python3.9/site-packages/zeep/wsdl/bindings/soap.py", line 329, in process_error
   2023-05-30 11:59:31 WARNING     raise Fault(
   2023-05-30 11:59:31 WARNING zeep.exceptions.Fault: The displayname is already used; exceptionId 1170523631-4

To fix this issue, a change in the  *OX App Suite* configuration is required.
Add the following lines to the :file:`user.properties` file.

.. code-block:: console

   com.openexchange.user.enforceUniqueDisplayName=false
   com.openexchange.folderstorage.database.preferDisplayName=false

.. note::
   This is configured by default in the *OX App Suite* installation from the App center.


Traceback provisioning *groups*
===============================

When an ox group is synchronized, the :program:`OX Connector` obtains information about all
its users by reading from the `listener/old` directory where the latest version of the objects
that have already been synchronized is stored. If any user is part of such group but is not in
`listener/old`, the :program:`OX Connector` will fail with a traceback like the following:

.. code-block:: console

   2023-11-17 09:21:20 INFO    Loading old object from /var/lib/univention-appcenter/apps/ox-connector/data/listener/old/d52a12f0-2d89-103c-82b6-b945bc689f52.json
   2023-11-17 09:21:20 INFO    Loading old object from /var/lib/univention-appcenter/apps/ox-connector/data/listener/old/f029fd00-8247-103c-89e3-bd95c6adf546.json
   2023-11-17 09:21:20 INFO    Error while processing /var/lib/univention-appcenter/apps/ox-connector/data/listener/2023-02-27-13-30-03-471251.json
   2023-11-17 09:21:20 WARNING Traceback (most recent call last):
   2023-11-17 09:21:20 WARNING   File "/tmp/univention-ox-connector.listener_trigger", line 341, in run_on_files
   2023-11-17 09:21:20 WARNING     function(obj)
   2023-11-17 09:21:20 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/provisioning/__init__.py", line 103, in run
   2023-11-17 09:21:20 WARNING     for new_obj in get_group_objs(obj):
   2023-11-17 09:21:20 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/provisioning/__init__.py", line 156, in get_group_objs
   2023-11-17 09:21:20 WARNING     user_obj = univention.ox.provisioning.helpers.get_old_obj(user)
   2023-11-17 09:21:20 WARNING   File "/tmp/univention-ox-connector.listener_trigger", line 72, in _get_old_object
   2023-11-17 09:21:20 WARNING     return object_from_path(path_to_old_user)
   2023-11-17 09:21:20 WARNING   File "/tmp/univention-ox-connector.listener_trigger", line 261, in object_from_path
   2023-11-17 09:21:20 WARNING     entry_uuid = content["id"]
   2023-11-17 09:21:20 WARNING TypeError: 'NoneType' object is not subscriptable
   2023-11-17 09:21:20 INFO    This is consecutive error #18
   2023-11-17 09:21:20 INFO    Sleeping for 0 sec
   2023-11-17 09:21:20 INFO    Successfully processed 0 files during this run

You can check which users are missing in the old directory by running the next command. It
will print the *DN* of the users that need to be provisioned again. Then you can follow
the instructions here :ref:`queue-reprovision-one` to synchronize the missing users.

.. code-block:: bash

   univention-ldapsearch "(&(univentionObjectType=users/user)(isOxUser=OK))" entryUUID | sed -ne 's/entryUUID: //p' | xargs -I{} bash -c "test -e  /var/lib/univention-appcenter/apps/ox-connector/data/listener/old/{}.json || univention-ldapsearch -LLL  entryUUID={} 1.1"


Verify data consistency
=======================

In OX Connector version 2.2.8 a new script called `check_sync_status.py` can be used to verify that the data
in *UDM*, the listener/old directory and the OX database are the same. If the App settings :envvar:`OX_USER_IDENTIFIER`,
:envvar:`OX_GROUP_IDENTIFIER`, :envvar:`OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE`, :envvar:`OX_IMAP_LOGIN` are set to non default
values, the script can detect and report inconsistencies between the OX database, listener files and UDM.

.. code-block:: console

   $ univention-app shell ox-connector
   /oxp # ./check_sync_status.py --dn uid=qwert,cn=users,dc=test,dc=ucs --udm_admin_account administrator --udm_password_file udm.secret --udm_host https://master.master.ucs

.. note::

   `./check_sync_status.py --help`

  --dn DN               Check the object with the specified dn
  --udm_module UDM_MODULE
                        Object's udm module. Required if the property is missing in the old/ directory object.
  --ox_context OX_CONTEXT
                        Object's ox context. Required if the property is missing in the old/ directory object.
  --resync              Re-sync object data by creating a new file in the listener. Re-synchronizing groups will only work if its users are correctly provisioned.
  --udm_admin_account UDM_ADMIN_ACCOUNT
                        Udm user used for connection.
  --udm_password_file UDM_PASSWORD_FILE
                        Udm password
  --udm_host UDM_HOST   Udm host


Collect information for support ticket
======================================

Before you open a support ticket, make sure to collect and provide relevant
details about your case, so that the Univention Support team can help you:

* `Provide relevant details about your environment
  <https://help.univention.com/faq#posting-guidelines>`_.

* Provide the relevant messages and tracebacks from  :ref:`log-files`,
  specifically the :term:`Listener Converter`.

* Describe the steps that can reproduce the faulty behavior.

* Describe the expected behavior.

* Provide data from the provisioning that causes the error.

Invalid values for OX_USER_IDENTIFIER or OX_GROUP_IDENTIFIER
============================================================
Only a UDM user property (or UDM group property in case of OX_GROUP_IDENTIFIER) that contains a **single value** which is **not None**
is a valid option. In case a UDM property that contains an empty value or a list of values is specified, the :program:`OX Connector`
will enter an error state which needs to be resolved manually by simply setting a valid value.

Setting invalid values for the app settings `OX_USER_IDENTIFIER` or `OX_GROUP_IDENTIFIER` will
lead to the following errors:

.. code-block:: console

    2024-01-11 13:57:39 WARNING Traceback (most recent call last):
    2024-01-11 13:57:39 WARNING   File "/tmp/univention-ox-connector.listener_trigger", line 351, in run_on_files
    2024-01-11 13:57:39 WARNING     function(obj)
    2024-01-11 13:57:39 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/provisioning/__init__.py", line 86, in run
    2024-01-11 13:57:39 WARNING     modify_user(obj)
    2024-01-11 13:57:39 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/provisioning/users.py", line 454, in modify_user
    2024-01-11 13:57:39 WARNING     user.modify()
    2024-01-11 13:57:39 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/soap/backend.py", line 475, in modify
    2024-01-11 13:57:39 WARNING     super(SoapUser, self).modify()
    2024-01-11 13:57:39 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/soap/backend.py", line 176, in modify
    2024-01-11 13:57:39 WARNING     assert self.name is not None

.. code-block:: console

    setting "users" udm property for groups
    2024-01-11 13:59:36 WARNING Traceback (most recent call last):
    2024-01-11 13:59:36 WARNING   File "/tmp/univention-ox-connector.listener_trigger", line 351, in run_on_files
    2024-01-11 13:59:36 WARNING     function(obj)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/provisioning/__init__.py", line 108, in run
    2024-01-11 13:59:36 WARNING     modify_group(new_obj)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/provisioning/groups.py", line 146, in modify_group
    2024-01-11 13:59:36 WARNING     group.modify()
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/soap/backend.py", line 180, in modify
    2024-01-11 13:59:36 WARNING     self.service(self.context_id).change(obj)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/soap/services.py", line 607, in change
    2024-01-11 13:59:36 WARNING     return self._call_ox('change', grp=grp)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/soap/services.py", line 194, in _call_ox
    2024-01-11 13:59:36 WARNING     return getattr(service, func)(**kwargs)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/proxy.py", line 46, in __call__
    2024-01-11 13:59:36 WARNING     return self._proxy._binding.send(
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/wsdl/bindings/soap.py", line 123, in send
    2024-01-11 13:59:36 WARNING     envelope, http_headers = self._create(
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/wsdl/bindings/soap.py", line 73, in _create
    2024-01-11 13:59:36 WARNING     serialized = operation_obj.create(*args, **kwargs)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/wsdl/definitions.py", line 224, in create
    2024-01-11 13:59:36 WARNING     return self.input.serialize(*args, **kwargs)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/wsdl/messages/soap.py", line 79, in serialize
    2024-01-11 13:59:36 WARNING     self.body.render(body, body_value)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/elements/element.py", line 232, in render
    2024-01-11 13:59:36 WARNING     self._render_value_item(parent, value, render_path)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/elements/element.py", line 256, in _render_value_item
    2024-01-11 13:59:36 WARNING     return self.type.render(node, value, None, render_path)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/types/complex.py", line 307, in render
    2024-01-11 13:59:36 WARNING     element.render(node, element_value, child_path)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/elements/indicators.py", line 256, in render
    2024-01-11 13:59:36 WARNING     element.render(parent, element_value, child_path)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/elements/element.py", line 232, in render
    2024-01-11 13:59:36 WARNING     self._render_value_item(parent, value, render_path)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/elements/element.py", line 255, in _render_value_item
    2024-01-11 13:59:36 WARNING     return value._xsd_type.render(node, value, xsd_type, render_path)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/types/complex.py", line 307, in render
    2024-01-11 13:59:36 WARNING     element.render(node, element_value, child_path)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/elements/indicators.py", line 256, in render
    2024-01-11 13:59:36 WARNING     element.render(parent, element_value, child_path)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/elements/element.py", line 232, in render
    2024-01-11 13:59:36 WARNING     self._render_value_item(parent, value, render_path)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/elements/element.py", line 256, in _render_value_item
    2024-01-11 13:59:36 WARNING     return self.type.render(node, value, None, render_path)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/types/simple.py", line 96, in render
    2024-01-11 13:59:36 WARNING     node.text = value if isinstance(value, etree.CDATA) else self.xmlvalue(value)
    2024-01-11 13:59:36 WARNING   File "/usr/lib/python3.9/site-packages/zeep/xsd/types/builtins.py", line 27, in _wrapper
    2024-01-11 13:59:36 WARNING     raise ValueError(
    2024-01-11 13:59:36 WARNING ValueError: The String type doesn't accept collections as value
