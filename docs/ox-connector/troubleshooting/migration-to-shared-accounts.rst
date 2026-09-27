.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-troubleshooting-migration:

Troubleshoot migration from functional accounts to shared accounts
==================================================================

During the :ref:`migration of functional accounts to shared accounts <ox-connector-usage-shared-accounts-migration>`,
a network failure or another unexpected error can leave a shared account half-configured.
You might encounter one of the following states:

Functional account still exists
   The functional account is still present,
   and the shared account is partially configured.
   Rerun the script with the same parameters as before to retry the migration.

Functional account no longer exists
   The functional account no longer exists,
   so only the final migration step remains.
   The remaining step is to modify the email address of the shared account
   and remove the ``tmp_`` prefix.
   To remove the prefix,
   use either the *Management UI* or the :command:`udm` command.

   .. tab-set::

      .. tab-item:: Management UI

         .. dropdown:: Deployment — All: Nubus for UCS and Nubus for Kubernetes
            :color: info
            :icon: rocket

            This section applies to both deployments.

         Use the *Management UI* on Nubus for Kubernetes
         or in cases where you don't have access to the UDM command-line.
         Use the following steps:

         #. Sign in to the *Management UI*
            and navigate to the :external+uv-nubus-manual:ref:`nubus-domain-ldap`.

         #. Select the container for the shared accounts.
            The default container is :samp:`cn=shared_accounts,cn=open-xchange,{<ldap_base>}`.

         #. Open the affected shared account.

         #. Change the email address and remove the ``tmp_`` prefix.

         #. Click :guilabel:`Save`.

         Verify that the shared account uses the expected email address
         and no longer has the ``tmp_`` prefix.

      .. tab-item:: UDM command-line

         .. dropdown:: Deployment — Nubus for UCS
            :color: info
            :icon: rocket

            This section applies to the Nubus for UCS deployment.

         To remove the prefix with the :command:`udm` command in Nubus for UCS,
         run the command shown in :numref:`app-troubleshooting-migration-remove-prefix-listing`.
         Define the following parameters:

         :``SHARED_ACCOUNT``: The DN of the affected shared account,
            for example ``"cn=test,cn=shared_accounts,cn=open-xchange,$(ucr get ldap/base)"``
         :``EMAIL``: The email address of the shared account.

         After you ran the command,
         verify that the shared account uses the expected email address
         and no longer has the ``tmp_`` prefix.

         .. code-block:: console
            :caption: Remove the ``tmp_`` prefix from the email address of a shared account
            :name: app-troubleshooting-migration-remove-prefix-listing

            $ export SHARED_ACCOUNT="<DN of affected shared account>"
            $ export EMAIL="<email address of the shared account>"
            $ udm \
               oxmail/shared_account \
               modify \
               --dn "$SHARED_ACCOUNT" \
               --set mailPrimaryAddress="$EMAIL"
