.. SPDX-FileCopyrightText: 2021 - 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-usage-shared-accounts:

***************
Shared accounts
***************

.. versionadded:: 3.2.0

OX App Suite lets users and groups access shared accounts.
Users with access to a shared account can read its email and calendar entries.
As an administrator, you can configure fine-grained permissions for users and groups.
The OX Connector app provides management modules for the *Management UI* in Nubus
that let you manage shared accounts and user and group permissions.

.. important::

   The *Shared accounts* feature requires *OX App Suite* version 8.49 or later.
   A runtime check deactivates the feature
   when *OX App Suite* doesn't support shared accounts.

.. seealso::

   `Shared accounts <https://documentation.open-xchange.com/8/middleware/permissions_and_capabilities/shared_accounts.html>`_
      in :cite:t:`ox-middleware`
      for information about shared accounts in OX App Suite.

.. _ox-connector-usage-shared-accounts-udm-module:

Management module for shared accounts
=====================================

Use the ``oxmail/shared_account`` management module to manage shared accounts
and their permissions.
In the *Management UI*, find the management module under *LDAP directory*
at ``open-xchange/shared_account``.

Every ``oxmail/shared_account`` object contains a list of users and groups with their respective permissions.
Each user and group entry in the list links to an ``oxmail/shared_account_permission`` object.

.. seealso::

   :external+uv-nubus-manual:ref:`nubus-domain-ldap`
      in :cite:t:`uv-nubus-manual`
      for information about the *LDAP directory* management module.

.. _ox-connector-usage-shared-accounts-udm-permissions:

Management module for permissions
=================================

OX App Suite uses permission objects
to control user and group access to shared accounts.
OX Connector provides the following predefined *permissions*
for OX App Suite shared accounts:

- *Full Calendar Access*
- *Full Mail Access*
- *Full Mail and Calendar Access*
- *Read-Only Mail Access*

You can also create permissions to meet your requirements.

Use the ``oxmail/shared_account_permission`` management module
to manage permissions for shared accounts.
In the *Management UI*, find the management module under *LDAP directory*
at ``open-xchange/shared_account_permission``.

When you create an ``oxmail/shared_account`` object,
you can grant permissions to users and groups in the *Management UI*.

.. _ox-connector-usage-shared-accounts-migration:

Migration from functional accounts to shared accounts
=====================================================

.. versionadded:: 3.2.1

OX App Suite has deprecated :ref:`ox-connector-usage-functional-accounts`.
OX Connector provides a script
that lets you migrate functional accounts to shared accounts.

Before you run the script,
:program:`Dovecot` must use the email address
as the unique identifier for the mail accounts.

.. danger::

   If your :program:`Dovecot` installation uses a unique identifier
   other than the email address,
   **don't run** the migration script.
   In that case, the script deletes your functional accounts
   and creates shared accounts without their content.

Before you use the migration script in production,
run it with the ``--dry-run`` option and review the output.
The ``--dry-run`` option doesn't make changes.
It displays the migration steps that the script would perform.

To view the migration script parameters,
run the script with the ``--help`` option.
The help output describes migrating multiple functional accounts in one run.
It also explains how to supply credentials through environment variables.

For troubleshooting, see :ref:`ox-connector-troubleshooting-ucs-migration`.

Choose the instructions for your OX Connector deployment.

.. tab-set::

   .. tab-item:: Nubus for UCS
      :sync: ucs

      For Nubus for UCS, run the migration script on the system
      where you installed the OX Connector.
      Use the commands in :numref:`usage-shared-accounts-migration-prepare-ucs-listing`
      and :numref:`usage-shared-accounts-migration-ucs-listing`.
      In the following command listings, replace the placeholders
      with values for these inputs:

      ``UDM_USERNAME``
         The username for the Univention Directory Manager (UDM) user account.
         The user account must be a member of the :external+uv-nubus-customization:ref:`customization-api-udm-rest-auth-group`
         for the *UDM HTTP REST API*.

      ``UDM_PASSWORD``
         The password for the ``UDM_USERNAME``.

      ``REST_API_HOSTNAME``
         The fully qualified domain name (FQDN) of the UDM HTTP REST API in your domain.

      ``OPTIONAL_DESTINATION``
         The optional full distinguished name (DN) for the new shared account
         when migrating one functional account.
         For example, :samp:`cn=example,cn=shared_accounts,cn=open-xchange,{LDAP_BASE}`.
         If you omit this value, the script derives the destination DN.

      ``DESTINATION_OX_CONTEXT``
         The OX Context where the migration script creates the shared account.

      .. code-block:: console
         :caption: Prepare migration to shared accounts
         :name: usage-shared-accounts-migration-prepare-ucs-listing

         $ export UDM_USERNAME="MANAGEMENT_USERNAME"
         $ export UDM_PASSWORD="MANAGEMENT_PASSWORD"
         $ export REST_API_HOSTNAME="MANAGEMENT_API_HOSTNAME"
         $ export OPTIONAL_DESTINATION="OPTIONAL_DESTINATION_DN"
         $ export DESTINATION_OX_CONTEXT=OX_CONTEXT_ID

      .. code-block:: console
         :caption: Test the migration from functional accounts to shared accounts
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
            --ox-context $DESTINATION_OX_CONTEXT \
            --dry-run

      After you verify the output,
      remove ``--dry-run`` and rerun the command
      to migrate the functional account.
      Confirm that the output contains ``Resulting Shared Account:``
      and review the printed shared-account properties.

   .. tab-item:: Nubus for Kubernetes
      :sync: kubernetes

      To run the migration script in Nubus for Kubernetes,
      follow these steps.

      #. To set the environment variables for your Nubus for Kubernetes environment
         and OX Consumer deployment,
         run the commands in :numref:`usage-shared-accounts-migration-env-listing`.

         ``NAMESPACE_N4K``
            The Kubernetes namespace for your Nubus for Kubernetes deployment.

         ``RELEASE_N4K``
            The release name for your Nubus for Kubernetes deployment.
            To list the release names in your namespace,
            run the command in :numref:`usage-shared-accounts-migration-release-name-listing`.

         ``NAMESPACE_CONNECTOR``
            The Kubernetes namespace of your OX Connector deployment.
            Typically, it is the same namespace as your Nubus for Kubernetes deployment.

         .. code-block:: console
            :caption: Set environment variables for Nubus for Kubernetes and the OX Connector
            :name: usage-shared-accounts-migration-env-listing

            $ export NAMESPACE_CONNECTOR="CONNECTOR_NAMESPACE"
            $ export NAMESPACE_N4K="NUBUS_NAMESPACE"
            $ export RELEASE_N4K="NUBUS_RELEASE"

         .. code-block:: console
            :caption: Show the release names in the namespace of Nubus for Kubernetes
            :name: usage-shared-accounts-migration-release-name-listing

            $ helm --namespace "$NAMESPACE_N4K" list -q

      #. Retrieve the LDAP base DN from your Nubus for Kubernetes environment.

         You need the LDAP base DN of your Nubus for Kubernetes deployment.
         You set the LDAP base DN in the :file:`custom_values.yaml` file
         during the
         :external+uv-nubus-kubernetes-operation:ref:`deployment of Nubus for Kubernetes <nubus-deployment-all-deps>`.
         To retrieve the LDAP base DN,
         run the command in :numref:`usage-shared-accounts-migration-n4k-retrieve-values-listing`.

         ``LDAP_BASE``
            The LDAP base DN of your directory service.

         .. code-block:: console
            :caption: Retrieve the LDAP base DN from Nubus for Kubernetes
            :name: usage-shared-accounts-migration-n4k-retrieve-values-listing

            $ export LDAP_BASE="$(kubectl \
               --namespace "$NAMESPACE_N4K" \
               get configmap \
               "$RELEASE_N4K-ldap-server" \
               -o "jsonpath={.data.LDAP_BASE_DN}")"

      #. Configure the remaining environment variables for the migration script.

         ``UDM_USERNAME``
            The username for the UDM user.
            The user account must be a member of the
            :external+uv-nubus-customization:ref:`customization-api-udm-rest-auth-group`
            for the *UDM HTTP REST API*.

         ``UDM_PASSWORD``
            The password for the ``UDM_USERNAME``.

         ``FUNCTIONAL_ACCOUNT``
            The LDAP distinguished name (DN) of the functional account that you want to migrate.

         ``DESTINATION_OX_CONTEXT``
            The OX Context where the migration script creates the shared account.

         .. code-block:: console
            :caption: Define the remaining parameters for the migration
            :name: usage-shared-accounts-migration-prepare-n4k-listing

            $ export UDM_USERNAME="MANAGEMENT_USERNAME"
            $ export UDM_PASSWORD="MANAGEMENT_PASSWORD"
            $ export FUNCTIONAL_ACCOUNT="cn=example_fupo,cn=functional_accounts,cn=open-xchange,$LDAP_BASE"
            $ export DESTINATION_OX_CONTEXT=OX_CONTEXT_ID

      #. Test the migration script.
         The example command in :numref:`usage-shared-accounts-migration-n4k-listing`
         uses the variables that you defined in the previous steps.
         Run the command with the ``--dry-run`` option.

         If the output is as expected, remove ``--dry-run`` and rerun the command.
         Confirm that the output contains ``Resulting Shared Account:``
         and review the printed shared-account properties
         before you use the script in production.

         .. code-block:: console
            :caption: Test the migration script
            :name: usage-shared-accounts-migration-n4k-listing

            $ kubectl \
               --namespace="$NAMESPACE_CONNECTOR" \
               get pods

            $ export CONNECTOR_POD="OX_CONNECTOR_POD"

            $ kubectl \
               --namespace="$NAMESPACE_CONNECTOR" \
               exec "$CONNECTOR_POD" -c main -- /bin/bash \
               -c 'UDM_USERNAME='$UDM_USERNAME' \
               UDM_URL="http://nubus-udm-rest-api:9979/univention/udm/" \
               UDM_PASSWORD='$UDM_PASSWORD' python3 \
               /usr/local/share/ox-connector/resources/migrate_fupo_to_shared_account.py \
               '$FUNCTIONAL_ACCOUNT' \
               "Full Mail Access" \
               --ox-context '$DESTINATION_OX_CONTEXT' \
               --dry-run'
