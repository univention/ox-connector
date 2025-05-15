.. SPDX-FileCopyrightText: 2021-2023 Univention GmbH
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

.. tab:: Add user account

   To create a user account:

   2. Click :guilabel:`Add` to create a user account and select the *User
      template* ``open-xchange groupware account``.

   #. Click :guilabel:`Next`.

   #. Fill out the required fields. To fill out more attributes, click :guilabel:`Advanced`.

   #. When finished, click :guilabel:`Create user`.

.. tab:: Update user account

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

.. tab:: Add group

   To create a group:

   2. Click :guilabel:`Add` to create a group.

   #. On the *General* tab, fill out the required fields and add users as group
      members.

   #. Go to the *OX App Suite* tab and activate the *Activate Group in OX*.

   #. Click :guilabel:`Create group`.


.. tab:: Update group

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

.. tab:: Remove group

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
