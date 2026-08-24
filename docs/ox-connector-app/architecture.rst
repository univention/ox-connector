.. SPDX-FileCopyrightText: 2021 - 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _app-architecture:

************
Architecture
************

The :program:`OX Connector` app architecture consists of the following elements:

* The operating environment |UCS| with the App Center and the Docker engine
  running OX Connector.

* The OX Connector software inside a Docker image.

* The OpenLDAP LDAP directory in UCS as identity management source for OX App
  Suite.

.. _architecture-overview:

Overview
========

The :program:`OX Connector` app consists of a Docker image with all the software
needed to provision user identities from |UCS| identity management to OX App
Suite. The OX connector connects to the OX App Suite SOAP API and creates, updates,
or deletes object entries in OX App Suite depending on what changed in the UCS
LDAP directory with relevance to OX App Suite.

.. figure:: /images/architecture.*
   :alt: OX Connector app architecture

   OX Connector app architecture

   The diagram shows the *LDAP directory*, *Provisioning Service*,
   *Provisioning API*, *OX Connector* with the *Provisioning Consumer*,
   *OX App Suite*, and its *SOAP API*.


.. glossary::

   LDAP
      The OpenLDAP software provides the *LDAP* directory in |UCS|. The LDAP
      directory stores all identity and infrastructure data of the UCS domain. For
      more information, see :ref:`domain-ldap` in :cite:t:`ucs-manual`.

   Provisioning Service
      The *Provisioning Service* is a Nubus app
      that you install in the Nubus for UCS domain.
      It's an event and messaging service
      that watches the LDAP directory for changes.
      When data changes on the :external+uv-ucs-operation:term:`Primary Directory Node`,
      the *Provisioning Service* notifies subscribed services about the change.

      In contrast to the Univention Directory Listener,
      it provides the UDM representation of the changed objects
      instead of the LDAP representation.
      The :program:`OX Connector` app subscribes to the
      *Provisioning Service* through the :term:`Provisioning API`
      for the UDM modules it provisions.

      On a fresh install of the :program:`OX Connector`,
      the *Provisioning Service* sends all existing UDM objects
      of the subscribed modules to the OX Connector (a *prefill*).

   Provisioning API
      The *Provisioning API* runs on the Primary Directory Node
      and :external+uv-ucs-operation:term:`Backup Directory Nodes <Backup Directory Node>`.
      It's the API that applications use
      to subscribe to events of the :term:`Provisioning Service`.
      The :term:`Provisioning Consumer` of the :program:`OX Connector` app
      subscribes through the *Provisioning API*
      for the UDM modules the connector provisions.
      You can access the *Provisioning API* locally through :file:`http://localhost:7777`
      or remotely through :file:`https://<primary FQDN>/univention/provisioning/`.

   OX Connector
      *OX Connector* connects the |UCS| identity management with OX App Suite.
      The connector receives data about changes in the LDAP directory.
      A :term:`Provisioning Consumer` handles the data,
      processes it, and sends it to the :term:`SOAP API` in OX App Suite.

   Provisioning Consumer
      The *Provisioning Consumer* runs inside the Docker container of the
      OX Connector. It subscribes to the :term:`Provisioning API` for the
      UDM modules the connector provisions. For every message it receives,
      it stores a task in its SQLite database and processes the tasks in a
      fixed module order, sending the data to the :term:`SOAP API`.

   OX App Suite
      *OX App Suite* is the groupware and collaboration software from Open-Xchange.

   SOAP API
      OX App Suite uses `SOAP <https://en.wikipedia.org/wiki/SOAP>`_ as network
      protocol to receive data and run remote procedure calls. The connector uses
      the SOAP API to create, update, or delete object entries in OX App Suite.

.. _app-how-it-works:

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

The OX Connector reacts on changes in the LDAP directory in |UCS| and relies on
modules in the Univention Directory Manager (UDM) modules. |UDM| is a layer on top
of the LDAP directory in UCS.

UCS provides the following UDM modules:

* ``users/user``
* ``groups/group``

The OX Connector provides the following UDM modules:

* ``oxmail/oxcontext``
* ``oxresources/oxresources``
* ``oxmail/accessprofile``

The OX Connector reacts on changes to the listed UDM modules and sends data to the
SOAP API in OX App Suite.

.. _connector-access-profiles:

Access profiles
---------------

.. index::
   single: udm modules; oxmail/accessprofile

Upon changes in the UDM module ``oxmail/accessprofile``, the connector rewrites
the local file
:file:`/var/lib/univention-appcenter/apps/ox-connector/data/ModuleAccessDefinitions.properties`
and doesn't send data to the SOAP API in OX App Suite. The module handles the
user rights and roles in OX App Suite. Administrators find the *access profiles*
in UMC in the module LDAP directory at :menuselection:`open-xchange -->
accessprofile`.

.. _connector-provisioning:

Provisioning
------------

In detail, the provisioning has the following steps, see
:numref:`sync-procedure`:

#. The :term:`Provisioning Service` detects the change in the LDAP directory
   and sends a message with the UDM object
   through the :term:`Provisioning API`.

#. In the container,
   the :term:`Provisioning Consumer` receives the message
   and stores it as a task in its SQLite database.

#. The :term:`Provisioning Consumer` processes the tasks in a fixed module
   order and sends the data of each task
   to the :term:`SOAP API` in OX App Suite.

#. After the :term:`SOAP API` receives and processes the data successfully,
   the :term:`Provisioning Consumer` stores the state of the object
   in its database of old entries, see :ref:`db-old-entries`.

.. index::
   single: provisioning; procedure

.. _sync-procedure:

.. figure:: /images/sync-procedure.*
   :alt: provisioning procedure

   Provisioning procedure

.. _synced-attributes:

Provisioned attributes
======================

.. index::
   pair: provisioning; attributes

The :program:`OX Connector` provisions a lot of attributes to OX App Suite. A
detailed description is beyond the scope of this document.

The OX Connector comes with the source code. The user attributes for
provisioning locate in the function :py:func:`update_user()` in
:file:`univention-ox-provisioning/univention/ox/provisioning/users.py` inside
the Docker container. To view the attributes, for example with :program:`vim`,
run the following command on the UCS system with OX Connector installed. Replace
:samp:`$version` with the proper Python version used in the Connector:

.. code-block:: console
   :caption: Example for how to view the definition of provisioned attributes.

   $ univention-app shell ox-connector \
     cat /usr/lib/python"$version"/site-packages/univention/ox/provisioning/users.py \
     | vim -

Likewise, the attributes for groups, context, and resources locate in the
respective source files in the ``update_*()`` function.

.. _db-old-entries:

Database of old entries
=======================

.. index::
   single: cache
   single: OX App Suite; internal ID
   pair: JSON; cache

.. versionadded:: 3.0.0

:term:`OX App Suite` creates an *internal ID* for every user object it creates
or updates. The OX Connector saves this *internal ID* in its own database, when it
processed the objects without errors. The connector doesn't store that ID in the
UCS LDAP directory, but maintains a database in which it stores the data old
object's it processed for later reference (i.e., for retrieving the *internal
ID*)

The OX Connector stores its database file at
:file:`/var/lib/univention-appcenter/apps/ox-connector/data/ox-connector.db`.
The database contains a table named ``old``.
Use the command-line interface that the app provides to modify this database.
For more information,
see :ref:`app-cli`.

When the :term:`Provisioning Consumer` updates groups in OX App Suite, the request
to the :term:`SOAP API` must include the internal ID of all group members. The
connector would need to ask the database of OX App Suite for the *internal ID*
of each group member, involving network requests and database queries. To speed
up the processing, the OX Connector uses the *internal ID* from the database.
