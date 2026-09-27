.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-troubleshooting-collect-support-information:

Collect information for a support ticket
========================================

Before you open a support ticket,
collect the following information so that Univention Support can investigate
the issue:

* Relevant messages and tracebacks:

  .. tab-set::

     .. tab-item:: Nubus for UCS
        :sync: ucs

        Messages and tracebacks from
        :ref:`ox-connector-troubleshooting-ucs-log-files`,
        especially from the
        :ref:`OX Connector Provisioning Consumer logs <ox-connector-troubleshooting-ucs-log-files-consumer>`.

     .. tab-item:: Nubus for Kubernetes
        :sync: kubernetes

        Messages and tracebacks from
        :ref:`ox-connector-troubleshooting-kubernetes-log-files`,
        especially from the
        :ref:`OX Connector Provisioning Consumer logs <ox-connector-troubleshooting-kubernetes-log-files-consumer>`.

* Steps that reproduce the unexpected behavior.

* The expected behavior.

* Provisioning data that causes the error.
