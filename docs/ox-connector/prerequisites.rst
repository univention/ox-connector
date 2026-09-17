.. SPDX-FileCopyrightText: 2021 - 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-prerequisites:

*************
Prerequisites
*************

Before you install the *OX Connector*,
make sure that your Nubus deployment
and *OX App Suite* meet the prerequisites.

.. _prerequisites-ox-app-suite:

OX App Suite server
===================

The *OX App Suite* server must meet the following prerequisites:

#. **Installed OX App Suite instance**

   You need an existing *OX App Suite* instance.
   The *OX Connector* doesn't install, configure, or operate *OX App Suite*.

   For information about installing *OX App Suite*,
   see :cite:t:`ox-app-suite-admin-guide`.

#. **SOAP API access**

   The *OX App Suite* instance must allow SOAP requests
   so that the *OX Connector* can access the ``/webservices`` endpoint
   in *OX App Suite*.

#. **OX App Suite administrator**

   Set up an administrator user in *OX App Suite*
   who can create OX contexts.
   The *OX Connector* uses this user to manage OX contexts.
   In the connector configuration,
   enter the username and password for this user.
   For information about managing OX contexts manually,
   see :cite:t:`ox-app-suite-admin-guide`.

   For the *OX Connector* app in Univention App Center,
   use the settings
   :envvar:`OX_MASTER_ADMIN` and :envvar:`OX_MASTER_PASSWORD`.

   For Nubus for Kubernetes,
   configure the OX administrator credentials in the Helm values
   for the *OX Consumer*.

   .. TODO: Activate the following content as soon as it's available in this document.
      For manually managing OX contexts without the OX Connector,
      see :ref:`usage-contexts`.

#. **Duplicate display names**

   Allow duplicate display names in *OX App Suite*.
   Add the lines in :numref:`prerequisites-ox-app-suite-display-names-listing`
   to the :file:`user.properties` file.

   .. code-block:: console
      :caption: Allow duplicate display names in *OX App Suite*
      :name: prerequisites-ox-app-suite-display-names-listing

      com.openexchange.user.enforceUniqueDisplayName=false
      com.openexchange.folderstorage.database.preferDisplayName=false

#. **Group names**

   *OX App Suite* must allow all group names
   that administrators can use in Nubus.
   Add the line in :numref:`prerequisites-ox-app-suite-group-names-listing`
   to the :file:`Group.properties` file.

   .. code-block:: console
      :caption: Allow all group names in *OX App Suite*
      :name: prerequisites-ox-app-suite-group-names-listing

      CHECK_GROUP_UID_FOR_NOT_ALLOWED_CHARS=false

.. _prerequisites-app-center:

OX Connector app in Univention App Center
=========================================

The *OX Connector* app from Univention App Center
needs the *referential integrity* overlay
in the central LDAP directory.

The overlay keeps the Univention Directory Manager (UDM) objects
that the *OX Connector* uses consistent.
It also ensures that these UDM objects reference user objects correctly.

For details,
see :cite:t:`openldap-referential-integrity-overlay`.

.. tab-set::

   .. tab-item:: OX Connector on UCS Primary Directory Node

      If you install the *OX Connector* app from Univention App Center
      on :external+uv-ucs-operation:term:`UCS Primary Directory Node`,
      the app activates the *referential integrity* overlay.
      You don't need to take further action.

   .. tab-item:: OX Connector on other system roles

      If you install the *OX Connector* app from Univention App Center
      on a Nubus for UCS system role other than the
      :external+uv-ucs-operation:term:`UCS Primary Directory Node`,
      run the commands in :numref:`prerequisite-activate-referential-integrity-overlay`
      on the :external+uv-ucs-operation:term:`UCS Primary Directory Node`
      with root privileges.

      .. code-block:: console
         :caption: Activate the OpenLDAP *referential integrity* overlay on the UCS Primary Directory Node
         :name: prerequisite-activate-referential-integrity-overlay

         $ ucr set ldap/refint=true
         $ service slapd restart

.. _prerequisites-kubernetes:

Nubus for Kubernetes
====================

On Nubus for Kubernetes,
the *OX Connector* runs as the *OX Consumer*.

Before you install the *OX Consumer*,
install the packaged integration for *OX App Suite*.
Follow :external+uv-nubus-customization:ref:`nubus-packaged-integrations-load`.
The packaged integration installs the required LDAP schema
in the *Directory Service*.
It also adds the required customizations to the *Management UI* in Nubus
for user accounts, user groups, and resources.

Before you install the packaged integration,
ask the team that provides it
for the container image details.

You need the registry name and the repository name.
This documentation uses the following example values:

:Registry: ``artifacts.software-univention.de``
:Repository: ``nubus/images/ox-extension``

For details,
see :cite:t:`uv-nubus-customization`.
