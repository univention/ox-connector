.. SPDX-FileCopyrightText: 2021 - 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-usage-objects:

*****************
Manage OX objects
*****************

Use this page to manage OX App Suite objects.
The OX Connector synchronizes these objects from the LDAP directory.
The following instructions explain how to create and configure contexts,
user accounts, groups, access profiles, functional accounts, and resources
in the *Management UI*.
Read them to control which directory objects are available in OX App Suite
and how the connector provisions them.

To complete the following tasks, sign in to the *Management UI*
with a user account that has domain administration rights.

.. seealso::

   :external+uv-nubus-manual:ref:`nubus-ui`
      in :cite:t:`uv-nubus-manual`
      for information about the *Management UI*.

   :external+uv-nubus-manual:ref:`nubus-authentication-sign-in`
      in :cite:t:`uv-nubus-manual`
      for information about sign-in.

   :external+uv-ucs-operation:ref:`management-interface-delegated-administration`
      in :cite:t:`uv-ucs-operation`
      for information about delegative administration.

.. _ox-connector-usage-contexts:

Contexts
========

OX App Suite uses *contexts* to collect users, groups, and resources for
collaboration in a virtual space. Data from one context isn't visible to other
contexts. For more information about contexts, see
:cite:t:`ox-context-management`.

To view, add, update, or delete a context, navigate to
:menuselection:`Domain --> OX Contexts` in the *Management UI*.

.. note::

   If you manage *contexts* manually in OX App Suite,
   keep the OX Connector context configuration.
   You don't need to share the OX context administrator credentials.

   .. tab-set::

      .. tab-item:: Nubus for UCS
         :sync: ucs

         In Nubus for UCS deployments,
         the configuration for *contexts* is in the
         :file:`/var/lib/univention-appcenter/apps/ox-connector/data/secrets/contexts.json`
         file.

         After you changed the *contexts* configuration file,
         you need to restart the OX Connector
         so that the changes become active.
         For the necessary commands, see
         :numref:`ox-connector-usage-contexts-ucs-restart-listing`.

         .. code-block:: console
            :caption: Restart the OX Connector on Nubus for UCS
            :name: ox-connector-usage-contexts-ucs-restart-listing

            $ sudo systemctl restart docker-app-ox-connector.service \
                univention-appcenter-listener-converter@ox-connector.service

      .. tab-item:: Nubus for Kubernetes
         :sync: kubernetes

         In Nubus for Kubernetes deployments,
         the configuration for *contexts* is in the
         :file:`/etc/ox-secrets/ox-contexts.json` file
         as part of a *PVC*.
         To edit the file,
         see the commands in :numref:`ox-connector-usage-contexts-kubernetes-listing`.

         * Replace ``NAMESPACE`` with the Kubernetes namespace for the OX Connector.
           See :ref:`ox-connector-install-on-kubernetes-install-ox-consumer`.

         * Replace ``POD`` with the OX Connector pod name.

         .. code-block:: console
            :caption: Download, edit and upload :file:`ox-contexts.json`
            :name: ox-connector-usage-contexts-kubernetes-listing

            $ kubectl -n "$NAMESPACE" \
               get pods -l app.kubernetes.io/name=ox-connector
            $ kubectl -n "$NAMESPACE" \
               cp "$POD":/etc/ox-secrets/ox-contexts.json ./ox-contexts.json

            $ cp ./ox-contexts.json ./ox-contexts.json.bak
            $ EDITOR ./ox-contexts.json

            $ python3 -m json.tool ./ox-contexts.json >/dev/null

            $ kubectl -n "$NAMESPACE" \
               cp ./ox-contexts.json "$POD":/etc/ox-secrets/ox-contexts.json

         After you changed the *contexts* configuration file,
         you need to restart the OX Connector
         so that the changes become active.
         For the necessary commands, see
         :numref:`ox-connector-usage-contexts-kubernetes-restart-listing`.

         * As before, replace ``NAMESPACE``.
         * Replace ``STATEFULSET`` with the name returned by the first command.

         .. code-block:: console
            :caption: Restart the OX Connector in a Kubernetes deployment
            :name: ox-connector-usage-contexts-kubernetes-restart-listing

            $ kubectl -n "$NAMESPACE" \
               get statefulsets -l app.kubernetes.io/name=ox-connector
            $ kubectl -n "$NAMESPACE" \
               rollout restart statefulset/"$STATEFULSET"
            $ kubectl -n "$NAMESPACE" \
               rollout status statefulset/"$STATEFULSET"

.. _ox-connector-usage-users:

Users
=====

To add a user to OX App Suite, create a user account or update an existing one.

.. tab-set::

   .. tab-item:: Add user account

      To create a user account:

      #. Navigate to :menuselection:`Users --> Users` in the *Management UI*.

      #. Select :guilabel:`Add` and the *User template*
         ``open-xchange groupware account``.

      #. Select :guilabel:`Next`.

      #. Enter the required information. To enter additional attributes,
         select :guilabel:`Advanced`.

      #. Select :guilabel:`Create user`.

   .. tab-item:: Update user account

      To update a user account:

      #. Navigate to :menuselection:`Users --> Users` in the *Management UI*.

      #. Select the username of the user account that you want to update.

      #. On the *Apps* tab, select the *Open-Xchange* checkbox.
         The *Open-Xchange* tab appears.

      #. Enter the user's primary email address at
         :menuselection:`General --> Primary email address (mailbox)`.

      #. Select :guilabel:`Save`.

.. seealso::

   :external+uv-nubus-manual:ref:`nubus-user-management`
      in :cite:t:`uv-nubus-manual`
      for information about user management in Nubus.

.. _ox-connector-usage-groups:

Groups
======

The :program:`OX Connector` app adds a group to the same context as the group
members. When the last group member leaves the group, the connector removes the
group from OX App Suite.

To enable a group for OX App Suite, follow these procedures:

.. tab-set::

   .. tab-item:: Add group

      To create a group:

      #. Navigate to :menuselection:`Users --> Groups` in the *Management UI*.

      #. Select :guilabel:`Add`.

      #. On the *General* tab, enter the required information
         and add users as group members.

      #. On the *OX App Suite* tab, select the *Activate Group in OX* checkbox.

      #. Select :guilabel:`Create group`.

   .. tab-item:: Update group

      To update a group:

      #. Navigate to :menuselection:`Users --> Groups` in the *Management UI*.

      #. Select the group that you want to edit.

      #. The *Groups* module in the *Management UI* automatically selects the
         *Activate Group in OX* checkbox when you edit a group. The *Management UI*
         displays a notification.

      #. To prevent OX provisioning,
         clear the *Activate Group in OX* checkbox on the *OX App Suite* tab.

      #. Select :guilabel:`Save`.

      .. warning::

         If you clear the *Activate Group in OX* checkbox while updating a group that
         exists in OX App Suite, the connector removes the group from OX App Suite.

      To update a group from the command line,
      run the command in
      :numref:`ox-connector-update-group-command`.
      Replace ``GROUP_DN`` with the distinguished name (DN) of the group.

      .. code-block:: console
         :caption: Update a group from the command line
         :name: ox-connector-update-group-command

         $ udm groups/group modify --dn GROUP_DN --set isOxGroup=OK

   .. tab-item:: Remove group

      To remove a group from OX App Suite:

      #. Navigate to :menuselection:`Users --> Groups` in the *Management UI*.
      #. Select the group that you want to edit.
      #. On the *OX App Suite* tab, clear the *Activate Group in OX* checkbox.
      #. Select :guilabel:`Save`.

      To remove a group from OX App Suite,
      run the command in
      :numref:`ox-connector-remove-group-command`.
      Replace ``GROUP_DN`` with the distinguished name (DN) of the group.

      .. code-block:: console
         :caption: Remove a group from the command line
         :name: ox-connector-remove-group-command

         $ udm groups/group modify --dn GROUP_DN --set isOxGroup=Not

.. seealso::

   :external+uv-nubus-manual:ref:`nubus-groups`
      in :cite:t:`uv-nubus-manual`
      for information about group management in Nubus.

.. _ox-connector-usage-access-profiles:

Access profiles
===============

The OX Connector provides *access profiles* for OX App Suite users.
To view custom *access profiles*:

#. Navigate to :menuselection:`Domain --> LDAP directory`
   in the *Management UI*.

#. In the *LDAP directory* module, open
   ``open-xchange/accessprofiles/``.

.. TODO: Reactivate after limitations are available with #174

   For limitations about plausibility verification, see
   :ref:`limit-access-profiles`.

.. _ox-connector-usage-functional-accounts:

Functional accounts
===================

.. deprecated:: 3.2.0
   Open-Xchange deprecated this feature in favor of
   :ref:`ox-connector-usage-shared-accounts`.

.. versionadded:: 2.0.0

Functional accounts let users in the same context share a functional mailbox and
its read status.

Use the ``oxmail/functional_account`` management module to add, update, or delete
functional-account objects.
When administrators grant a user permission,
emails sent to functional-account addresses appear in the OX Mail view for that user.

.. versionadded:: 2.2.12

The default directory position for ``oxmail/functional_account`` objects is:
``cn=functional_accounts,cn=open-xchange,$LDAP_BASE``.
Replace ``$LDAP_BASE`` with the LDAP base DN.

You can add default containers for ``oxmail/functional_account``.
The *Management UI* then prompts you to select a position when you create an object.

To add default containers:

#. In the :guilabel:`LDAP directory` module, open the ``univention`` container.

#. Open the ``default containers`` object.

#. Select ``OX App Suite``.

#. Add containers to the ``Default container for OX functional accounts`` list.

Enter the distinguished names (DNs) of existing container objects.
Each DN must include the LDAP base DN.

.. _ox-connector-usage-resources:

Resources
=========

Use *OX Resources* to manage bookable rooms and equipment.
For more information about resource management, see
:cite:t:`ox-resource-management`.

To view resources, navigate to
:menuselection:`Domain --> OX Resources` in the *Management UI*.

.. spelling:word-list::

   delegative
