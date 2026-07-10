.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _migration-v0.41.0:

********************
Migration to v0.41.0
********************

When you :ref:`upgrade from a previous version to v0.41.0 <consumer-changelog-v0.41.0>`,
you must update your configuration
so that the *OX Connector* can run through the following procedure in the ``init-db`` container.
The first startup can take some time, because of the full synchronization.

#. Detect empty database tables.
#. Recreate the subscription to the *Provisioning Service*.
#. Trigger a full synchronization of all UDM objects to the *OX Connector*.
#. Create the cache in the database.

.. warning::

    Before you upgrade from a previous version to ``v0.41.0``
    go through the migration steps.
    Otherwise, the *OX Connector* fails during start.

Go through the following steps to update your configuration:

#. Create a PostgreSQL user and empty database for the *OX Connector*,
   see :ref:`configure-database`.

#. Provide a PostgreSQL database connection URL through the
   ``openXchange.oxDbConnectionString`` Helm value
   in your custom values file.
   See :ref:`user-provisioning-configuration`.

#. Retrieve the administrative credentials for the *Provisioning Service* of your Nubus for Kubernetes deployment.
   For information about how to retrieve these credentials,
   refer to :external+uv-nubus-customization:ref:`customization-api-provisioning-authentication`
   in :cite:t:`uv-nubus-customization`.

   .. tip::

      Use existing Kubernetes secrets
         Instead of specifying passwords directly in the values file,
         you can reference existing Kubernetes secrets.
         When you use existing secrets,
         Helm ignores the inline ``password`` values.

#. Provide the provisioning admin credentials through the following Helm Chart values:

   * ``provisioningApi.resync.auth.username`` and  ``provisioningApi.resync.auth.password``
   * or ``provisioningApi.resync.auth.existingSecret``

#. Run :command:`helm upgrade` as described in :numref:`user-provisioning-helm-listing` in :ref:`user-provisioning-installation`.
