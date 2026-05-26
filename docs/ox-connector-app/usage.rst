.. SPDX-FileCopyrightText: 2021 - 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _app-usage:

*****
Usage
*****

The :program:`OX Connector` centrally manages users, groups, OX contexts, OX
access profiles and functional accounts with the web based management system in
UCS. This section shows how.

To follow the tasks, you need to sign-in to Univention Management Console (UMC)
with a user account with domain administration rights. For more information, see
:ref:`uv-manual:delegated-administration` in :cite:t:`ucs-manual`.

.. _usage-contexts:

Contexts
========

OX App Suite uses *contexts* to collect users, groups, and resources for
collaboration in a virtual space. Data from one context isn't visible to other
contexts. For more information about contexts, see
:cite:t:`ox-context-management`.

To view, add, update, or delete a context, you navigate to
:menuselection:`Domain --> OX Contexts` in UMC.

.. note::

   If you don't want the OX Connector to manage *contexts*, you can manually
   manage them in OX App Suite, as long as you maintain the *context*
   configuration for the OX Connector in the
   :file:`/var/lib/univention-appcenter/apps/ox-connector/data/secrets/contexts.json`.

   This approach doesn't require to share the credentials for the OX context
   administrator.


.. _usage-users:

Users
=====

To enable users for OX App Suite, administrators can either create user accounts
or update existing ones.

To enable a user account for OX App Suite, run the following steps:

#. Navigate to :menuselection:`Users --> Users` in UMC and click to open.

.. tab-set::

   .. tab-item:: Add user account

      To create a user account:

      2. Click :guilabel:`Add` to create a user account and select the *User
         template* ``open-xchange groupware account``.

      #. Click :guilabel:`Next`.

      #. Fill out the required fields. To fill out more attributes, click :guilabel:`Advanced`.

      #. When finished, click :guilabel:`Create user`.

   .. tab-item:: Update user account

      To update a user account:

      2. Click the username for the user you want to update.

      #. Go to the *Apps* tab and activate the *Open-Xchange* checkbox. The tab
         *Open-Xchange* appears.

      #. Define an email address for the user at :menuselection:`General --> Primary
         e-mail address (mailbox)`.

      #. Click :guilabel:`Save`.

.. seealso::

   :ref:`uv-manual:users-general` in :cite:t:`ucs-manual`.

.. _usage-groups:

Groups
======

The :program:`OX Connector` app adds a group to the same context as the group
members. When the last group member leaves the group, the connector removes the
group from OX App Suite.

To enable a group for OX App suite, run the following steps:

#. Navigate to :menuselection:`Users --> Groups` in UMC and click to open.

..tab-set::

   .. tab-item:: Add group

      To create a group:

      2. Click :guilabel:`Add` to create a group.

      #. On the *General* tab, fill out the required fields and add users as group
         members.

      #. Go to the *OX App Suite* tab and activate the *Activate Group in OX*.

      #. Click :guilabel:`Create group`.


   .. tab-item:: Update group

      To update a group:

      2. Click a group to edit.

      #. The UDM module *Groups* automatically enables *Activate Group in OX*, when
         you edit a group. UMC displays a notification.

         If you don't want to enable the group, clear the checkbox *Activate Group
         in OX* on the *OX App Suite* tab.

      #. Click :guilabel:`Save`.

      .. warning::

         When you as administrator update a group, that already is a group in OX App
         Suite, and you clear the checkbox *Activate Group in OX* on the *OX App
         Suite* tab, the connector removes this group from OX App Suite.

      To update a group from the command-line, run the following command:

      .. code-block:: console

         $ udm groups/group modify --dn $dn_of_group --set isOxGroup=OK

   .. tab-item:: Remove group

      To remove a group from OX App Suite:

      2. Click a group to edit.

      #. Go to the *OX App Suite* tab and clear the checkbox *Activate Group
         in OX*.

      #. Click :guilabel:`Save`.

      To remove the group from OX App Suite through command-line, run the following
      command:

      .. code-block:: console

         $ udm groups/group modify --dn $dn_of_group --set isOxGroup=Not

.. seealso:: :ref:`uv-manual:groups` in :cite:t:`ucs-manual`.

.. _usage-access-profiles:

Access profiles
===============

The OX Connector already provides ready-to-use *access profiles* for OX App Suite
users. Administrators can create custom *access profiles* in UMC in the *LDAP
directory* module at :menuselection:`Domain --> LDAP directory` at the directory
location ``open-xchange/accessprofiles/``.

For limitations about plausibility verification, see
:ref:`limit-access-profiles`.

.. _usage-functional-accounts:

Functional accounts
===================

.. versionadded:: 2.0.0

OX App Suite shares functional mailboxes among other users in the same context.

With the |UDM| module ``oxmail/functional_account`` administrators can add,
update or delete objects for functional accounts. OX App Suite users with the
same functional account share the read status. Emails to addresses of functional
accounts show up in the OX Mail view for every user where administrators granted
the permission.

.. warning::

   Open-Xchange marked this feature as deprecated in favor of :ref:`usage-shared-accounts`.


Default LDAP position for functional accounts
---------------------------------------------

.. versionadded:: 2.2.12

When you create a new ``oxmail/functional_account`` object in |UMC| the
default position for these new objects in the directory tree is
``cn=functional_accounts,cn=open-xchange,$LDAP_BASE``.

However, you can add additional default containers for the
``oxmail/functional_account`` so that |UMC| will ask for a position before
creating the new object.

In the UMC module :guilabel:`LDAP directory` open the container ``univention``
in the tree view (left) and then open the object ``default containers`` in
the object list (right). Click on ``OX App suite`` and add additional default
containers to the list of ``Default container for OX functional accounts``.
The values are LDAP DNs of existing container objects in your LDAP directory,
which must include the LDAP base DN.

.. _usage-resources:

Resources
=========

OX App Suite uses *OX Resources* to manage resources like rooms or equipment
that users can book for appointments. For more information about resource
management, see :cite:t:`ox-resource-management`.

To view, add, update, or delete a resource, you navigate to
:menuselection:`Domain --> OX Resources` in UMC.

.. TODO : Add section about resources.

.. _usage-shared-accounts:

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

.. _usage-shared-accounts-udm-module:

UDM module for shared accounts
------------------------------

As an administrator, you can use the |UDM| module ``oxmail/shared_account``
to add, update, or delete objects for shared accounts
and manage their permissions.
You can find the UDM module in the *Management UI* under *LDAP directory*
at the directory location ``open-xchange/shared_account``.

Every ``oxmail/shared_account`` object contains a list of users and groups with their respective permissions.
Each user and group entry in the list links to an ``oxmail/shared_account_permissions`` object.

.. seealso::

   :external+uv-nubus-manual:ref:`nubus-domain-ldap`
      for information about the *LDAP directory* management module.

.. _usage-shared-accounts-udm-permissions:

UDM module for permissions
--------------------------

OX App Suite uses permission objects to control user and group access to shared accounts.
OX Connector provides ready-to-use *permissions* for OX App Suite shared accounts,
including *Full Calendar Access*, *Full Mail Access*, *Full Mail and Calendar Access*, and *Read-Only Mail Access*.
You can also create permissions to meet your requirements.

As an administrator, you can use the |UDM| module ``oxmail/shared_account_permissions``
to create, update, or delete permissions for shared accounts.
You can find the UDM module in the *Management UI* under *LDAP directory*
at the directory location ``open-xchange/shared_account_permissions``.

When you create an ``oxmail/shared_account`` object,
you can grant permissions to users and groups in |UMC|.

.. _usage-shared-accounts-migration:

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
