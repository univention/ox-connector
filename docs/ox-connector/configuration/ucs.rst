.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-configuration-ucs:

Configuration for UCS
=====================

Use this reference to configure the :program:`OX Connector` app
on Nubus for UCS.
The app settings define how the connector reaches *OX App Suite*
and how it provisions users, groups, shared accounts, and related features.
The UCR variables describe UCS-specific values
that affect the connector configuration.

.. _ox-connector-configuration-ucs-app-settings:

App settings
------------

.. envvar:: OX_SOAP_SERVER

   Defines the *OX App Suite* server.
   Provide the protocol and the fully qualified domain name (FQDN),
   for example :samp:`https://ox-app-suite.example.com`.

   :envvar:`OX_SOAP_SERVER` tells the :program:`OX Connector` app in the container
   where to look for the *OX App Suite* system.
   The container must resolve the FQDN.

   For secure HTTPS connections,
   the container needs to validate the certificate.
   If the *OX App Suite* instance uses a self-signed certificate
   or a certificate that the :program:`OX Connector` container can't validate,
   the container needs the root certificate for validation.
   For information about how to add self-signed certificates,
   see :ref:`ox-connector-ucs-additional-certificates`.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - Yes
        - String
        - :samp:`https://{$hostname}.{$domainname}`


.. envvar:: OX_IMAP_SERVER

   Defines the default IMAP server for new users,
   if not explicitly set on the user object.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - Yes
        - String
        - :samp:`imap://{$hostname}.{$domainname}:143`


.. envvar:: OX_SMTP_SERVER

   Defines the SMTP server for new users,
   if not explicitly set on the user object.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - Yes
        - String
        - :samp:`smtp://{$hostname}.{$domainname}:587`


.. envvar:: DEFAULT_CONTEXT

   Defines the default context for users.
   The :program:`OX Connector` doesn't create ``DEFAULT_CONTEXT`` automatically.
   Before the :program:`OX Connector` provisions the first user,
   ensure that the default context exists.

   To create a context, see :ref:`ox-connector-usage`.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - Yes
        - Integer
        - ``10``


.. envvar:: OX_LANGUAGE

   Defines the default language for new users.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - Yes
        - String
        - ``de_DE``


.. envvar:: LOCAL_TIMEZONE

   Defines the default time zone for new users.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - Yes
        - String
        - ``Europe/Berlin``


.. envvar:: OX_MASTER_ADMIN

   Defines the username for the *OX App Suite* administrator account,
   also called the *OX Admin user*.
   This user can create, modify, and delete contexts.
   The user must already exist.
   The administrator defines the username for the *OX Admin user*
   during the installation of OX App Suite.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - Yes
        - String
        - ``oxadminmaster``


.. envvar:: OX_MASTER_PASSWORD

   Defines the password for the *OX Admin user*.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - Password
        - N/A


.. envvar:: OX_IMAP_LOGIN

   Defines the value that *OX App Suite* uses to access the user's inbox.
   If this value is empty,
   *OX App Suite* sets it to the user's email address.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - String
        - N/A

   If you use single sign-on (SSO),
   append an asterisk and the mail server master user to this variable.
   For Dovecot,
   set ``OX_IMAP_LOGIN`` to ``'{}*dovecotadmin'``.

   The :program:`OX Connector` interprets the curly braces as a template.
   Empty braces use ``primaryMailAddress``.
   To use another user attribute,
   enter the attribute name in the braces,
   for example ``{username}``.


.. envvar:: OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE

   Defines the value that *OX App Suite* uses
   to access the functional account inbox.
   If this value is empty,
   the :program:`OX Connector` sets it to a concatenation
   of the functional account LDAP entry UUID and the LDAP UID of the user.

   This template can include the functional account entry UUID
   (``fa_entry_uuid``),
   the functional account email address (``fa_email_address``),
   and any Univention Directory Manager (UDM) property of the OX user,
   including the user's ``entry_uuid`` and ``dn``.
   Enclose every UDM property used in this template in ``{{ }}``,
   for example ``{{fa_entry_uuid}}{{username}}``.
   You can optionally separate multiple values with other text.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - String
        - N/A

   If you use the *OX App Suite* app from Univention App Center,
   you can leave this app setting empty.
   An empty value is equivalent to ``{{fa_entry_uuid}}{{username}}``.

   If an existing :program:`OX Connector` installation used only
   the functional account entry UUID,
   set this app setting to ``{{fa_entry_uuid}}``.

   :numref:`settings-ox-functional-account-login-template-examples-listing`
   shows valid template values.

   .. code-block:: console
      :caption: Valid functional account login template values
      :name: settings-ox-functional-account-login-template-examples-listing

      "{{fa_entry_uuid}}::{{entry_uuid}}"
      "{{username}}+{{fa_entry_uuid}}+{{dn}}"
      "{{fa_email_address}}*dovecotadmin"

   ``{{fa_entry_uuid}}::{{entry_uuid}}``
      Concatenates the functional account entry UUID
      and the user UUID,
      separated by two colons.

   ``{{username}}+{{fa_entry_uuid}}+{{dn}}``
      Concatenates the username,
      the functional account entry UUID,
      and the user DN,
      separated by plus signs.

   ``{{fa_email_address}}*dovecotadmin``
      Concatenates the functional account email address
      and the string ``*dovecotadmin``.

   If you use single sign-on,
   append an asterisk and the mail server master user to this variable.
   For Dovecot,
   set ``OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE``
   to ``'{{fa_email_address}}*dovecotadmin'``.
   :numref:`settings-ox-functional-account-login-template-sso-listing`
   shows the resulting login value for the functional account.

   .. code-block:: console
      :caption: Resulting functional account login value with SSO
      :name: settings-ox-functional-account-login-template-sso-listing

      myfunctional_account@maildomain.de*dovecotadmin


.. envvar:: OX_USER_IDENTIFIER

   Defines the UDM user property that *OX App Suite* uses
   as the unique user identifier.
   If this app setting isn't set,
   the :program:`OX Connector` uses the ``username`` property by default.

   For Nubus for Kubernetes, see :envvar:`openXchange.mappings.userIdentifier`.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - String
        - N/A

   .. caution::

      Use only a mandatory UDM user property
      that contains one non-empty value.
      If you specify a UDM user property
      that contains an empty value or a list of values,
      the :program:`OX Connector` enters an error state.
      To resolve the error,
      set a valid property.

.. envvar:: OX_GROUP_IDENTIFIER

   Defines the UDM group property that *OX App Suite* uses
   as the unique group identifier.
   If this app setting isn't set,
   the :program:`OX Connector` uses the ``name`` property by default.

   For Nubus for Kubernetes, see :envvar:`openXchange.mappings.groupIdentifier`.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - String
        - N/A

   .. caution::

      Use only a mandatory UDM group property
      that contains one non-empty value.
      If you specify a UDM group property
      that contains an empty value or a list of values,
      the :program:`OX Connector` enters an error state.
      To resolve the error,
      set a valid property.

.. envvar:: OX_SHARED_ACCOUNT_IDENTIFIER

   Defines the UDM shared account property that *OX App Suite* uses
   as the unique shared account identifier.
   If this app setting isn't set,
   the :program:`OX Connector` uses the ``name`` property by default.

   For Nubus for Kubernetes, see :envvar:`openXchange.mappings.sharedAccountIdentifier`.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - String
        - N/A

   .. caution::

      Use only a mandatory UDM shared account property
      that contains one non-empty value.
      If you specify a UDM shared account property
      that contains an empty value or a list of values,
      the :program:`OX Connector` enters an error state.
      To resolve the error,
      set a valid property.

.. envvar:: OX_CONNECTOR_LOG_LEVEL

   Defines the log level for the :program:`OX Connector` app.
   If this app setting isn't set,
   the :program:`OX Connector` uses ``INFO`` by default.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - String
        - ``INFO``

.. envvar:: OX_ENABLE_DEPUTY_PERMISSIONS

   Enables the provisioning of OX deputy permissions.
   Administrators can then set, modify, or delete deputy permissions
   for users in the *Management UI*.

   For example,
   administrators can grant ``user01`` the roles *Viewer*, *Editor*, and *Author*
   for the calendar and mail modules for ``user02``.
   Also,
   ``user01`` can send email on behalf of ``user02``.

   The default value is ``False``.
   To enable the feature,
   set the app setting :envvar:`OX_ENABLE_DEPUTY_PERMISSIONS` to ``True``.

   To show the feature in the *Management UI*,
   you must enable the UMC representation for the extended attribute
   after the app installation
   or after the configuration.
   Run the command in :numref:`settings-ox-enable-deputy-permission-listing`
   on the :external+uv-ucs-operation:term:`Primary Directory Node`
   or a :external+uv-ucs-operation:term:`Backup Directory Node`.

   .. code-block:: console
      :caption: Activate the UMC representation of the enabled deputy permission feature.
      :name: settings-ox-enable-deputy-permission-listing

      $ univention-directory-manager \
         settings/extended_attribute modify \
         --dn "cn=oxDeputyPermissionGivenTo,cn=open-xchange,cn=custom attributes,cn=univention,$(ucr get ldap/base)" \
         --set disableUDMWeb="0"

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - Boolean
        - ``False``

   .. important::

      The *Deputy Permissions* feature requires *OX App Suite* version 8 or later.

      Users can modify their deputy permissions in *OX App Suite*.
      Provisioning through the :program:`OX Connector` app in Nubus for UCS
      overwrites these settings.

   .. seealso::

      `Deputy permissions: Technical Documentation <https://documentation.open-xchange.com/8/middleware/permissions_and_capabilities/deputy_permission.html>`_
         for more information about OX deputy permissions.

.. envvar:: OX_CONNECTOR_STOP_ON_ERROR

   Changes how the :program:`OX Connector` app handles synchronization errors.
   Set one of the following values:

   ``True``
      Stop on any error.
      The app retries the failed action until it succeeds
      or an administrator resolves the error manually.

   ``False``
      Continue with other queued actions.
      The app moves the failed action to the morgue.
      The failed action no longer interferes with the connector run,
      and an administrator can examine it later.

      For information about managing provisioning tasks in Nubus for UCS,
      see :ref:`ox-connector-troubleshooting-ucs-manage-provisioning-tasks`.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - Boolean
        - ``True``

.. _ox-connector-configuration-ucs-ucr-variables:

UCR variables
-------------

.. envvar:: ox/context/id

   The app setting :envvar:`DEFAULT_CONTEXT` sets the value of the UCR variable
   :envvar:`ox/context/id`.

   When you install the :program:`OX Connector` app,
   it creates the extended attribute ``oxContext``
   and uses the value from :envvar:`ox/context/id`
   as the initial value for the extended attribute ``oxContext``.

   When an administrator creates a user account
   that the :program:`OX Connector` app synchronizes,
   UDM sets the OX context for the user account
   to the value of the extended attribute ``oxContext``.

   .. caution::

      The UCR variable :envvar:`ox/context/id` **isn't** for manual use.

      Changing the variable **doesn't** change the OX context
      on existing user accounts.

      Changing the value of the app setting :envvar:`DEFAULT_CONTEXT`
      changes **neither** :envvar:`ox/context/id`
      **nor** the extended attribute ``oxContext``.

.. _ox-connector-configuration-ucs-user-attribute-mapping:

User attribute mapping
----------------------

Since version 2.2.9,
you can change the mapping between *Open-Xchange* and *UDM* properties.
Use the :program:`change_attribute_mapping.py` script from the app.
The script creates a JSON file
with the Open-Xchange property mapping
and provisioning data.

Don't modify the file manually.
Use only the script.
The script stores the JSON file at
:file:`/var/lib/univention-appcenter/apps/ox-connector/data/AttributeMapping.json`.

If the file doesn't exist,
the :program:`OX Connector` app uses the default mapping.
The default mapping comes from the following file
inside the container of the app:

:file:`/usr/lib/python3.9/site-packages/univention/ox/provisioning/default_user_mapping.py`.

.. program:: change_attribute_mapping.py

The script supports these actions:

.. option:: modify

   Performs operations that change the current mapping.

.. option:: restore_default

   Restores the default mapping.

.. option:: dump

   Writes the current JSON mapping to the console.


The *modify* action supports these options:

.. option:: modify --set

   Changes the UDM property used to provision an Open-Xchange property.
   :numref:`conf-user-mapping-set-listing` shows how to map
   the Open-Xchange property ``userfield01``
   to the UDM property ``description``.

   .. code-block:: console
      :caption: Set the mapping of an Open-Xchange property to a UDM property
      :name: conf-user-mapping-set-listing

      $ python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         modify \
         --set userfield01 description

   You can use the :option:`modify --set` argument multiple times
   in the same invocation.
   :numref:`conf-user-mapping-multiple-set-listing` shows how to map
   multiple Open-Xchange properties to multiple UDM properties.

   .. code-block:: console
      :caption: Set multiple Open-Xchange properties to multiple UDM properties
      :name: conf-user-mapping-multiple-set-listing

      $ python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         modify \
         --set userfield01 description \
         --set given_name custom_attribute

.. option:: modify --unset

   Removes the Open-Xchange property from the mapping
   if the property isn't marked as required.
   You can use this option to remove properties from synchronization.

   .. code-block:: console
      :caption: Unset the OX property ``userfield01``.

      $ python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         modify \
         --unset userfield01

.. option:: modify --set_alternatives

   Sets alternative UDM properties for synchronization
   when the primary UDM property is ``None``.
   :numref:`conf-user-mapping-set-alternative-listing`
   shows how to set the example attributes
   ``CustomAttributeUserMail`` and ``CustomAttributeUserMail2``
   as alternatives to the Open-Xchange property ``email1``.

   .. code-block:: console
      :caption: Set example attributes as alternatives to an Open-Xchange property
      :name: conf-user-mapping-set-alternative-listing

      $ python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         modify \
         --set_alternatives email1 CustomAttributeUserMail CustomAttributeUserMail2

.. option:: modify --unset_alternatives

   Removes the current alternatives for an OX property.

   :numref:`conf-user-mapping-unset-alternative-listing`
   shows how to remove the alternative attributes for the OX property ``email1``.

   .. code-block:: console
      :caption: Unset the alternative attributes for the OX property ``email1``
      :name: conf-user-mapping-unset-alternative-listing

      $ python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         modify \
         --unset_alternatives email1

You can migrate an existing attribute mapping
from the *OX App Suite* app in Univention App Center.
To migrate the mapping,
do the following:

#. On the Nubus for UCS system that runs *OX App Suite*,
   run the command in
   :numref:`conf-user-mapping-migrate-existing-mapping-listing`.

   .. code-block:: console
      :caption: Create the migration command for an existing attribute mapping
      :name: conf-user-mapping-migrate-existing-mapping-listing

      $ python3 <<EOF
      from univention.config_registry import ConfigRegistry
      ucr = ConfigRegistry()
      ucr.load()

      changed_mapping_single = {
        'displayname': 'display_name',
        'givenmame': 'given_name',
        'surname': 'sur_name',
        'categories': 'employee_type',
        'quota': 'max_quota',
        }

      changed_mapping_multi = {
        'telephone_business': ['telephone_business1', 'telephone_business2'],
        'telephone_home': ['telephone_home1', 'telephone_home2'],
      }


      ucr_ldap2ox = ucr.get('ox/listener/user/ldap/attributes/mapping/ldap2ox', '').strip()
      ucr_ldap2oxmulti = ucr.get('ox/listener/user/ldap/attributes/mapping/ldap2oxmulti', '').strip()
      command = []
      if ucr_ldap2ox:
        for entry in ucr_ldap2ox.split():
          value, key = entry.split(':', 1)
          if value is None:
            command.append(f"--unset {changed_mapping_single.get(key, key)}")
          else:
            command.append(f"--set {changed_mapping_single.get(key, key)} {value}")

      if ucr_ldap2oxmulti:
        ldap2oxmulti = {}
        for entry in ucr_ldap2oxmulti.split():
          value, key = entry.split(':', 1)
          if value is None:
            for v in changed_mapping_multi.get(key, [key]):
              command.append(f"--unset {v}")
          else:
            for v in changed_mapping_multi.get(key, [key]):
              command.append(f"--set {v} {value}")

      if command:
        print("Run the following command on the ox-connector server to update attribute mapping:")
        print("python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py modify " + " ".join(command))
      else:
        print("Nothing to do.")
      EOF

#. Copy the generated command from the output.

#. On the Nubus for UCS system where the :program:`OX Connector` app runs,
   run the generated command.

#. Verify the migration result.
   Run the command in
   :numref:`conf-user-mapping-verify-migration-listing`
   and check that the expected Open-Xchange properties
   map to the expected UDM properties.

   .. code-block:: console
      :caption: Verify the migrated attribute mapping
      :name: conf-user-mapping-verify-migration-listing

      $ python3 \
         /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         dump
