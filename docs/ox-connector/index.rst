.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _doc-entry:

************
Introduction
************

The *OX Connector* provisions selected directory objects from Nubus
to a remote *OX App Suite* installation through the OX SOAP API.
These directory objects include user accounts,
user groups,
and resources.

Nubus is the leading system for identity data.
When you create, change, or remove selected objects in Nubus,
the *OX Connector* synchronizes these changes to *OX App Suite*.

The connector doesn't install or operate *OX App Suite*.

.. _introduction-deployment-paths:

Deployment paths
================

The *OX Connector* supports the following deployment paths:

App Center app
   Use this deployment path
   if you operate Nubus on Univention Corporate Server (UCS).

   The *OX Connector app* runs as an App Center app on UCS.
   It provisions selected UCS directory objects to *OX App Suite*.

Nubus for Kubernetes
   Use this deployment path
   if you operate Nubus for Kubernetes.

   The *OX Consumer* runs in the Kubernetes cluster.
   It provisions selected Nubus directory objects to *OX App Suite*.
   The Kubernetes deployment uses the packaged integration for *OX App Suite*
   to extend Nubus with the required directory schema
   and management interface customizations.

Both deployment paths use the same provisioning logic.
The chapters in this manual state which steps apply to which deployment path.

.. _introduction-audience-and-prerequisites:

Audience and prerequisites
==========================

This manual addresses technical administrators and operators
who want to connect Nubus with *OX App Suite*.
You need administrative access to the Nubus deployment
that you want to connect.

For the App Center deployment,
you need to know how to use a shell
on a Debian GNU/Linux derivative distribution such as UCS.
You also need to know how to manage apps
through the Univention App Center.

For the Kubernetes deployment,
you need to know Kubernetes concepts
and how to deploy and manage applications with Helm.

.. _introduction-document-scope:

Document scope
==============

This manual covers the following topics:

* Install the *OX Connector* for the supported deployment paths.
* Configure provisioning from Nubus to *OX App Suite*.
* Understand how the connector works.
* Read about known limitations.
* Find log files and troubleshoot common problems.

This manual doesn't cover the following topics:

* Installation,
  setup,
  and operation of:

  * Kubernetes
  * *OX App Suite*
  * *Nubus for UCS*

* Installation and operation of *Nubus for Kubernetes*.

.. seealso::

   Nubus for UCS
      For information about installation,
      setup,
      and operation of UCS,
      see :external+uv-ucs-operation:ref:`Nubus for UCS Operation Manual <lifecycle>`
      in :cite:t:`uv-ucs-operation`.

   Nubus for Kubernetes
      For information about installation,
      setup,
      and operation of Nubus for Kubernetes,
      see :external+uv-nubus-kubernetes-operation:ref:`Deploy Nubus for Kubernetes <nubus-deployment-all-deps>`
      in :cite:t:`uv-nubus-kubernetes-operation`.

   OX App Suite
      for information, setup and operation,
      see :cite:t:`ox-app-suite-admin-guide`.

.. _introduction-support-status:

Support status
==============

The OX Connector supports Nubus for Kubernetes.
Support for the connector doesn't include installation,
configuration,
or operation of *OX App Suite*.

For further documentation about Nubus for Kubernetes,
see :external+uv-navigation:ref:`page-nubus`.

.. _introduction-feedback:

Feedback
========

Your feedback about this documentation is welcome and highly appreciated.
If you have comments,
suggestions,
or criticism,
`submit your feedback <https://www.univention.com/feedback/?ox-connector=generic>`_
to improve the document.
