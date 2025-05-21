.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _configure-ox-app-suite:

************************
Configure *OX App Suite*
************************

Describing how to configure *OX App Suite* for connection with Nubus for Kubernetes
is out of scope of this document.

If you want to use LDAP authentication,
you have to set the LDAP search user in *OX App Suite*
that you configured in the packaged integration
in :numref:`install-packaged-integration-helm-chart-values-listing`.

If you want to use single sign-on with OpenID Connect or SAML,
you need to create a suitable client in *Keycloak*,
the *Identity Provider* in Nubus for Kubernetes.

For particular details and necessary settings,
follow the Technical Documentation from Open-Xchange.

.. important::

   Univention doesn't provide support for the configuration *OX App Suite*.

.. seealso::

   `Technical Documentation - Open-Xchange <https://documentation.open-xchange.com/index.html>`_
      for the documentation for *OX App Suite*.
