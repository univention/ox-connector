.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-troubleshooting-kubernetes:

*************************************************
Troubleshoot OX Connector on Nubus for Kubernetes
*************************************************

Use this page to troubleshoot problems with the *OX Connector* on Nubus for Kubernetes.
It explains how to inspect log files and provisioning tasks,
resolve blocked provisioning,
and re-provision data or rebuild the OX database ID cache.
It also covers known problems,
including missing group members,
and invalid identifier values.

.. _ox-connector-troubleshooting-kubernetes-log-files:

Log files
=========

The *OX Connector* has the following locations for relevant logs.
This section describes how to read the logs through :command:`kubectl`.
You can use other tools
that give you access to the same information in the respective pods.

The following listings need the same environment variables.
Add them to your shell with the commands in
:numref:`ox-connector-troubleshooting-kubernetes-logfiles-prepare-listing`.

.. code-block:: console
   :caption: Prepare environment variables
   :name: ox-connector-troubleshooting-kubernetes-logfiles-prepare-listing

   $ export NAMESPACE_FOR_CONSUMER="<NAMESPACE>"

.. _ox-connector-troubleshooting-kubernetes-log-files-consumer:

OX Connector Provisioning Consumer
   The ``main`` container in the ``ox-connector`` pod provides the log files
   for the *OX Connector*.
   To read the logs with :command:`kubectl`,
   use the following steps.
   You find all the commands in
   :numref:`ox-connector-troubleshooting-kubernetes-logfiles-ox-connector-listing`.

   #. Find out the name of the *OX Connector* pod and remember it.
      The example has the pod name ``ox-connector-0``.

   #. Open the log file of the ``main`` container of the *OX Connector* pod.

   .. code-block:: console
      :name: ox-connector-troubleshooting-kubernetes-logfiles-ox-connector-listing
      :caption: Read the log files of the *OX Connector*

      $ kubectl \
         --namespace "$NAMESPACE_FOR_CONSUMER" \
         get pods | grep "ox-connector"
      ox-connector-0    1/1   Running   0  19h

      $ export POD_NAME_FOR_OX_CONNECTOR="ox-connector-0"
      $ kubectl \
         --namespace "$NAMESPACE_FOR_CONSUMER" \
         logs \
         "$POD_NAME_FOR_OX_CONNECTOR" \
         -c main

.. _ox-connector-troubleshooting-kubernetes-logfiles-provisioning-service:

Provisioning Service
   The *Provisioning Service* is a component in Nubus for Kubernetes.
   To read the logs with :command:`kubectl`,
   use the following steps.
   You find all the commands in
   :numref:`ox-connector-troubleshooting-kubernetes-logfiles-provisioning-listing`.

   #. Find out the name of the *Provisioning Service* API pod and remember it.
      The example has the pod name ``ums-provisioning-api-968d7c9b7-26brx``.

   #. Open the log file of the ``main`` container of the *OX Connector* pod.

   .. code-block:: console
      :name: ox-connector-troubleshooting-kubernetes-logfiles-provisioning-listing
      :caption: Read the log files of the *Provisioning Service*

      $ kubectl \
         --namespace "$NAMESPACE_FOR_CONSUMER" \
         get pods | grep "provisioning-api"
      ums-provisioning-api-968d7c9b7-26brx   1/1   Running  0  20h

      $ export POD_NAME_FOR_PROVISIONING_API="ums-provisioning-api-968d7c9b7-26brx"
      $ kubectl \
         --namespace "$NAMESPACE_FOR_CONSUMER" \
         logs \
         "$POD_NAME_FOR_PROVISIONING_API" \
         -c main

   .. TODO: Move the whole section about provisioning service logs to the Customization Guide.
      Replace the content here with a cross-reference

.. seealso::

   `kubectl logs | Kubernetes <https://kubernetes.io/docs/reference/kubectl/generated/kubectl_logs/>`_
      for more information of available parameters for :command:`kubectl logs`.
      For example, to follow the logs stream, use the option ``follow``.

.. _ox-connector-troubleshooting-kubernetes-manage-provisioning-tasks:

Manage provisioning tasks
=========================

.. code-block:: console

   $ kubectl \
      --namespace "$NAMESPACE_FOR_CONSUMER" \
      get pods | grep "ox-connector"
   # Remember the pod name

   $ kubectl \
      --namespace "$NAMESPACE_FOR_CONSUMER" \
      execute \
      --stdin \
      --tty \
      "$POD_NAME_FOR_OX_CONNECTOR" \
      -- \
      /usr/local/bin/univention-ox-connector-task-management --help

.. _ox-connector-troubleshooting-kubernetes-database-integrity:

Ensure OX database ID integrity
===============================

The *OX Connector* caches the internal IDs that *OX App Suite* assigns to objects.
After you restore an *OX App Suite* database backup,
the cached IDs can become stale or inconsistent.
For more information about the cache,
see :ref:`ox-connector-architecture-kubernetes-database`.

To set the proper environment variables in the following listing,
use the commands in
:numref:`ox-connector-troubleshooting-kubernetes-logfiles-prepare-listing`.
To rebuild the cache,
run the command in :numref:`ox-connector-troubleshooting-kubernetes-rebuild-ox-db-id-listing`.

.. code-block:: console
   :caption: Rebuild cache for *internal ID*
   :name: ox-connector-troubleshooting-kubernetes-rebuild-ox-db-id-listing

   $ kubectl \
      --namespace "$NAMESPACE_FOR_CONSUMER" \
      get pods | grep "ox-connector"
   ox-connector-0    1/1   Running   0  19h

   $ export POD_NAME_FOR_OX_CONNECTOR="ox-connector-0"
   $ kubectl \
      --namespace "$NAMESPACE_FOR_CONSUMER" \
      execute \
      --stdin \
      --tty \
      "$POD_NAME_FOR_OX_CONNECTOR" \
      -- \
      univention-ox-connector-task-management \
      rewrite-ox-db-id

.. tip::

   Retrieve all users per context in one request
      Rebuilding the cache can take a long time
      and depends on the number of users in the *OX App Suite* database.

      The command in
      :numref:`ox-connector-troubleshooting-kubernetes-database-integrity-listing`
      can speed up cache rebuilding
      because it retrieves up to 1,000 users from one context per request.

      .. code-block:: console
         :caption: Increase performance on rebuilding the cache
         :name: ox-connector-troubleshooting-kubernetes-database-integrity-listing

         $ kubectl \
            --namespace "$NAMESPACE_FOR_CONSUMER" \
            execute \
            --stdin \
            --tty \
            "$POD_NAME_FOR_OX_CONNECTOR" \
            -- \
            univention-ox-connector-task-management \
            rewrite-ox-db-id \
            --build-cache-size=1000

.. warning::

   Memory consumption
      On Nubus for Kubernetes system with the *OX Connector*,
      the rebuild process can use up to 1 GB of memory per 10,000 users
      in the *OX App Suite* database.

   System load
      Furthermore, the process may generate a lot of load on the *OX App Suite* system
      and the *OX Connector* app.

.. _ox-connector-troubleshooting-kubernetes-missing-group-members:

Missing group members
=====================

When the *OX Connector* synchronizes a group,
it needs the *internal ID* of every group member.
For more information, see :ref:`ox-connector-architecture-kubernetes-database`.
The connector looks up each member in its database of old entries.
If a user belongs to a group but isn't in that database,
the *OX Connector* skips the user without failing.
It logs a message, as shown in
:numref:`ox-connector-troubleshooting-kubernetes-missing-group-members-listing`.

Re-provision the missing user object manually.
For example, re-provision ``uid=oxuser1,cn=users,dc=example,dc=com``.
Follow :ref:`ox-connector-troubleshooting-handle-failed-tasks`
to synchronize the missing user.
When the *OX Connector* next processes the group object,
the :term:`OX Connector Provisioning Consumer` adds the user to the group again.

.. code-block:: console
   :caption: Log message for missing group members
   :name: ox-connector-troubleshooting-kubernetes-missing-group-members-listing

    2024-11-15 16:06:33 INFO    Group will be OX Group
    2024-11-15 16:06:33 INFO    Group wants user as member. But the user is unknown. Ignoring...

.. _ox-connector-troubleshooting-kubernetes-invalid-values:

Invalid values for OX_USER_IDENTIFIER or OX_GROUP_IDENTIFIER
============================================================

A UDM user property, or a UDM group property for :envvar:`OX_GROUP_IDENTIFIER`,
is valid only when it contains a single value that isn't ``None``.
If the configured UDM property contains an empty value or a list of values,
the *OX Connector* enters an error state.
Set a valid value to resolve the error.

Setting an invalid value for the app settings :envvar:`OX_USER_IDENTIFIER`
or :envvar:`OX_GROUP_IDENTIFIER` leads to the errors in :numref:`ox-connector-troubleshooting-kubernetes-invalidate-values-listing`
or :numref:`ox-connector-troubleshooting-kubernetes-invalidate-values-groups-listing`.
You find the log information in the :ref:`OX Consumer logs <ox-connector-troubleshooting-kubernetes-log-files-consumer>`.

.. code-block:: console
   :name: ox-connector-troubleshooting-kubernetes-invalidate-values-listing
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
   :name: ox-connector-troubleshooting-kubernetes-invalidate-values-groups-listing
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
