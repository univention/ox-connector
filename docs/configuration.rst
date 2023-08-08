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
      certificate it can't validate, the OX Connector Docker container needs the
      root certificate for validation.

      For example, to add a custom certificate, run the following commands on
      the UCS system, where OX Connector is installed:

      .. code-block:: console

         $ univention-app shell ox-connector
         /oxp # wget --no-check-certificate \
           https://ox-app-suite.example.com/root-ca.crt \
           -O /usr/local/share/ca-certificates/ox-app-suite.crt
         /oxp # update-ca-certificates
         "WARNING: ca-certificates.crt does not contain exactly one certificate or CRL: skipping"

      Administrators can ignore the warning.


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

   .. note::

        In cases where SSO is to be used, this variable has to be appended with an asterisk
        and the mail server's master user. For Dovecot this would be *\*dovecotadmin*. In this
        case ``OX_IMAP_LOGIN`` can be set to ``'{}*dovecotadmin'``. The curly braces are used
        as a template for the primary mail address. The resulting `imaplogin` value would then
        look like this:

        .. code-block:: console

            myuser@maildomain.de*dovecotadmin


.. envvar:: OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE

   A template that defines the value which is used by OX to log in to the functional account inbox.
   If this value is empty it is set to a concatenation of the functional account LDAP entry UUID
   and the user LDAP uid.

   This template has to include the functional account entry UUID (`fa_entry_uuid`) and can additionally
   include any OX user UDM property (including the user's `entry_uuid` and `dn`). Every value used in this
   template must be enclosed by ``{{ }}`` e.g ``{{fa_entry_uuid}}{{username}}``. Multiple values can
   optionally be separated by any combination of the characters ``:;+``.

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

        OX-Connector installations that previously only used the functional account entry UUID should configure
        this app setting to ``{{fa_entry_uuid}}``.

        Some examples:

        .. code-block:: console

            "{{fa_entry_uuid}}::{{entry_uuid}}" # Functional account entry UUID and user UUID separated by two colons.
            "{{username}}+{{fa_entry_uuid}}+{{dn}}" # username, functional account entry UUID and user dn separated by a '+'


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
