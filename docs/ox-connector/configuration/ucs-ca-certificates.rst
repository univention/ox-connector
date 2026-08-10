.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-ucs-additional-certificates:

Import additional CA certificates on UCS
========================================

The :program:`OX Connector` app in UCS runs as a container with its own CA certificate store.
By default, the app imports the UCS root CA certificate into the CA store
to enable a secure connection to the UCS LDAP directory.
You may need additional CA certificates for the :program:`OX Connector` app,
for example, when provisioning to a remote *OX App Suite* installation.

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
