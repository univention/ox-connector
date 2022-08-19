.. _app-configuration:

*************
Configuration
*************

The following reference shows the available settings for the :program:`OX
Connector` app.

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

