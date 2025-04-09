.. SPDX-FileCopyrightText: 2021-2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _app-configuration:

*************
Configuration
*************

The following reference shows the available settings for the :program:`OX
Connector` app.

.. _settings:

App Settings
============

.. envvar:: OX_SOAP_SERVER

   Defines the server that has OX App Suite installed. Provide the protocol and
   the FQDN, for example :samp:`https://ox-app-suite.example.com`.

   :envvar:`OX_SOAP_SERVER` instructs the OX Connector app in the Docker
   container, where it must look for the OX App Suite system. The Docker
   container must resolve the FQDN.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - Yes
        - String
        - :samp:`https://{$hostname}.{$domainname}`

   For secure connections with HTTPS the Docker container needs to validate the
   certificate.

   .. note::

      .. index::
         single: certificate; self-signed
         single: certificate; custom
         see: installation; certificate

      If the OX App Suite instance uses a self-signed certificate or a
      certificate it can't validate, the OX Connector container needs the
      root certificate for validation.
      You need to store the self-signed certificate files in the
      :file:`/var/lib/univention-appcenter/apps/ox-connector/data/conf/ca-certificates/` directory.
      For details, see :ref:`additional-ca-certificates`.


.. envvar:: OX_IMAP_SERVER

   Defines the default IMAP server for new users, if not explicitly set at the user object.

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

   Defines the SMTP server for new users, if not explicitly set at the user
   object.

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

   Defines the default context for users. The OX Connector doesn't create the
   ``DEFAULT_CONTEXT`` automatically. You as administrator must ensure, the
   default context exists before the OX Connector provisions the first user. To
   create a context, see :ref:`usage-contexts`.

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

   Defines the default language for new users

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

   Defines the default timezone for new users

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

   Defines the user for the OX App Suite administrator user, also called *OX
   Admin user*. This user can create, modify, and delete contexts. The user must
   already exist. The administrator defines the username for the *OX Admin user*
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

   Defines the value that is used by OX to log in to the user's inbox.
   If this value is empty it is set to the user's mail address.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - String
        - N/A

   In cases where you use single sign-on,
   you need to append this variable with an asterisk
   and the mail server's master user.
   For Dovecot, the master user is ``*dovecotadmin``.
   In this case, you need to set ``OX_IMAP_LOGIN`` to ``'{}*dovecotadmin'``.
   The OX Connector interprets the curly braces as a template for the primary email address.
   You can add any user attribute inside the curly braces if needed, for example,
   ``{username}`` while empty braces are for ``primaryMailAddress``.


.. envvar:: OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE

   A template that defines the value which is used by OX to log in to the functional account inbox.
   If this value is empty it is set to a concatenation of the functional account LDAP entry UUID
   and the user LDAP uid.

   This template can include the functional account entry UUID (`fa_entry_uuid`), the functional
   account email address (`fa_email_address`) and any OX user UDM property (including the user's `entry_uuid` and `dn`).
   Every UDM property used in this template must be enclosed by ``{{ }}`` e.g ``{{fa_entry_uuid}}{{username}}``. Multiple values can
   optionally be separated by other text.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - String
        - N/A

   .. note::

        If the UCS OX App Suite is used, this app setting can be left empty, which is equivalent to using the
        value ``{{fa_entry_uuid}}{{username}}``.

        OX Connector installations that previously only used the functional account entry UUID should configure
        this app setting to ``{{fa_entry_uuid}}``.

        Some examples:

        .. code-block:: console

            "{{fa_entry_uuid}}::{{entry_uuid}}" # Functional account entry UUID and user UUID separated by two colons.
            "{{username}}+{{fa_entry_uuid}}+{{dn}}" # username, functional account entry UUID and user dn separated by a '+'
            "{{fa_email_address}}*dovecotadmin" # Concatenation of functional account's mail address and the string *\*dovecotadmin

   .. note::

        In cases where SSO is to be used, this variable has to be appended with an asterisk
        and the mail server's master user. For Dovecot this would be *\*dovecotadmin*. In this
        case ``OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE`` can be set to ``'{{fa_email_address}}*dovecotadmin'``.
        The resulting login value for the functional account would then look like this:

        .. code-block:: console

            myfunctional_account@maildomain.de*dovecotadmin


.. envvar:: OX_USER_IDENTIFIER

   Defines which UDM user property is used as the unique user identifier for OX. If this app setting is not set the :program:`OX Connector`
   will use the ``username`` property by default.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - String
        - N/A

   .. note::

         Only a UDM user property that contains a **single value** which is **not None** (mandatory UDM property) is a valid option. In case a UDM user property
         that contains an empty value or a list of values is specified, the :program:`OX Connector` will enter an error state which needs
         to be resolved manually by simply setting a valid value.


.. envvar:: OX_GROUP_IDENTIFIER

   Defines which UDM group property is used as the unique group identifier for OX. If this app setting is not set the :program:`OX Connector`
   will use the ``name`` property by default.

   .. list-table::
      :header-rows: 1
      :widths: 2 2 8

      * - Required
        - Type
        - Initial value

      * - No
        - String
        - N/A

   .. note::

         Only a UDM group property that contains a **single value** which is **not None** (mandatory UDM property) is a valid option. In case a UDM group property
         that contains an empty value or a list of values is specified, the :program:`OX Connector` will enter an error state which needs
         to be resolved manually by simply setting a valid value.

.. envvar:: OX_CONNECTOR_LOG_LEVEL

   Defines the log level for the ox-connector app. If this app setting is not set the :program:`OX Connector`
   will use ``INFO`` by default.

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
   Administrators then can set, modify, or delete deputy permissions for users in the UMC.

   For example, administrators can grant ``user01`` the roles *Viewer*, *Editor*, and *Author*
   for the calendar and mail module for ``user01``.
   Furthermore, ``user01`` can send emails on behalf of ``user02``.

   The default value is ``False``.
   To enable the feature,
   set the app setting :envvar:`OX_ENABLE_DEPUTY_PERMISSIONS` to ``True``.

   To see the feature in the UMC,
   you need to enable the UMC representation for the extended attribute
   either after the app installation,
   or after the configuration.
   Run the command in :numref:`settings-ox-enable-deputy-permission-listing`
   either on the *UCS Primary Directory Node*
   or a *UCS Backup Directory Node*.

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

      The *Deputy Permissions* feature requires OX App Suite version >= 8.

      Users can modify the deputy permissions on their own in :program:`OX App Suite`.
      The provisioning in the :program:`OX Connector` app through UCS overwrites these settings.

   .. seealso::

      `Deputy permissions : Technical Documentation <https://documentation.open-xchange.com/8/middleware/permissions_and_capabilities/deputy_permission.html>`_
         for more information about OX deputy permissions.

.. _ucr-variables:

|UCSUCRV|\ s
============

.. envvar:: ox/context/id

   The app setting :envvar:`DEFAULT_CONTEXT` sets the value of the |UCSUCRV|
   :envvar:`ox/context/id`.

   Upon installation of the app :program:`OX Connector`, the OX Connector
   creates the extended attribute ``oxContext`` and uses the value from
   :envvar:`ox/context/id` as initial value for the extended attribute
   ``oxContext``.

   When an administrator creates a new user account that the OX Connector
   synchronizes, UDM sets the OX context for the user account to value of the
   extended attribute ``oxContext``.

   .. caution::

      The UCR variable :envvar:`ox/context/id` **isn't** for manual usage.

      Changing the variable **doesn't** change the OX context on existing user
      accounts.

      Changing the value of the app setting :envvar:`DEFAULT_CONTEXT` does
      **neither** change :envvar:`ox/context/id` **nor** the extended attribute
      ``oxContext``.

.. _conf-user-attribute-mapping:

User attribute mapping
======================

.. versionadded:: 2.2.9

   Modify the mapping between *Open-Xchange* and *UDM* properties.

Since version 2.2.9, you can modify the mapping
between *Open-Xchange* and *UDM* properties
using the script :program:`change_attribute_mapping.py` provided with the app.
The script creates a JSON file
that stores information about the Open-Xchange properties
and other information useful for user provisioning.

Don't modify the file manually, but only with the script.
The JSON file locates at
:file:`/var/lib/univention-appcenter/apps/ox-connector/data/AttributeMapping.json`.
If the file doesn't exist,
the OX Connector uses the default mapping defined in
:file:`/usr/lib/python3.9/site-packages/univention/ox/provisioning/default_user_mapping.py`
inside the Docker container of the app.

.. program:: change_attribute_mapping.py

The script allows the following operations:

.. option:: modify

   performs operations that change the current mapping.

.. option:: restore_default

   restores the default mapping.

.. option:: dump

   writes the current JSON mapping to console.


With the *modify* operation, you can use the following additional operations:

.. option:: --set

   Changes the UDM property used for an Open-Xchange property provisioning.
   :numref:`conf-user-mapping-set-listing` shows how to set the mapping
   of the Open Xchange property ``userfield01`` to the UDM property ``description``.

   .. code-block:: console
      :caption: Sets the mapping of an Open-Xchange property to an UDM property.
      :name: conf-user-mapping-set-listing

      $ python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         modify \
         --set userfield01 description

   It's possible to use the :option:`--set` arguments multiple times in the same invocation.
   :numref:`conf-user-mapping-multiple-set-listing` shows an example
   that sets the mapping of the Open-Xchange properties ``userfield01`` and ``given_name``
   to the UDM properties ``description`` and ``custom_attribute``.

   .. code-block:: console
      :caption: Sets the mapping of multiple Open-Xchange properties to multiple UDM properties.
      :name: conf-user-mapping-multiple-set-listing

      $ python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         modify \
         --set userfield01 description \
         --set given_name custom_attribute

.. option:: --unset

   Removes the Open-Xchange property from the mapping
   if it isn't marked as required.
   You can use it to remove properties from the synchronization.

   .. code-block:: console
      :caption: Unset the OX property ``userfield01``.

      $ python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         modify \
         --unset userfield01

.. option:: --set_alternatives

   Sets alternative UDM properties used for the synchronization if the main one is ``None``.
   :numref:`conf-user-mapping-set-alternative-listing` shows an example
   to set the theoretical attributes ``CustomAttributeUserMail`` and ``CustomAttributeUserMail2``
   as alternatives to the Open-Xchange property ``email1``.

   .. code-block:: console
      :caption: Set theoretical attributes as alternatives to an Open-Xchange property.
      :name: conf-user-mapping-set-alternative-listing

      $ python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         modify \
         --set_alternatives email1 CustomAttributeUserMail CustomAttributeUserMail2

.. option:: unset_alternatives

   Unset the current alternatives for an OX property

   .. code-block:: console
      :caption: Unset the alternative attributes to the OX property ``email1``.

      $ python3 /var/lib/univention-appcenter/apps/ox-connector/data/resources/change_attribute_mapping.py \
         modify \
         --unset_alternatives email1

If you previously used the attribute mapping feature of the OX App Suite app from the App Center,
you can migrate it by running the following command
on the UCS system where you installed the OX App Suite.
You then use the output of the script as command and run it
on the UCS system where the OX Connector is running.

.. code-block:: python

   python3 <<EOF
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

.. _additional-ca-certificates:

Import additional CA certificates
=================================

.. versionadded:: 2.3.0

   Allow the connector to import additional CA certificates

The :program:`OX Connector` app in UCS runs as a container with its own CA certificate store.
By default, the app imports the UCS root CA certificate into the CA store
to enable a secure connection to the UCS LDAP directory.
You may need additional CA certificates for the :program:`OX Connector` app,
for example, when provisioning to a remote :program:`OX App Suite` installation.

To add certificates to the certificate store in the :program:`OX Connector`,
use the following steps on the system where the app is installed:

#. Create the
   :file:`/var/lib/univention-appcenter/apps/ox-connector/data/conf/ca-certificates/` directory.

#. Copy the CA certificate files in PEM format with the ending ``.pem`` into this directory.
   :numref:`additional-ca-certificates-examples-listing` shows an example.

   .. code-block:: console
      :caption: Examples for additional CA certificates
      :name: additional-ca-certificates-examples-listing


      $ file /var/lib/univention-appcenter/apps/ox-connector/data/conf/ca-certificates/*.pem
      .../ox-connector/data/conf/ca-certificates/cert1.pem: PEM certificate
      .../ox-connector/data/conf/ca-certificates/cert2.pem: PEM certificate

#. Manually reconfigure the OX Connector with the command in
   :numref:`additional-ca-certificates-manual-reconfigure-listing`.
   The :program:`OX Connector` app automatically adds the certificates to its certificate store,
   also during app updates.

   .. code-block:: console
      :caption: Manually reconfigure the OX Connector
      :name: additional-ca-certificates-manual-reconfigure-listing

      $ univention-app configure ox-connector
