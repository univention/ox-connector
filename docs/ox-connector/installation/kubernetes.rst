.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-install-on-kubernetes:

Install on Nubus for Kubernetes
===============================

Provisioning sends selected directory objects
from the *Directory Service* in Nubus
to a remote *OX App Suite* installation.
These objects include user accounts, user groups, and resources.

The *OX Consumer* sends this data through the *OX SOAP API*.
For example, users created in Nubus appear
in the *OX App Suite* address book.
Users can also book synchronized resources, such as meeting rooms,
in *OX App Suite*.

For Nubus for Kubernetes,
the *OX Consumer* provides the same functionality for *OX App Suite*
as the *OX Connector app* provides for the Nubus for UCS appliance.
Both use the same business logic.

Before you start,
make sure that your environment meets the Kubernetes prerequisites.
For details,
see :ref:`prerequisites-kubernetes`.

This page covers the following tasks:

#. :ref:`ox-connector-install-on-kubernetes-prepare-app-suite`
#. :ref:`ox-connector-install-on-kubernetes-install-packaged-integration`
#. :ref:`ox-connector-install-on-kubernetes-create-subscription`
#. :ref:`ox-connector-install-on-kubernetes-prepare-ox-consumer`
#. :ref:`ox-connector-install-on-kubernetes-install-ox-consumer`

.. _ox-connector-install-on-kubernetes-prepare-app-suite:

Prepare OX App Suite
--------------------

If you don't have an *OX App Suite* installation,
install it before you continue.
Installing *OX App Suite* is beyond the scope of this manual.
For installation resources,
see the following links:

`OX App Suite 8 Operations Guide <https://documentation.open-xchange.com/appsuite/operation-guides/>`_
   for information about the deployment of OX App Suite 8.

`OX App Suite 7 <https://wiki.open-xchange.com/wiki/index.php?title=AppSuite:Main_Page_AppSuite>`_
   for information about the installation of OX App Suite 7.

.. important::

   Univention doesn't provide support for the installation of *OX App Suite*.

.. _ox-connector-install-on-kubernetes-install-packaged-integration:

Install the packaged integration
--------------------------------

This section shows how to install the packaged integration
for *OX App Suite* in Nubus for Kubernetes.
It adds these customizations to Nubus:

* A Nubus *Portal* tile for the *OX App Suite* instance.
* Management capabilities in the *Management UI*
  for the following *OX App Suite* objects:

  * Access profiles
  * Functional accounts
  * OX contexts
  * OX resources
  * User access to *OX App Suite*
  * User groups

For details,
see :external+uv-nubus-customization:ref:`nubus-packaged-integrations-load`
in :cite:t:`uv-nubus-customization`.

Before you continue,
make sure that you know the container image registry
and repository name for the packaged integration.
For details,
see :ref:`prerequisites-kubernetes`.

To install the packaged integration,
follow these steps:

#. Copy the content from :download:`nubus-values.yaml`
   to the :file:`custom_values.yaml` file
   for your Nubus for Kubernetes installation.
   :numref:`ox-connector-kubernetes-packaged-integration-values-listing`
   shows the Helm Chart values to add.

   ``oxDefaultContext``
      Define the number of the first and default context in *OX App Suite*.
      You can define the value as an integer,
      for example ``10``,
      or as a string,
      for example ``"10"``.

   ``oxSystemUserPassword``
      Choose a secure password.
      Use the same password later when you set up LDAP in *Open-Xchange*.

   ``portalOxLinkBase``
      Define the base URL of your *OX App Suite* instance.
      You get this URL after you install *OX App Suite*.
      See :ref:`ox-connector-install-on-kubernetes-prepare-app-suite`.

   To choose an appropriate version number for the packaged integration
   in the ``tag`` attribute,
   see the `tags <https://github.com/univention/ox-connector/tags>`_
   in the repository.

   .. literalinclude:: nubus-values.yaml
      :language: yaml
      :emphasize-lines: 10,15-17
      :caption: Helm Chart values for adding the *Open-Xchange* packaged integration
      :name: ox-connector-kubernetes-packaged-integration-values-listing

#. Apply the changes with Helm.
   Use the command in :numref:`ox-connector-kubernetes-packaged-integration-helm-listing`.

   Before you run it,
   replace these placeholders:

   * ``<NAMESPACE>``: Kubernetes namespace of your Nubus installation.
   * ``<NUBUS_RELEASE_NAME>``: Helm Chart release name of your Nubus installation.
   * ``<NUBUS_VERSION>``: Nubus Helm Chart version to install.

   .. code-block:: console
      :caption: Install the *Open-Xchange* packaged integration
      :name: ox-connector-kubernetes-packaged-integration-helm-listing

      $ export NAMESPACE_FOR_NUBUS="<NAMESPACE>"
      $ export RELEASE_NAME="<NUBUS_RELEASE_NAME>"
      $ export VERSION="<NUBUS_VERSION>"

      $ helm upgrade \
         "$RELEASE_NAME" \
         --namespace="$NAMESPACE_FOR_NUBUS" \
         oci://artifacts.software-univention.de/nubus/charts/nubus \
         --values custom_values.yaml \
         --version "$VERSION"

#. Verify that the Helm upgrade completes successfully
   and that the packaged integration is available in Nubus for Kubernetes.

.. _ox-connector-install-on-kubernetes-create-subscription:

Create a Provisioning API subscription
--------------------------------------

Create the subscription before the *OX Consumer* connects
to the *Provisioning Service*.

The subscription gives the *OX Consumer* access to the *Provisioning API*.
The *Provisioning Service* sends directory object updates.
It also provides the data that you want to provision.

For *OX App Suite*,
the relevant directory objects are user accounts, user groups, and Open-Xchange resources.
Examples include meeting rooms and functional mailboxes.

To create the *OX Consumer* subscription,
follow these steps:

#. Make sure that your local client can reach the *Provisioning API*.

   If you run the commands outside the cluster,
   create temporary port forwarding.
   Use the command in :numref:`ox-connector-kubernetes-provisioning-api-port-forward-listing`.
   Keep it running while you create the subscription.

   .. code-block:: console
      :caption: Forward the *Provisioning API* to your local client
      :name: ox-connector-kubernetes-provisioning-api-port-forward-listing

      $ export LOCAL_PORT=7777
      $ kubectl \
         --namespace "$NAMESPACE_FOR_NUBUS" \
         port-forward \
         services/"$RELEASE_NAME"-provisioning-api \
         "$LOCAL_PORT":80

#. Get the password for the *Provisioning API* administrator
   with the command in :numref:`ox-connector-kubernetes-provisioning-api-admin-password-listing`.

   .. caution::

      Environment variables can expose passwords
      in shell history, debug output, or process environments.
      Use this method only on a trusted system.

   .. code-block:: console
      :caption: Retrieve the administrative password for the *Provisioning API*
      :name: ox-connector-kubernetes-provisioning-api-admin-password-listing

      $ export BASE_URL="http://localhost:7777"
      $ export USERNAME="admin"
      $ export PASSWORD="$(kubectl \
         --namespace "$NAMESPACE_FOR_NUBUS" \
         get secret \
         nubus-provisioning-api-admin \
         -o json \
         | jq -r ".data.password" \
         | base64 -d)"

#. Create the :download:`provisioning-api.json` configuration file
   for the *OX Consumer*.
   Use the content in :numref:`ox-connector-kubernetes-subscription-listing`.

   Set ``password`` to any value.
   Use the ``name`` and ``password`` values later
   for the *OX Consumer* configuration.

   .. literalinclude:: provisioning-api.json
      :language: json
      :caption: Subscription configuration for the *OX Consumer*
      :name: ox-connector-kubernetes-subscription-listing
      :emphasize-lines: 2,30

#. Send the subscription file to the *Provisioning API*
   with the command in :numref:`ox-connector-kubernetes-create-subscription-listing`.

   .. code-block:: console
      :caption: Create the subscription for the *OX Consumer*
      :name: ox-connector-kubernetes-create-subscription-listing

      $ curl \
         --user "$USERNAME":"$PASSWORD" \
         --request POST \
         "$BASE_URL"/v1/subscriptions \
         --header "Accept: application/json" \
         --header "Content-Type: application/json" \
         --data @provisioning-api.json

#. Verify that the subscription exists
   with the command in :numref:`ox-connector-kubernetes-list-subscriptions-listing`.

   .. code-block:: console
      :caption: Retrieve the list of subscriptions
      :name: ox-connector-kubernetes-list-subscriptions-listing

      $ curl \
         --user "$USERNAME":"$PASSWORD" \
         --request GET \
         "$BASE_URL"/v1/subscriptions \
         --header "Accept: application/json"

#. If you created a temporary port forward,
   stop the :command:`kubectl port-forward` command
   in :numref:`ox-connector-kubernetes-provisioning-api-port-forward-listing`
   after you verify that the subscription exists.

.. seealso::

   :external+uv-nubus-customization:ref:`customization-api-provisioning-subscription`
      in :cite:t:`uv-nubus-customization`
      for information about how to create a subscription in the *Provisioning Service*
      using the *Provisioning API*.

.. _ox-connector-install-on-kubernetes-prepare-ox-consumer:

Prepare the OX Consumer configuration
-------------------------------------

Prepare the configuration **before** you install the *OX Consumer*
in a Kubernetes cluster.
For the installation step,
see :ref:`ox-connector-install-on-kubernetes-install-ox-consumer`.
The configuration defines the data source, the *Provisioning API*,
and the data target, your *OX App Suite* instance.

To prepare the *OX Consumer* configuration,
follow these steps:

#. Create the :download:`ox-consumer-values.yaml` values file
   with the structure in :numref:`ox-consumer-kubernetes-values-listing`.

   .. literalinclude:: ox-consumer-values.yaml
      :language: yaml
      :caption: Configuration for the *OX Consumer* in the values file
      :name: ox-consumer-kubernetes-values-listing

#. Set the required values for the following settings.

   For optional settings and their default values,
   see :ref:`ox-connector-configuration-kubernetes`.

   Section :ref:`helm-ref-openxchange`
      :envvar:`openXchange.domainName`: The OX mail domain that the connector uses to generate email addresses.

      :envvar:`openXchange.auth.password`: :envvar:`OX_MASTER_PASSWORD`

      :envvar:`openXchange.oxSmtpServer`: :envvar:`OX_SMTP_SERVER`

      :envvar:`openXchange.oxImapServer`: :envvar:`OX_IMAP_SERVER`

      :envvar:`openXchange.oxSoapServer`: :envvar:`OX_SOAP_SERVER`

      :envvar:`openXchange.oxDbConnectionString`: The SQLAlchemy connection string for the database.

      The connection string uses the following pattern::

         postgresql+psycopg2://<DATABASE_USERNAME>:<PASSWORD>@<HOSTNAME>/<DATABASE_NAME>

      Replace ``<DATABASE_USERNAME>``,
      ``<PASSWORD>``,
      ``<HOSTNAME>``,
      and ``<DATABASE_NAME>`` with the values for your database connection.

   Section :ref:`helm-ref-provisioningapi`
      :envvar:`provisioningApi.auth.username`:
      The value of the ``name`` attribute in :numref:`ox-connector-kubernetes-subscription-listing`.

      :envvar:`provisioningApi.auth.password`:
      The value of the ``password`` attribute in :numref:`ox-connector-kubernetes-subscription-listing`.

      :envvar:`provisioningApi.connection.baseUrl`:
      The base URL for the *Provisioning API* in the *Provisioning Service*.

      The URL points to the Kubernetes service for the *Provisioning API*.

      Use the following URL format:
         :samp:`http://{release-name}-provisioning-api`

         Replace :samp:`{release-name}` with the Helm Chart release name
         of your Nubus for Kubernetes installation.

      :envvar:`provisioningApi.resync.auth.password`:
      The password for the administrative user
      of the *Provisioning API*.
      Use this setting if you leave :envvar:`provisioningApi.resync.enabled` set to ``true``.

      .. important::

         Nubus for Kubernetes doesn't expose the *Provisioning API* outside the cluster
         for security reasons.

      .. tip::

         **Using existing Kubernetes secrets**

         Instead of specifying passwords directly in the values file,
         you can use existing Kubernetes secrets.
         Set ``openXchange.auth.existingSecret.*``,
         ``provisioningApi.auth.existingSecret.*``,
         and ``provisioningApi.resync.auth.existingSecret.*``
         to the names of the secrets that contain the credentials.

         When you use existing secrets,
         the *OX Consumer* ignores the inline ``password`` values.

.. seealso::

   `README file for the OX Consumer <https://github.com/univention/ox-connector/blob/ucs5.2/helm/ox-connector/README.md>`_
      for information about the available Helm Chart values and their default settings.

   :external+uv-nubus-customization:ref:`customization-api-provisioning-endpoint-access`
      in :cite:t:`uv-nubus-customization`
      for information about how to access the *Provisioning API*
      inside the Kubernetes cluster.

   `Engine Configuration - SQLAlchemy 2.0 Documentation <https://docs.sqlalchemy.org/en/20/core/engines.html#postgresql>`_
      for information about the configuration of database connections.

.. _ox-connector-install-on-kubernetes-install-ox-consumer:

Install the OX Consumer
-----------------------

To install the *OX Consumer* with the configuration in
:ref:`ox-connector-install-on-kubernetes-prepare-ox-consumer`,
follow these steps:

#. Select an *OX Consumer* version
   from the `OX Connector repository tags <https://github.com/univention/ox-connector/tags>`_.

#. Replace the following placeholders
   in :numref:`ox-consumer-helm-installation-listing`:

   * ``<NAMESPACE>``: Kubernetes namespace for the *OX Consumer*.
   * ``<OX_CONSUMER_RELEASE_NAME>``: Helm Chart release name for the *OX Consumer*.
   * ``<OX_CONSUMER_VERSION>``: OX Consumer Helm Chart version to install.

   .. danger::

      Use a different Helm release name for the *OX Consumer*.
      Don't reuse the Nubus release name.
      If both releases use the same name in the same namespace,
      Helm can delete the existing Nubus for Kubernetes installation.

#. Install the *OX Consumer*
   with the command in :numref:`ox-consumer-helm-installation-listing`.

   .. code-block:: console
      :caption: Install the *OX Consumer* with Helm
      :name: ox-consumer-helm-installation-listing

      $ export NAMESPACE_FOR_CONSUMER="<NAMESPACE>"
      $ export RELEASE_NAME="<OX_CONSUMER_RELEASE_NAME>"
      $ export VERSION="<OX_CONSUMER_VERSION>"

      $ helm upgrade \
         "$RELEASE_NAME" \
         --namespace "$NAMESPACE_FOR_CONSUMER" \
         --install \
         oci://artifacts.software-univention.de/nubus/charts/ox-connector \
         --values ox-consumer-values.yaml \
         --version "$VERSION"

#. Verify that the Helm release installs successfully
   and that the *OX Consumer* workloads are ready.
