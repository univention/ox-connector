.. SPDX-FileCopyrightText: 2021 - 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-usage-shared-accounts:

Shared accounts
===============

.. versionadded:: 3.2.0

OX App Suite lets users and groups access shared accounts.
Users with a shared account can read its email and calendar entries.
As an administrator, you can configure fine-grained permissions for users and groups.
The OX Connector app provides UDM modules
to manage shared accounts and the permissions of users and groups.

.. important::

   The *Shared accounts* feature requires *OX App Suite* version 8.49 or later.
   A runtime check deactivates the feature
   when *OX App Suite* doesn't support shared accounts.

.. seealso::

   `Shared accounts <https://documentation.open-xchange.com/8/middleware/permissions_and_capabilities/shared_accounts.html>`_

.. _ox-connector-usage-shared-accounts-udm-module:

UDM module for shared accounts
------------------------------

As an administrator, you can use the management module ``oxmail/shared_account``
to add, update, or delete objects for shared accounts
and manage their permissions.
You can find the UDM module in the *Management UI* under *LDAP directory*
at the directory location ``open-xchange/shared_account``.

Every ``oxmail/shared_account`` object contains a list of users and groups with their respective permissions.
Each user and group entry in the list links to an ``oxmail/shared_account_permissions`` object.

.. seealso::

   :external+uv-nubus-manual:ref:`nubus-domain-ldap`
      for information about the *LDAP directory* management module.

.. _ox-connector-usage-shared-accounts-udm-permissions:

UDM module for permissions
--------------------------

OX App Suite uses permission objects to control user and group access to shared accounts.
OX Connector provides ready-to-use *permissions* for OX App Suite shared accounts,
including *Full Calendar Access*, *Full Mail Access*, *Full Mail and Calendar Access*, and *Read-Only Mail Access*.
You can also create permissions to meet your requirements.

As an administrator, you can use the management module ``oxmail/shared_account_permissions``
to create, update, or delete permissions for shared accounts.
You can find the UDM module in the *Management UI* under *LDAP directory*
at the directory location ``open-xchange/shared_account_permissions``.

When you create an ``oxmail/shared_account`` object,
you can grant permissions to users and groups in the *Management UI*.

.. _ox-connector-usage-shared-accounts-migration:

Migration from functional accounts to shared accounts
-----------------------------------------------------

.. versionadded:: 3.2.1

The shared accounts feature in OX App Suite
deprecates the old functional accounts.
OX Connector provides a script
that lets you migrate from functional accounts
to shared accounts.

Before you run the script,
:program:`Dovecot` must use the email address
as the unique identifier for the mail accounts.

.. danger::

   If your :program:`Dovecot` installation uses a unique identifier
   other than the email address,
   **don't run** the migration script.
   In that case, the script deletes your functional accounts
   and creates shared accounts without their content.

Test the migration script
and carefully review the results
before you use it in production.
The ``dry-run`` option runs the migration script without actually writing changes to OX App Suite,
and prints statements from the steps during the migration.

For information about the migration script parameters,
use the ``--help`` option.
It provides options about addressing multiple functional accounts with one run,
or providing credentials through environment variables.

.. TODO: Reactivate after troubleshooting is added with #175

   For troubleshooting, see :ref:`app-troubleshooting-migration`.

Depending on your deployment of the OX Connector,
choose one of the following options to run the migration.

.. tab-set::

   .. tab-item:: App in Univention App Center

      Run the migration script on Nubus for UCS on the system
      that has the OX Connector installed.
      Use the commands in
      :numref:`usage-shared-accounts-migration-prepare-ucs-listing`
      and :numref:`usage-shared-accounts-migration-ucs-listing`.
      In the listing you need to provide the values for the following inputs:

      ``UDM_USERNAME``
         The username for the UDM user.
         The user account must be a member of the :external+uv-nubus-customization:ref:`customization-api-udm-rest-auth-group`
         in the *UDM HTTP REST API*.

      ``UDM_PASSWORD``
         The password for the ``UDM_USERNAME``.

      ``REST_API_HOSTNAME``
         The FQDN of the UDM HTTP REST API in your domain.

      ``OPTIONAL_DESTINATION``
         The container for the shared account that the migration script creates.

      ``DESTINATION_OX_CONTEXT``
         The OX Context where the shared account will be created.

      .. code-block:: console
         :caption: Prepare migration to shared accounts
         :name: usage-shared-accounts-migration-prepare-ucs-listing

         $ export UDM_USERNAME="<your-udm-user>"
         $ export UDM_PASSWORD="<your-udm-password>"
         $ export REST_API_HOSTNAME="<your-udm-rest>"
         $ export OPTIONAL_DESTINATION="<optional-custom-destination-for-single-migration>"
         $ export DESTINATION_OX_CONTEXT=<your-ox-context-id>

      .. code-block:: console
         :caption: Run the migration from functional accounts to shared accounts
         :name: usage-shared-accounts-migration-ucs-listing

         $ univention-app shell \
            ox-connector \
            /usr/local/share/ox-connector/resources/migrate_fupo_to_shared_account.py \
            "cn=example_fupo,cn=functional_accounts,cn=open-xchange,$(ucr get ldap/base)" \
            "Full Mail Access" \
            "$OPTIONAL_DESTINATION" \
            "$UDM_USERNAME" \
            "$UDM_PASSWORD" \
            "https://$REST_API_HOSTNAME/univention/udm" \
            --ox-context $DESTINATION_OX_CONTEXT

   .. tab-item:: Consumer in Nubus for Kubernetes

      To run the migration script in your Nubus for Kubernetes environment,
      use the following steps.

      #. To configure the namespaces for your Nubus for Kubernetes environment
         and the OX Consumer deployment,
         set the environment variables as shown in :numref:`usage-shared-accounts-migration-env-listing`.

         ``NAMESPACE_N4K``
            The Kubernetes namespace for your Nubus for Kubernetes deployment.

         ``RELEASE_N4K``
            The release name for your Nubus for Kubernetes deployment.
            To list the release names in your namespace,
            run the command in :numref:`usage-shared-accounts-migration-release-name-listing`.

         ``NAMESPACE_CONNECTOR``
            The Kubernetes namespace of your OX Connector deployment.
            Typically, it's the same namespace as for Nubus for Kubernetes.

         .. code-block:: console
            :caption: Set environment variables for Nubus for Kubernetes and the OX Connector.
            :name: usage-shared-accounts-migration-env-listing

            $ export NAMESPACE_CONNECTOR="<your-namespace-for-the-connector>"
            $ export NAMESPACE_N4K="<your-namespace-for-nubus-for-kubernetes>"
            $ export RELEASE_N4K="<Release-name-for-nubus-for-kubernetes>"

         .. code-block:: console
            :caption: Show the release names in the namespace of Nubus for Kubernetes
            :name: usage-shared-accounts-migration-release-name-listing

            $ helm --namespace "$NAMESPACE_N4K" list -q

      #. Retrieve the LDAP base DN from your Nubus for Kubernetes environment.

         You need the LDAP base DN of your Nubus for Kubernetes deployment.
         You provided the LDAP base DN during the :external+uv-nubus-kubernetes-operation:ref:`deployment of Nubus for Kubernetes <nubus-deployment-all-deps>`
         in your :file:`custom_values.yaml`.
         To retrieve the LDAP base DN,
         run the command in :numref:`usage-shared-accounts-migration-n4k-retrieve-values-listing`.

         ``LDAP_BASE``
            The LDAP base DN of your directory service.

         .. code-block:: console
            :caption: Retrieve parameters from Nubus for Kubernetes environment
            :name: usage-shared-accounts-migration-n4k-retrieve-values-listing

            $ export LDAP_BASE="$(kubectl \
               --namespace "$NAMESPACE_N4K" \
               get configmap \
               "$RELEASE_N4K-ldap-server" \
               -o "jsonpath={.data.LDAP_BASE_DN}")"

      #. Configure the remaining parameters for the migration script.

         ``UDM_USERNAME``
            The username for the UDM user.
            The user account must be a member of the :external+uv-nubus-customization:ref:`customization-api-udm-rest-auth-group`
            in the *UDM HTTP REST API*.

         ``UDM_PASSWORD``
            The password for the ``UDM_USERNAME``.

         ``FUNCTIONAL_ACCOUNT``
            The LDAP distinguished name (DN) of the functional account that you want to migrate.

         ``DESTINATION_OX_CONTEXT``
            The OX Context where the shared account will be created.

         .. code-block:: console
            :caption: Define the remaining parameters for the migration
            :name: usage-shared-accounts-migration-prepare-n4k-listing

            $ export UDM_USERNAME="<your-udm-user>"
            $ export UDM_PASSWORD="<your-udm-password>"
            $ export FUNCTIONAL_ACCOUNT="cn=example_fupo,cn=functional_accounts,cn=open-xchange,$LDAP_BASE"
            $ export DESTINATION_OX_CONTEXT=<your-ox-context-id>

      #. Run the migration script.
         The example command in :numref:`usage-shared-accounts-migration-n4k-listing`
         uses the variables that you defined in the previous steps.

         Verify the migration result
         before you continue with production use.

         .. code-block:: console
            :caption: Run the migration script
            :name: usage-shared-accounts-migration-n4k-listing

            $ kubectl \
               --namespace="$NAMESPACE_CONNECTOR" \
               exec ox-connector-0 -c main -- /bin/bash \
               -c 'UDM_USERNAME='$UDM_USERNAME' \
               UDM_URL="http://nubus-udm-rest-api:9979/univention/udm/" \
               UDM_PASSWORD='$UDM_PASSWORD' python3 \
               /usr/local/share/ox-connector/resources/migrate_fupo_to_shared_account.py \
               '$FUNCTIONAL_ACCOUNT' \
               "Full Mail Access" \
               --ox-context '$DESTINATION_OX_CONTEXT''
