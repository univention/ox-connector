.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-architecture-ucs:

*****************
For Nubus for UCS
*****************

The :program:`OX Connector` app architecture includes the following elements:

* The Nubus for UCS operating environment includes the App Center and Docker Engine.
  A container runs OX Connector.

* The container image contains the OX Connector software.

* The OpenLDAP directory in Nubus for UCS is the identity management source for OX App Suite.

Before you continue reading, ensure you know :ref:`ox-connector-architecture-common`.

.. _ox-connector-architecture-ucs-overview:

Overview
========

The :program:`OX Connector` uses the software in its container image
to provision identity data from Nubus for UCS to OX App Suite.
The OX Connector connects to the OX App Suite SOAP API.
It creates, updates, or deletes OX App Suite objects,
including users, groups, contexts, and resources,
in response to relevant LDAP directory changes.
:numref:`ox-connector-architecture-kubernetes-components-figure`
shows the following components, their boundaries, and dependencies:

#. :term:`Identity Store and Directory Service`
#. :term:`Directory Manager`
#. :term:`Provisioning Service`
#. :term:`Provisioning API`
#. :term:`OX Connector Provisioning Consumer`
#. :term:`OX App Suite`

.. _ox-connector-architecture-ucs-overview-figure:

.. figure:: /images/OX_Connector_Architecture_Provisioning.*
   :target: ../_images/OX_Connector_Architecture_Provisioning.svg
   :alt: OX Connector app architecture

   OX Connector app architecture

.. dropdown:: Detailed OX Connector app processing, click to open.
   :color: info
   :icon: zoom-in

   :numref:`ox-connector-architecture-ucs-detail-figure`
   includes the *Provisioning Service* with all its parts
   and what happens there before the data moves to the *OX Connector*.
   Follow the *Flow* relations from the top right corner to the OX App Suite.

   .. _ox-connector-architecture-ucs-detail-figure:

   .. figure:: /images/OX_Connector_Architecture_Provisioning_Details_Behavior.*
      :target: ../_images/OX_Connector_Architecture_Provisioning_Details_Behavior.svg
      :alt: OX Connector app architecture

      OX Connector app architecture in more detail

      Click the diagram to zoom in.

.. _ox-connector-architecture-ucs-how-it-works:

How the connector works
=======================

.. index::
   single: udm modules
   single: provisioning
   see:  synchronization; provisioning
   see: UDM; udm modules
   single: udm modules; users/user
   single: udm modules; groups/group
   single: udm modules; oxmail/oxcontext
   single: udm modules; oxresources/oxresources

Univention Directory Manager (UDM) is an object layer
on top of the LDAP directory in UCS.
The OX Connector reacts to changes in the following UDM modules:

* Source modules:

  * ``users/user``
  * ``groups/group``

* Connector-specific modules:

  * ``oxmail/oxcontext``
  * ``oxresources/oxresources``
  * ``oxmail/accessprofile``
  * ``oxmail/functional_account``
  * ``oxmail/shared_account``
  * ``oxmail/shared_account_permission``

The connector processes changes to these modules
and sends data to the SOAP API in OX App Suite when required.

.. _ox-connector-architecture-ucs-profiles:

Access profiles
---------------

.. index::
   single: udm modules; oxmail/accessprofile

When the ``oxmail/accessprofile`` UDM module changes,
the connector rewrites the local file
:file:`/var/lib/univention-appcenter/apps/ox-connector/data/ModuleAccessDefinitions.properties`.
It doesn't send access-profile data directly to the SOAP API in OX App Suite.
When the connector provisions a user,
it applies the access-profile definitions from this file through the SOAP API.

Administrators can find *access profiles*
in the *Management UI*,
in the *LDAP directory* module,
at :menuselection:`open-xchange --> accessprofile`.

.. _ox-connector-architecture-ucs-provisioning:

Provisioning
------------

For a visualization of the provisioning process,
see :numref:`ox-connector-architecture-ucs-provisioning-figure`.
The following steps describe how the OX Connector provisions changed UDM objects
to OX App Suite:

#. The :term:`Provisioning Service` detects a change
   in the *Identity Store and Directory Service*
   and sends a message with the UDM object
   through the :term:`Provisioning API`.

#. In the container,
   the :term:`OX Connector Provisioning Consumer` receives the message
   and stores it as a task in its SQLite database.

#. The :term:`OX Connector Provisioning Consumer` processes tasks in a fixed module order
   and sends the data for each task
   to the :term:`SOAP API` in OX App Suite.

#. After the :term:`SOAP API` successfully processes the data,
   the :term:`OX Connector Provisioning Consumer` stores the object state
   in its database of old entries.
   For more information, see :ref:`ox-connector-architecture-ucs-database`.

#. After a connection error, the connector stops processing tasks
   and retries later.
   For other errors, it moves the task to the morgue.

.. index::
   single: provisioning; procedure

.. _ox-connector-architecture-ucs-provisioning-figure:

.. figure:: /images/OX_Connector_Architecture_Provisioning_Procedure.*
   :target: ../_images/OX_Connector_Architecture_Provisioning_Procedure.svg
   :alt: provisioning procedure

   Provisioning procedure

.. _ox-connector-architecture-ucs-attributes:

Provisioned attributes
======================

.. index::
   pair: provisioning; attributes

For information about configuring the user attribute mapping,
see :ref:`ox-connector-configuration-ucs-user-attribute-mapping`.

For the related group, context, and resource provisioning implementations,
see the following files:

* :file:`univention-ox-provisioning/univention/ox/provisioning/groups.py`
* :file:`univention-ox-provisioning/univention/ox/provisioning/contexts.py`
* :file:`univention-ox-provisioning/univention/ox/provisioning/resources.py`

.. _ox-connector-architecture-ucs-database:

Database of stored object state
===============================

.. index::
   single: cache
   single: OX App Suite; internal ID
   pair: JSON; cache

.. versionadded:: 3.0.0

The OX Connector stores its database file at
:file:`/var/lib/univention-appcenter/apps/ox-connector/data/ox-connector.db`.
The database contains a table named ``old``.
Don't modify the database file directly.

:numref:`ox-connector-architecture-ucs-inspect-pending-tasks`
shows how to inspect pending tasks on the Nubus for UCS system.
The command displays a summary of the pending tasks.

.. code-block:: console
   :name: ox-connector-architecture-ucs-inspect-pending-tasks
   :caption: Inspect pending OX Connector tasks.

   $ univention-app shell ox-connector \
     python3 -m univention.ox.provisioning.db summarize-tasks

.. TODO: Refers to a section in troubleshooting. Update with issue #175

   For more information,
   see :ref:`app-cli`.
