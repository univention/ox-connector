.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-limitations:

***********
Limitations
***********

To use the *OX Connector* reliably,
read the following limitations.
Each section identifies the deployments it applies to.

.. _ox-connector-limitations-integration-app-suite:

OX Connector integration with the OX App Suite app
==================================================

.. dropdown:: Deployment — Nubus for UCS
   :color: info
   :icon: rocket

   This section applies to the Nubus for UCS deployment.

.. versionadded:: 2.1.2

Starting with version 2.1.2 of the OX Connector app,
you can use the *OX Connector* with the *OX App Suite* app
from Univention App Center.
The OX Connector handles provisioning,
while OX App Suite provides groupware.

For OX App Suite administrator credentials on separate UCS systems,
see :ref:`OX App Suite administrator <prerequisites-ox-app-suite-administrator>`.

.. _ox-connector-limitations-handle-faulty-items:

How OX Connector handles faulty items
=====================================

.. dropdown:: Deployment — All: Nubus for UCS and Nubus for Kubernetes
   :color: info
   :icon: rocket

   This section applies to both deployments.

The *OX Connector* stores provisioning tasks in its database.
It uses :envvar:`OX_CONNECTOR_STOP_ON_ERROR` to select how it handles
ordinary errors during provisioning.

.. tab-set::

   .. tab-item:: Nubus for UCS
      :sync: ucs

      In the Nubus for UCS deployment,
      the value defaults to ``true``.

   .. tab-item:: Nubus for Kubernetes
      :sync: kubernetes

      In the Nubus for Kubernetes deployment,
      the value defaults to ``false``.

.. _ox-connector-limitations-continue-at-conflict:

OX Connector continues after faulty items
-----------------------------------------

If :envvar:`OX_CONNECTOR_STOP_ON_ERROR` is ``false``
and the *OX Connector* can't process a faulty queue item,
it moves the task to the error list
and continues with the remaining queue items.
The connector logs the problem.

The *OX Connector* app provides a command-line interface (CLI)
to manage the error list.
For more information,
see :ref:`ox-connector-troubleshooting-ucs-log-files`
and :ref:`ox-connector-troubleshooting-ucs-manage-provisioning-tasks`.

Regardless of the setting,
the *OX Connector* handles HTTP, connection, timeout,
and OX context errors differently.
It retains the task in the task list,
increments its error count,
and retries the task after a delay.

.. tab-set::

   .. tab-item:: Nubus for UCS
      :sync: ucs

      When you set :envvar:`OX_CONNECTOR_STOP_ON_ERROR` to ``false``,
      you must monitor the list of errors manually
      and decide whether to delete or retry a task.
      Meanwhile, the *OX Connector* continues
      to process data it receives from the :term:`Provisioning Service`.

   .. tab-item:: Nubus for Kubernetes
      :sync: kubernetes

      In the Nubus for Kubernetes deployment,
      the OX Connector moves tasks that fail with an ordinary error to the error list by default.
      The OX Connector then continues with the following tasks.

      Network errors and errors while processing OX context objects remain in the task list.
      The consumer retries these tasks while outstanding tasks remain.

.. _ox-connector-limitations-stop-at-conflict:

OX Connector stops at faulty items
----------------------------------

If :envvar:`OX_CONNECTOR_STOP_ON_ERROR` is ``true``
and the *OX Connector* can't process a faulty queue item,
it retains the task in the task list.
The connector logs the problematic task
in the
:ref:`OX Connector Provisioning Consumer log file <ox-connector-troubleshooting-ucs-log-files-consumer>`.
For more information,
see :ref:`ox-connector-troubleshooting-ucs-log-files`.

The :term:`Provisioning Service` continues to add items to the queue.

.. tab-set::

   .. tab-item:: Nubus for UCS
      :sync: ucs

      After an administrator removes the faulty queue item,
      the *OX Connector Provisioning Consumer* resumes processing the queue.
      It also processes items that the :term:`Provisioning Service` adds.

      As administrator, you need to resolve that conflict manually when it happens,
      see :ref:`ox-connector-troubleshooting-ucs-resolve-blocked-provisioning`.
      After the conflict resolution, the connector
      continues to process the provisioning queue.

   .. tab-item:: Nubus for Kubernetes
      :sync: kubernetes

      In the Nubus for Kubernetes deployment,
      when you set :envvar:`OX_CONNECTOR_STOP_ON_ERROR` to ``true``,
      the OX Connector retains a task that fails with an ordinary error
      in the task list.

.. _ox-connector-limitations-access-profiles-rights:

No validation of access profile rights
======================================

.. dropdown:: Deployment — All: Nubus for UCS and Nubus for Kubernetes
   :color: info
   :icon: rocket

   This section applies to both deployments.

When an access profile changes,
the *OX Connector* doesn't check its rights against *OX App Suite*.
It writes the recognized rights to the module-access definition file
and applies them to users during provisioning.
If a user references an unknown access profile,
the connector leaves the user's existing module-access rights unchanged.

For more information, see `OX App Suite Permission Level
<https://oxpedia.org/wiki/index.php?title=AppSuite:Permission_Level>`_.
