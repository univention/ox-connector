.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _install-packaged-integration:

****************************
Install packaged integration
****************************

This section describes how an operator installs the packaged integration for *OX App Suite*
to Nubus for Kubernetes.
For more information about loading packaged integrations,
see :external+uv-nubus-kubernetes-customization:ref:`nubus-packaged-integrations-load`
in :cite:t:`uv-nubus-kubernetes-customization`.

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
      You must define the name for the first and default context in *OX App Suite*.

   ``oxSystemUserPassword``
      You can pick any secure password and use it later to set up LDAP in *Open-Xchange*.

   ``portalOxLinkBase``
      It's the URL to your *OX App Suite* instance.
      You have it after you installed *OX App Suite*.
      See :ref:`install-ox-app-suite`.

   To pick an appropriate version number for the packaged integration
   in the ``tag`` attribute,
   see the `tags <https://github.com/univention/ox-connector/tags>`_
   and the `changelog <https://github.com/univention/ox-connector/blob/ucs5.0/CHANGELOG.md>`_
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
