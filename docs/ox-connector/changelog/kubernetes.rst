

.. _ox-connector-changelog-kubernetes:

************************************
Changelog OX Connector on Kubernetes
************************************

Find information about deploying :term:`OX Connector Provisioning Consumer`
for user provisioning at :ref:`ox-connector-install-on-kubernetes`.
This changelog documents all notable changes to *OX Consumer*.

This project follows `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_ format
and `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.


.. _consumer-changelog-v0.41.1:

v0.41.1
=======

Released: 2026-08-03

Fixed
-----

Relaxed database integrity checks when adding relations between objects.
If objects encounter synchronization errors and can't be saved,
the relation is still added.
The library layer enforces integrity checks instead of the DBMS.

If you deployed v0.41.0 and your database contains these foreign-key constraints,
remove them with the following command:
:command:`ALTER TABLE relations DROP CONSTRAINT relations_src_obj_id_fkey; ALTER TABLE relations DROP CONSTRAINT relations_dst_obj_id_fkey;`
Use equivalent commands for other database systems.

.. _consumer-changelog-v0.41.0:

v0.41.0
=======

Released: 2026-07-10

.. _consumer-changelog-v0.41.0-migration:

Migration
---------

When you :ref:`upgrade from a previous version to v0.41.0 <consumer-changelog-v0.41.0>`,
update your configuration so that the ``init-db`` container can complete the following procedure.
The connector performs a full synchronization during its first startup,
which can take some time.

#. Detect empty database tables.
#. Recreate the subscription to the *Provisioning Service*.
#. Trigger a full synchronization of all UDM objects to the *OX Connector*.
#. Create the cache in the database.

.. warning::

    Before you upgrade from a previous version to ``v0.41.0``,
    complete the migration steps.
    Otherwise, the *OX Connector* fails during startup.

Go through the following steps to update your configuration:

#. Create a PostgreSQL user and empty database for the *OX Connector*,
   see :ref:`ox-connector-configuration-kubernetes-database`.

#. Provide a PostgreSQL database connection URL through the
   :envvar:`openXchange.oxDbConnectionString` Helm value
   in your custom values file.
   See :ref:`ox-connector-install-on-kubernetes-prepare-ox-consumer`.

#. Retrieve the administrative credentials for the *Provisioning Service*
   in your Nubus for Kubernetes deployment.
   For information about retrieving these credentials,
   refer to :external+uv-nubus-customization:ref:`customization-api-provisioning-authentication`
   in :cite:t:`uv-nubus-customization`.

   .. tip::

      Use existing Kubernetes secrets
         Instead of specifying passwords directly in the values file,
         you can reference existing Kubernetes secrets.
         When you use existing secrets,
         Helm ignores inline ``password`` values.

#. Provide the provisioning admin credentials through the following Helm Chart values:

   * ``provisioningApi.resync.auth.username`` and  ``provisioningApi.resync.auth.password``
   * or ``provisioningApi.resync.auth.existingSecret``

#. Run :command:`helm upgrade` as described in :numref:`ox-consumer-helm-installation-listing` in :ref:`ox-connector-install-on-kubernetes-install-ox-consumer`.

Added
-----

This version adds support for *OX Shared Accounts*.
You can now add UDM objects for shared accounts and their permissions.
For more information, see :ref:`ox-connector-usage-shared-accounts`.

*OX Shared Accounts* require a database.
The *OX Connector* now requires a PostgreSQL database.
The database isn't included with the packaged *OX App Suite*
and *OX Connector* integration.
You must provide it separately.
For more information, read :ref:`ox-connector-configuration-kubernetes-database`.

.. warning::

   Before you upgrade from a previous version to ``v0.41.0``,
   complete the migration steps in :ref:`consumer-changelog-v0.41.0-migration`.
   Otherwise, this version of the *OX Connector* fails during startup.

Fixed
-----

The ox-connector pod now updates and restarts correctly
when the `openXchange.auth.password` value changes.

.. _consumer-changelog-v0.36.2:

v0.36.2
=======

Released: 2026-03-17

Removed
-------

The ``groups`` property has been removed from the *Functional Accounts* module.
Functional accounts never supported groups,
so the Univention Management Console didn't offer this option.
The connector no longer lets you set groups
through direct Univention Directory Manager access.

.. important::

    If groups were used as *Functional Account* members,
    add their members directly to the *Functional Account*.
    Attempting to add a group to a *Functional Account*
    will raise an error in UDM after this update.


.. _consumer-changelog-v0.36.1:

v0.36.1
=======

Released: 2026-03-12

Fixed
-----

The ``oxDeputyPermissionGivenTo`` property lets users grant deputy permissions
to other users.
The connector didn't update these references when a referenced user was moved in LDAP.
This issue is fixed.

.. _consumer-changelog-v0.36.0:

v0.36.0
=======

Released: 4. Mar 2026

Changed
-------

The *OX Consumer* now uses the UDM property ``univentionObjectIdentifier``
instead of ``entryUUID`` for the functional account login template.
A functional account provides a shared mailbox and calendar for multiple users
in *OX App Suite*.
If your configuration uses ``entryUUID``,
consult the *OX App Suite* and :program:`Dovecot` documentation
to update the sign-in configuration to use ``univentionObjectIdentifier``.
Without this update,
users can't sign in to newly provisioned functional accounts.

.. important::

   Before you upgrade your production environment to *OX Consumer* ``0.36.0``,
   test the update in a test environment
   and verify that users can sign in to existing
   and newly created functional accounts.

After you upgrade to *OX Consumer* ``0.36.0``, validate the following:

* Create a new functional account after the upgrade and verify that it was created successfully.
* Verify that members can access the new functional account.
* If validation fails, don't proceed with upgrading additional environments.
  Contact your support provider before continuing.
