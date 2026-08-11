.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-ucs-additional-certificates:

Import additional CA certificates on UCS
========================================

The :program:`OX Connector` app on Nubus for UCS
runs in a container with its own CA store.
By default,
the app imports the Nubus for UCS root CA into this store.
This import enables a secure connection to the Nubus LDAP directory.
You might need additional CA certificates
when provisioning to a remote *OX App Suite* installation.

Before you start,
make sure that you meet the following prerequisites:

* You have installed the :program:`OX Connector` app.
* You have the CA certificate files in PEM format.

Use these steps on the system that runs the :program:`OX Connector` app:

#. Create the
   :file:`/var/lib/univention-appcenter/apps/ox-connector/data/conf/ca-certificates/` directory.

#. Copy the CA certificate files in PEM format to this directory.
   Use only files with the ``.pem`` filename extension.
   :numref:`additional-ca-certificates-examples-listing` shows an example.

   .. code-block:: console
      :caption: Examples of additional CA certificates
      :name: additional-ca-certificates-examples-listing

      $ file /var/lib/univention-appcenter/apps/ox-connector/data/conf/ca-certificates/*.pem
      .../ox-connector/data/conf/ca-certificates/cert1.pem: PEM certificate
      .../ox-connector/data/conf/ca-certificates/cert2.pem: PEM certificate

#. Run the command shown in
   :numref:`additional-ca-certificates-manual-reconfigure-listing`
   to reconfigure the :program:`OX Connector` app.
   The command finishes without errors
   and adds the certificates to the app's certificate store.
   During app updates,
   the app also imports the certificates from the directory.

   .. code-block:: console
      :caption: Manually reconfigure the OX Connector
      :name: additional-ca-certificates-manual-reconfigure-listing

      $ univention-app configure ox-connector
