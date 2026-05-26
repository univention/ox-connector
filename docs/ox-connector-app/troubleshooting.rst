.. SPDX-FileCopyrightText: 2021 - 2025 Univention GmbH
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
   single: database management script; log file

Database management script: :file:`/var/lib/univention-appcenter/apps/ox-connector/data/db.log`
   Contains log information from the `Database management script` that is described below.

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

.. _troubleshoot-listener:

Checking the Listener
=====================

Before checking the OX Connector, you may want to have a look at the connection
between the :term:`Listener` and the :term:`Listener Converter`. The Listener
should create files and the Listener Converter should translate these files
rather quickly.

.. code-block:: console
   :caption: Verify the number of unprocessed files for the :term:`Listener`.

   $ DIR_LISTENER="/var/lib/univention-appcenter/listener/ox-connector"
   $ ls -1 "$DIR_LISTENER"/*.json 2> /dev/null | wc -l
   0

If files here are not created upon a change or are piling up, this indicates a
problem in the Listener or Listener Converter. See :ref:`log-files`.

.. _app-cli:

CLI to monitor the current state
================================

The OX Connector ships a command-line interface that you can use to query and
manipulate the database it uses to keep track of current tasks, objects already
synced and errors it may have found.

.. code-block:: console
   :caption: List all commands of the CLI.

   $ /usr/sbin/univention-ox-connector-task-management --help

The tool operates on the :program:`SQLite` database
:file:`/var/lib/univention-appcenter/apps/ox-connector/data/listener/ox-connector.db`.
The terminology of the tool is as follows:

.. glossary::

   Tasks
      A database table managed by the OX Connector. A row represents an active
      task. The OX Connector iterates over all tasks and synchronizes them to
      the OX App Suite.

   Old
      A database table managed by the OX Connector. A row represents the state
      of an item at the moment it was successfully synchronized. It is more or
      less a copy of a former task. Needed when certain items are synchronized
      and reference other items (e.g., when synchronizing a group that contains
      users). Also used for faster look-ups by storing the database ID given by
      OX.

   Morgue
      A database table managed by the OX Connector. A row represents a failed
      task. It was moved automatically or manually to this table and is not
      actively processed by the OX Connector. Administrators can examine the
      items in the morgue and decide how to proceed with them (see below).

.. _health-check:

Health check
------------

.. index::
   pair: listener converter; health check
   pair: listener; health check

First, have a look at the log file for the :term:`Listener Converter` and look
for warnings and errors, see :ref:`log-files`.

Second you can get a brief summary of current tasks. This can indicate if the
OX Connector can process the items fast enough or at all.

.. code-block:: console
   :caption: Show all tasks the OX Connector is yet to process.

   $ /usr/sbin/univention-ox-connector-task-management summarize-tasks
   $ /usr/sbin/univention-ox-connector-task-management search-tasks

Third, you can get a brief summary of past errors. Every item is an object
not synchronized. Note that this only makes sense should you have chosen
:ref:`limit-continue-at-conflict`.

.. code-block:: console
   :caption: Show all items in the morgue.

   $ /usr/sbin/univention-ox-connector-task-management search-morgue

.. _handling-errors:

Handling errors
---------------

You can decide what to do with the items that have been moved to the morgue.
All commands assume that you have the ``UniventionObjectIdentifier`` of that
object. For each item you have the option to

#. Delete it from the list: It is as if this item never hit the OX Connector.
   The underlying object can of course be synchronized again if it is modified
   in the LDAP directory (creating a completely new item in the OX Connector's
   tasks).

   .. code-block:: console
      :caption: Remove an item from the morgue.

      $ /usr/sbin/univention-ox-connector-task-management remove-from-morgue --obj-id=...

#. Retry the very same item: The erroneous item in the list is again copied to
   the list of tasks, assuming that the problem is now fixed (e.g., a
   validation on the OX App Suite's side has been disabled).

   .. code-block:: console
      :caption: Retry an item from the morgue.

      $ /usr/sbin/univention-ox-connector-task-management retry-from-morgue --obj-id=...

#. Fresh synchronization of the object: The object is again put into the list
   of tasks but not with the attributes it had when the synchronization
   happened (and failed). Instead, it is freshly fetched from the LDAP
   database.

   .. code-block:: console
      :caption: Retry an item from the morgue.

      $ /usr/sbin/univention-ox-connector-task-management resync-item --obj-id=...

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

As a last resort, the administrator can move the task aside. The log file
reveals the ``Database ID`` of that object (e.g. ``uid=...; $object_identifier;
tasks:$database_id``).

.. code-block:: console
   :caption: Retry an error from the list.

   $ /usr/sbin/univention-ox-connector-task-management move-task-to-morgue --task-id=$database_id  --error-msg="Manual intervention after careful consideration"

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

Ensuring the OX database ID integrity
=====================================

.. index::
   single: cache; rebuild

The *internal ID* of objects in the database of OX App Suite can become
corrupted, for example after a backup restore of the database. For more
information about the cache, see :ref:`db-old-entries`.

To rewrite that cache, run the following commands:

.. code-block:: console
   :caption: Rebuild cache for *internal ID*

   $ /usr/sbin/univention-ox-connector-task-management rewrite-ox-db-id

.. tip::

   Retrieve all users per context in one request
      Rebuilding the cache may take a long time and depends on the amount of
      users in the OX App Suite database.

      :command:`/usr/sbin/univention-ox-connector-task-management
      rewrite-ox-db-id --build-cache-size=1000` can speed up the rebuild,
      because it retrieves up to 1000 users of one context with one request.

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

   2024-11-15 16:06:33 INFO    Group oxgroup will be OX Group
   2024-11-15 16:06:33 INFO    Error while processing /var/lib/univention-appcenter/apps/ox-connector/data/listener/2024-11-15-15-51-31-669745.json
   2024-11-15 16:06:33 INFO    This is consecutive error #11
   2024-11-15 16:06:33 INFO    Sleeping for 0 sec
   2024-11-15 16:06:33 WARNING Traceback (most recent call last):
   2024-11-15 16:06:33 INFO    Successfully processed 0 files during this run
   2024-11-15 16:06:33 WARNING   File "/tmp/univention-ox-connector.listener_trigger", line 419, in run_on_files
   2024-11-15 16:06:33 WARNING     function(obj)
   2024-11-15 16:06:33 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/provisioning/__init__.py", line 115, in run
   2024-11-15 16:06:33 WARNING     for new_obj in get_group_objs(obj):
   2024-11-15 16:06:33 WARNING   File "/usr/lib/python3.9/site-packages/univention/ox/provisioning/__init__.py", line 173, in get_group_objs
   2024-11-15 16:06:33 WARNING     user_obj = univention.ox.provisioning.helpers.get_old_obj(user)
   2024-11-15 16:06:33 WARNING   File "/tmp/univention-ox-connector.listener_trigger", line 76, in _get_old_object
   2024-11-15 16:06:33 WARNING     raise Exception(f"Old object file {path_to_old_user} for {distinguished_name} does not exist!\nYou need to re-provision \"{distinguished_name}\" (see https://docs.software-univention.de/ox-connector-app/latest/troubleshooting  .html#traceback-provisioning-groups).")
   2024-11-15 16:06:33 WARNING Exception: Old object file /var/lib/univention-appcenter/apps/ox-connector/data/listener/old/d10338de-3144-103f-8ea2-f39fa7a811dd.json for uid=oxuser1,cn=users,dc=example,dc=com does not exist!
   2024-11-15 16:06:33 WARNING You need to re-provision "uid=oxuser1,cn=users,dc=example,dc=com" (see https://docs.software-univention.de/ox-connector-app/latest/troubleshooting.html#traceback-provisioning-groups).

You need to re-provision the user object
(*uid=oxuser1,cn=users,dc=example,dc=com* in this case) manually. Follow the
instructions in :ref:`handling-errors` to synchronize the missing users.
After this manual intervention the connector automatically continues with the
synchronization of the group object.

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
    2024-01-11 13:57:39 WARNING No name for this attribute. Missing or misconfigured identifier app settings
    2024-01-11 13:57:39 WARNING (OX_USER_IDENTIFIER or OX_GROUP_IDENTIFIER) might be the reason, see
    2024-01-11 13:57:39 WARNING https://docs.software-univention.de/ox-connector-app/latest/troubleshooting.html#invalid-values-for-ox-user-identifier-or-ox-group-identifier
    2024-01-11 13:57:39 WARNING for more information.

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

.. _app-troubleshooting-migration:

Troubleshooting migration of functional accounts to shared accounts
===================================================================

During the :ref:`migration of functional accounts to shared accounts <usage-shared-accounts-migration>`,
a network failure or another unexpected error can leave a shared account half-configured.
You might encounter one of the following states:

Functional account still exists
   The functional account is still present,
   and the shared account is partially configured.
   Rerun the script with the same parameters as before
   to retry the migration.

Functional account doesn't exist anymore
   The functional account doesn't exist anymore,
   so the migration is nearly complete.
   The remaining step is to modify the email address of the shared account
   and remove the ``tmp_`` prefix.
   To remove the prefix,
   use either the *Management UI* or the :command:`udm` command.

   .. tab-set::

      .. tab-item:: Management UI

         Use the following steps:

         #. Sign in to the *Management UI*
            and navigate to the :external+uv-nubus-manual:ref:`nubus-domain-ldap`.

         #. Select the container for the shared accounts.
            The default container is :samp:`cn=shared_accounts,cn=open-xchange,{<ldap_base>}`.

         #. Open the affected shared account.

         #. Change the email address and remove the ``tmp_`` prefix.

         #. Click :guilabel:`Save`.

         Verify that the shared account uses the expected email address
         and no longer has the ``tmp_`` prefix.

      .. tab-item:: UDM command-line

         To remove the prefix by using the :command:`udm` command
         in Nubus for UCS,
         run the command shown in :numref:`app-troubleshooting-migration-remove-prefix-listing`.
         Define the following parameters:

         :``SHARED_ACCOUNT``: The DN of the affected shared account,
            for example ``"cn=test,cn=shared_accounts,cn=open-xchange,$(ucr get ldap/base)"``
         :``EMAIL``: The email address of the shared account.

         .. code-block:: console
            :caption: Remove the ``tmp_`` prefix from the email address of a shared account
            :name: app-troubleshooting-migration-remove-prefix-listing

            $ export SHARED_ACCOUNT="<DN of affected shared account>"
            $ export EMAIL="<email address of the shared account>"
            $ udm \
               oxmail/shared_account \
               modify \
               --dn "$SHARED_ACCOUNT" \
               --set mailPrimaryAddress="$EMAIL"

         Verify that the shared account uses the expected email address
         and no longer has the ``tmp_`` prefix.
