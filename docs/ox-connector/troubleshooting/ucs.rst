.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-troubleshooting-ucs:

******************************************
Troubleshoot OX Connector on Nubus for UCS
******************************************

Use this page to troubleshoot problems with the *OX Connector* app on Nubus for UCS.
It explains how to inspect log files.
It also covers known problems,
including duplicate display names, missing group members,
and invalid identifier values.

.. _ox-connector-troubleshooting-ucs-log-files:

Log files
=========

The *OX Connector* app writes logs to several locations.
This section lists the log file per involved component.

.. _ox-connector-troubleshooting-ucs-log-files-consumer:

OX Connector Provisioning Consumer
   Standard output of the *OX Connector* container.
   To read the output, run the command in :numref:`ox-connector-troubleshooting-ucs-log-files-listing`.

   Contains log information from the :term:`OX Connector Provisioning Consumer`
   about object create, update, and delete actions.
   It also reports warnings and errors when the *OX Connector* configuration isn't
   correct or the connector can't connect to the :term:`SOAP API`.

   .. code-block:: console
      :caption: View the log output of the OX Connector Provisioning Consumer
      :name: ox-connector-troubleshooting-ucs-log-files-listing

      $ univention-app logs ox-connector

.. _ox-connector-troubleshooting-ucs-log-files-provisioning:

Provisioning Service
   :file:`/var/log/univention/listener_modules/nubus-provisioning.log`

   Contains log information from the :term:`Provisioning Service`
   about changes detected in the LDAP directory
   and delivered to subscribed services.
   The Provisioning Service containers write additional log information
   to :file:`/var/log/syslog`.

.. _ox-connector-troubleshooting-ucs-log-files-database-management:

Database management script
   :file:`/var/lib/univention-appcenter/apps/ox-connector/data/univention-ox-connector-task-management.log`

   Contains log information from the database management script described in
   :ref:`ox-connector-troubleshooting-manage-provisioning-tasks`.

.. _ox-connector-troubleshooting-ucs-log-files-app-center:

App Center
   :file:`/var/log/univention/appcenter.log`

   Contains log information about *App Center* activities.

   The *App Center* writes *OX Connector*-related information to this file
   when you run app lifecycle tasks, such as installing, updating,
   or uninstalling the app, or when you change the app settings.

   For information about *App Center* logging and diagnostics,
   see :external+uv-ucs-operation:ref:`lifecycle-app-center-troubleshooting-logging`
   in :cite:t:`uv-ucs-operation`.

.. _ox-connector-troubleshooting-ucs-log-files-join:

Domain join
   :file:`/var/log/univention/join.log`

   Contains log information from domain join processes.
   When the *App Center* installs *OX Connector*, the app also joins the domain.

   For information about the domain join process,
   see :external+uv-ucs-operation:ref:`domain-infrastructure-join-process`
   in :cite:t:`uv-ucs-operation`.

.. _ox-connector-troubleshooting-ucs-database-integrity:

Ensure OX database ID integrity
===============================

The *OX Connector* caches the internal IDs that *OX App Suite* assigns to objects.
After you restore an *OX App Suite* database backup,
the cached IDs can become stale or inconsistent.
For more information about the cache,
see :ref:`ox-connector-architecture-ucs-database`.

To rebuild the cache,
run the command in :numref:`ox-connector-troubleshooting-ucs-rebuild-ox-db-id-listing`.

.. code-block:: console
   :caption: Rebuild cache for *internal ID*
   :name: ox-connector-troubleshooting-ucs-rebuild-ox-db-id-listing

   $ /usr/sbin/univention-ox-connector-task-management rewrite-ox-db-id

.. tip::

   Retrieve all users per context in one request
      Rebuilding the cache can take a long time
      and depends on the number of users in the *OX App Suite* database.

      The command in
      :numref:`ox-connector-troubleshooting-ucs-database-integrity-listing`
      can speed up cache rebuilding
      because it retrieves up to 1,000 users from one context per request.

      .. code-block:: console
         :caption: Increase performance on rebuilding the cache
         :name: ox-connector-troubleshooting-ucs-database-integrity-listing

         $ /usr/sbin/univention-ox-connector-task-management \
            rewrite-ox-db-id \
            --build-cache-size=1000

.. warning::

   Memory consumption
      On the Nubus for UCS system with *OX Connector*,
      the rebuild process can use up to 1 GB of memory per 10,000 users
      in the *OX App Suite* database.

   System load
      Furthermore, the process may generate a lot of load on the *OX App Suite* system
      and the *OX Connector* app.

.. _ox-connector-troubleshooting-ucs-duplicate-display-name:

Duplicate display names
=======================

Since *OX Connector* version 2.2.0,
the UDM property *oxDisplayName* no longer has a unique constraint.

If *OX App Suite* isn't configured to allow duplicate display names,
:term:`SOAP API` calls fail with the exception as shown in
:numref:`ox-connector-troubleshooting-ucs-duplicate-display-name-exception-listing`.

.. code-block:: console
   :caption: Exception when OX App Suite doesn't allow duplicate display names
   :name: ox-connector-troubleshooting-ucs-duplicate-display-name-exception-listing

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

To allow duplicate display names,
add the properties in :numref:`ox-connector-troubleshooting-ucs-duplicate-display-name-listing`
to the :file:`user.properties` file in *OX App Suite*.

.. code-block:: console
   :caption: Configuration to allow duplicate display names in OX App Suite
   :name: ox-connector-troubleshooting-ucs-duplicate-display-name-listing

   com.openexchange.user.enforceUniqueDisplayName=false
   com.openexchange.folderstorage.database.preferDisplayName=false

.. note::

   The *OX App Suite* installation from the *App Center*
   configures these properties by default.

.. _ox-connector-troubleshooting-ucs-missing-group-members:

Missing group members
=====================

When the *OX Connector* synchronizes a group,
it needs the *internal ID* of every group member.
For more information, see :ref:`ox-connector-architecture-ucs-database`.
The connector looks up each member in its database of old entries.
If a user belongs to a group but isn't in that database,
the *OX Connector* skips the user without failing.
It logs a message, as shown in
:numref:`ox-connector-troubleshooting-ucs-missing-group-members-listing`.

Re-provision the missing user object manually.
For example, re-provision ``uid=oxuser1,cn=users,dc=example,dc=com``.
Follow :ref:`ox-connector-troubleshooting-handle-failed-tasks`
to synchronize the missing user.
When the *OX Connector* next processes the group object,
the :term:`OX Connector Provisioning Consumer` adds the user to the group again.

.. code-block:: console
   :caption: Log message for missing group members
   :name: ox-connector-troubleshooting-ucs-missing-group-members-listing

    2024-11-15 16:06:33 INFO    Group will be OX Group
    2024-11-15 16:06:33 INFO    Group wants user as member. But the user is unknown. Ignoring...

.. _ox-connector-troubleshooting-ucs-invalidate-values:

Invalid values for OX_USER_IDENTIFIER or OX_GROUP_IDENTIFIER
============================================================

A UDM user property, or a UDM group property for :envvar:`OX_GROUP_IDENTIFIER`,
is valid only when it contains a single value that isn't ``None``.
If the configured UDM property contains an empty value or a list of values,
the *OX Connector* enters an error state.
Set a valid value to resolve the error.

Setting an invalid value for the app settings :envvar:`OX_USER_IDENTIFIER`
or :envvar:`OX_GROUP_IDENTIFIER` leads to the errors in :numref:`ox-connector-troubleshooting-ucs-invalidate-values-listing`
or :numref:`ox-connector-troubleshooting-ucs-invalidate-values-groups-listing`.

.. code-block:: console
   :name: ox-connector-troubleshooting-ucs-invalidate-values-listing
   :caption: Error caused by an invalid value for app settings ``OX_USER_IDENTIFIER``

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
   :name: ox-connector-troubleshooting-ucs-invalidate-values-groups-listing
   :caption: Error caused by an invalid value for app settings ``OX_GROUP_IDENTIFIER``

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
