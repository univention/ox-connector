.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-install-on-kubernetes:

Install on Nubus for Kubernetes
===============================

.. _ox-connector-install-on-kubernetes-before-start:

Before you start
----------------

.. _ox-connector-install-on-kubernetes-prepare-app-suite:

Prepare OX App Suite
--------------------

This section only applies to you,
if you don't have an *OX App Suite* installation yet.

How to install *OX App Suite* is beyond the scope of this document.
For resources, refer to the following *see also* box.

.. important::

   Univention doesn't provide support for the installation of *OX App Suite*.

.. seealso::

   `OX App Suite product information <https://www.open-xchange.com/products/ox-app-suite>`_
      for general information about the product.

   `OX App Suite 8 Operations Guide <https://documentation.open-xchange.com/appsuite/operation-guides/>`_
      for information about the deployment of OX App Suite 8.

   `OX App Suite 7 <https://oxpedia.org/wiki/index.php?title=AppSuite:Main_Page_AppSuite>`_
      for information about installation of OX App Suite 7.

.. _ox-connector-install-on-kubernetes-install-packaged-integration:

Install the packaged integration
--------------------------------

This section describes how an operator installs the packaged integration for *OX App Suite*
to Nubus for Kubernetes.
The packaged integration for *OX App Suite* installs the following customizations to Nubus:

* A tile in the Nubus *Portal* that links to the *OX App Suite* instance.
* Management capability in the *Management UI* for the following objects of *OX App Suite*:

  * Access profile
  * Functional accounts
  * OX Context
  * OX Resources
  * Select user accounts in Nubus for access to *OX App Suite*
  * Organize users in groups

For more information about loading packaged integrations,
see :external+uv-nubus-customization:ref:`nubus-packaged-integrations-load`
in :cite:t:`uv-nubus-customization`.

Before you begin,
you need to the location and name of the container image from the software developer,
or responsible entity of the packaged integration.
The example uses the following values:

:Registry: ``artifacts.software-univention.de``
:Repository: ``nubus/images/ox-extension``

To install the packaged integration to your Nubus for Kubernetes installation,
use the following steps:

#. Add the content from :download:`nubus-values.yaml`
   to the :file:`custom_values.yaml` values file of your Nubus for Kubernetes installation.
   :numref:`install-packaged-integration-helm-chart-values-listing`
   shows the Helm Chart values of that file.
   You **must** define values for the following variables here:

   ``oxDefaultContext``
      You must define the number of the context as integer value,
      for the first and default context in *OX App Suite*.
      You can define the value as number,
      for example ``10``, or as string, for example ``"10"``.

   ``oxSystemUserPassword``
      You can pick any secure password and use it later to set up LDAP in *Open-Xchange*.

   ``portalOxLinkBase``
      It's the URL to your *OX App Suite* instance.
      You have it after you installed *OX App Suite*.
      See :ref:`ox-connector-install-on-kubernetes-prepare-app-suite`.

   To pick an appropriate version number for the packaged integration
   in the ``tag`` attribute,
   see the `tags <https://github.com/univention/ox-connector/tags>`_
   and the `changelog <https://github.com/univention/ox-connector/blob/ucs5.2/CHANGELOG.md>`_
   in the repository.

   .. literalinclude:: nubus-values.yaml
      :language: yaml
      :emphasize-lines: 10,15-17
      :caption: Helm Chart values for adding the *Open-Xchange* packaged integration
      :name: install-packaged-integration-helm-chart-values-listing

#. To apply the changes to your Nubus for Kubernetes installation,
   run the commands in
   :numref:`install-packaged-integration-apply-listing`

   .. code-block:: console
      :caption: Install the *Open-Xchange* packaged integration
      :name: install-packaged-integration-apply-listing

      $ export NAMESPACE_FOR_NUBUS="Set to your Kubernetes namespace"
      $ export RELEASE_NAME="The Helm Chart release name"
      $ export VERSION="Your version of Nubus"
      $ helm upgrade \
         "$RELEASE_NAME" \
         --namespace="$NAMESPACE_FOR_NUBUS" \
         oci://artifacts.software-univention.de/nubus/charts/nubus \
         --values custom_values.yaml \
         --version "$VERSION"

.. _ox-connector-install-on-kubernetes-user-provisioning:

Set up user provisioning
------------------------

User provisioning is the unidirectional synchronization of selected directory objects,
such as user accounts, user groups, and resources,
from the *Directory Service* in Nubus
to a remote *OX App Suite* installation through the *OX SOAP API*.
The *OX Consumer* is the responsible component.
In particular, the *OX Consumer* enables
users created in Nubus to appear in the *OX App Suite*'s address book,
and resources, such as meeting rooms, created in Nubus
so that users can book them in *OX App Suite*.
The *OX Consumer* provides the same functionality
to *OX App Suite* in connection with Nubus for Kubernetes,
as the *OX Connector app* provides to *OX App Suite* in connection with the UCS appliance.
Both use the same business logic.

This section addresses operators
and describes how to install and configure the *OX Consumer*
in the same Kubernetes cluster as Nubus using Helm.

.. important::

   The *OX Consumer* **requires**
   the packaged integration for the *OX App Suite*
   which installs the necessary LDAP schema to the *Directory Service*,
   and customizations to the *Management UI* in Nubus
   for the management of user accounts, user groups, and resources.

   For information about installing the packaged integration,
   see :ref:`ox-connector-install-on-kubernetes-install-packaged-integration`.

.. _ox-connector-install-on-kubernetes-create-subscription:

Create a Provisioning API subscription
--------------------------------------

Before the *OX Consumer* can use the *Provisioning Service* in Nubus for Kubernetes,
you must create a subscription
that provides access to the Provisioning API.
The *Provisioning Service* notifies interested services about updates to directory objects.
It's the source for the data that you want to provision.
In the case of *OX App Suite*,
the directory objects of interest are user accounts, user groups, and resources such as meeting rooms and functional mailboxes related to Open-Xchange.

To create a subscription for the *OX Consumer*,
use the following steps:

#. Read the example in :external+uv-nubus-customization:ref:`customization-api-provisioning-subscription`
   in :cite:t:`uv-nubus-customization`.
   The section describes the steps for the subscription configuration.
   It also contains information about the parameter constraints, such as naming conventions.

#. Create a text file in JSON format
   for the subscription configuration
   with the filename :download:`provisioning-api.json`
   for the *OX Consumer*
   with the content in :numref:`user-provisioning-subscription-listing`.

   You can define any value for the ``password``.
   The credentials for the *OX Consumer* are the ``name`` and the ``password``.

   .. literalinclude:: provisioning-api.json
      :language: json
      :caption: Subscription configuration for the *OX Consumer*
      :name: user-provisioning-subscription-listing
      :emphasize-lines: 2,30

#. Create the subscription by following the steps outlined in
   :external+uv-nubus-customization:ref:`customization-api-provisioning-subscription`.

.. seealso::

   :external+uv-nubus-customization:ref:`customization-api-provisioning-subscription`
      in :cite:t:`uv-nubus-customization`
      for information about how to create a subscription in the *Provisioning Service*
      using the *Provisioning API*.

.. _ox-connector-install-on-kubernetes-prepare-ox-consumer:

Prepare the OX Consumer configuration
-------------------------------------

Before you can install the *OX Consumer* in a Kubernetes cluster,
you need to prepare the configuration.
The configuration defines the location of the data source, the *Provisioning API*,
and the data target, your *OX App Suite instance*.

To prepare the configuration for the *OX Consumer*,
use the following steps:

#. Create the :download:`ox-consumer-values.yaml` values file
   with the structure in :numref:`install-consumer-values-listing`.

   .. literalinclude:: ox-consumer-values.yaml
      :language: yaml
      :caption: Configuration for *OX Consumer* in values file
      :name: install-consumer-values-listing

#. Fill in the mandatory values for the following settings.

   For the optional settings with their default values,
   see `README file of the OX Consumer <https://github.com/univention/ox-connector/blob/ucs5.2/helm/ox-connector/README.md>`_.

   Section ``openXchange``
      For information about their meaning,
      see the references to :cite:t:`uv-ox-connector-app`.

      :``domainName``: OX mail to domain to generate email addresses.
      :``auth.password``: :envvar:`OX_MASTER_PASSWORD`
      :``oxSmtpServer``: :envvar:`OX_SMTP_SERVER`
      :``oxImapServer``: :envvar:`OX_IMAP_SERVER`
      :``oxSoapServer``: :envvar:`OX_SOAP_SERVER`
      :``oxDbConnectionString``: The SQLAlchemy connection string to the database.

      | The connection string uses the pattern:
      | :samp:`postgresql+psycopg2://{<database_username>}:{<password>}@{<hostname>}/{<database_name>}`.
      | Replace the fields with the respective values for your database connection.

   Section ``provisioningApi``
      :``auth.username``: The value from the ``name`` attribute in :numref:`user-provisioning-subscription-listing`.

      :``auth.password``: The value from the ``password`` attribute in :numref:`user-provisioning-subscription-listing`.

      :``connection.baseUrl``: The base URL to the *Provisioning API* in the *Provisioning Service*.

      The URL points to the Kubernetes service for the *Provisioning API*.

      Example:
         :samp:`http://{release-name}-provisioning-api`

         Replace :samp:`{release-name}` with the value
         that you use in your Helm command in :numref:`user-provisioning-helm-listing`.

      .. important::

         Nubus for Kubernetes doesn't expose the *Provisioning API* to the outside of the cluster
         for security reasons.

   .. tip::

      **Using existing Kubernetes secrets**

      Instead of specifying passwords directly in the values file,
      you can reference existing Kubernetes secrets.
      Use ``openXchange.auth.existingSecret`` and ``provisioningApi.auth.existingSecret``
      to reference pre-created secrets containing the credentials.

      When using existing secrets, the inline ``password`` values are ignored.

.. seealso::

   `README file of the OX Consumer <https://github.com/univention/ox-connector/blob/ucs5.2/helm/ox-connector/README.md>`_
      for information about the available Helm Chart values and their default settings.

   :external+uv-nubus-customization:ref:`customization-api-provisioning-endpoint-access`
      in :cite:t:`uv-nubus-customization`
      for information about how to access the *Provisioning API*
      where it locates.

   `Engine Configuration - SQLAlchemy 2.0 Documentation <https://docs.sqlalchemy.org/en/20/core/engines.html#postgresql>`_
      for information about the configuration of database connections.

.. _ox-connector-install-on-kubernetes-install-ox-consumer:

Install the OX Consumer
-----------------------

To install *OX Consumer* with the configuration in :ref:`user-provisioning-configuration`,
use the command in :numref:`user-provisioning-helm-listing`.
For the version of the *OX Consumer*,
look at the
`tags in project repository <https://github.com/univention/ox-connector/tags>`_.

.. important::

   For :numref:`user-provisioning-helm-listing`,
   select a different value for ``RELEASE_NAME``
   than you did for your Nubus for Kubernetes installation.
   Otherwise, Helm deletes your existing Nubus for Kubernetes installation
   if you install the *OX Consumer* in the same namespace.

.. code-block:: console
   :caption: Install the *OX Consumer* through Helm
   :name: user-provisioning-helm-listing

   $ export NAMESPACE_FOR_CONSUMER="Set to your Kubernetes namespace"
   $ export RELEASE_NAME="The Helm Chart release name"
   $ export VERSION="Your version of the OX Consumer"

   $ helm upgrade \
      "$RELEASE_NAME" \
      --namespace "$NAMESPACE_FOR_CONSUMER" \
      --install \
      oci://artifacts.software-univention.de/nubus/charts/ox-connector \
      --values ox-consumer-values.yaml \
      --version "$VERSION"
