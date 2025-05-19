.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _doc-entry:

************
Introduction
************

Welcome to the documentation for the *OX App Suite* packaged integration for Nubus for Kubernetes.

This document describes
how you can install the packaged integration for *OX App Suite*
to Nubus for Kubernetes.
A packaged integration is the way to extend Nubus for Kubernetes with plugins
in the *Directory Service*, the *Management UI*, and the *UMC Server*.
A packaged integration bundles the combination of different plugins.
Together with the packaged integration,
Nubus lets you manage users, groups, and resources for *OX App Suite* through the *Management UI*.
For more information,
see :external+uv-nubus-kubernetes-customization:ref:`nubus-packaged-integrations`
in :cite:t:`uv-nubus-kubernetes-customization`.

This document addresses operators who have installed Nubus for Kubernetes.
If you want to connect :program:`OX App Suite` to Nubus for Kubernetes
so that *OX App Suite* uses the user accounts from Nubus,
then this documentation is for you.

If you want to connect :program:`OX App Suite` with Nubus in the UCS appliance deployment,
refer to :external+uv-ox-connector-app:ref:`doc-entry`.

.. important::

   This documentation describes a **product preview** for packaged integrations in Nubus for Kubernetes.
   It shows by example how to install the packaged integration for *Open-Xchange*.

   Univention **doesn't** provide support for the packaged integration
   referred to in this document,
   nor the installation and configuration of *OX App Suite*.

This document assumes that you have knowledge of the following topics:

* Kubernetes, its concepts, and how to deploy, scale and manage applications.
* Helm and Helm Charts.

This document doesn't cover the installation and maintenance of a Kubernetes cluster,
the installation of Nubus for Kubernetes,
the installation of *OX App Suite*,
and the configuration of LDAP for *OX App Suite*.
However, it provides links to respective documentation
and value references for the configuration.

The document has the following structure:

#. :ref:`install-packaged-integration` provides steps and configuration guidance.
#. :ref:`install-ox-app-suite` provides links to resources about the installation on Kubernetes.
#. :ref:`configure-ox-app-suite` provides a configuration reference for LDAP in *OX App Suite*.

For further documentation for Univention Nubus for Kubernetes,
see :external+uv-navigation:ref:`page-nubus`.

You find a summary of the changes in the :ref:`document's changelog section <changelog>`.

Your feedback on this documentation is welcome and highly appreciated.
If you have any comments, suggestions, or criticisms,
please
`submit your feedback <https://www.univention.com/feedback/?packaged-integration-open-xchange=generic>`_
to improve the document.
