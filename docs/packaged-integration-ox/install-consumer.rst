.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _user-provisioning:

*****************
User provisioning
*****************

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
   see :ref:`install-packaged-integration`.

This section guides you through the setup of the *OX Consumer*:

#. :ref:`user-provisioning-subscription`
#. :ref:`user-provisioning-configuration`
#. :ref:`user-provisioning-installation`

.. _user-provisioning-subscription:

Create subscription
===================

Before the *OX Consumer* can use the *Provisioning Service* in Nubus for Kubernetes,
you must create a subscription
that provides access to the Provisioning API.
The *Provisioning Service* notifies interested services about updates to directory objects.
It's the source for the data that you want to provision.
In the case of *OX App Suite*,
the directory objects of interest are user accounts, user groups, and resources such as meeting rooms and functional mailboxes related to Open-Xchange.

To create a subscription for the *OX Consumer*,
use the following steps:

#. Read the example in :external+uv-nubus-kubernetes-customization:ref:`customization-api-provisioning-subscription`
   in :cite:t:`uv-nubus-kubernetes-customization`.
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
   :external+uv-nubus-kubernetes-customization:ref:`customization-api-provisioning-subscription`.

.. seealso::

   :external+uv-nubus-kubernetes-customization:ref:`customization-api-provisioning-subscription`
      in :cite:t:`uv-nubus-kubernetes-customization`
      for information about how to create a subscription in the *Provisioning Service*
      using the *Provisioning API*.

.. _user-provisioning-configuration:

Prepare configuration
=====================

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
   see `README file of the OX Consumer <https://github.com/univention/ox-connector/blob/ucs5.0/helm/ox-connector/README.md>`_.

   Section ``oxConnector``
      For information about their meaning,
      see the references to :cite:t:`uv-ox-connector-app`.

      :``domainName``: OX mail to domain to generate email addresses.
      :``oxMasterPassword``: :external+uv-ox-connector-app:envvar:`OX_MASTER_PASSWORD`
      :``oxSmtpServer``: :external+uv-ox-connector-app:envvar:`OX_SMTP_SERVER`
      :``oxImapServer``: :external+uv-ox-connector-app:envvar:`OX_IMAP_SERVER`
      :``oxSoapServer``: :external+uv-ox-connector-app:envvar:`OX_SOAP_SERVER`

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

.. seealso::

   `README file of the OX Consumer <https://github.com/univention/ox-connector/blob/ucs5.0/helm/ox-connector/README.md>`_
      for information about the available Helm Chart values and their default settings.

   :external+uv-nubus-kubernetes-customization:ref:`customization-api-provisioning-endpoint-access`
      in :cite:t:`uv-nubus-kubernetes-customization`
      for information about how to access the *Provisioning API*
      where it locates.

.. _user-provisioning-installation:

Install consumer
================

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
