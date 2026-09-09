.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-architecture-kubernetes:

************************
For Nubus for Kubernetes
************************

The :program:`OX Connector` provisions selected identity data from Nubus for Kubernetes
into OX App Suite.
It receives directory changes through the Provisioning API
and sends create, update, and delete requests to the OX App Suite SOAP API.

.. _ox-connector-architecture-kubernetes-overview:

Overview
========

The :program:`OX Connector` runs as an OX Consumer in the Kubernetes cluster.
The consumer receives changes to selected Univention Directory Manager (UDM) modules
from the Provisioning Service.
It processes the changes and provisions the corresponding OX App Suite objects.
:numref:`ox-connector-architecture-kubernetes-components-figure`
shows the components and their boundaries.

.. _ox-connector-architecture-kubernetes-components-figure:

.. figure:: /images/OX_Connector_Architecture_Kubernetes_components.*
   :target: ../_images/OX_Connector_Architecture_Kubernetes_components.svg
   :alt: Nubus for Kubernetes components that provision directory data to OX App Suite through the OX Connector.

   OX Connector components for Nubus for Kubernetes

   The diagram shows identity data flowing from the
   *Identity Store and Directory Service* through *Directory Manager*,
   *Provisioning Service*, *Provisioning API*, and the *OX Consumer*
   to *OX App Suite*.

   .. dropdown:: Information about architecture notation
      :color: info
      :icon: info

      This page uses the *ArchiMate®* enterprise architecture modeling notation
      to visualize the OX Connector architecture.
      For more information,
      see :external+uv-ucs-architecture:ref:`architecture-notation-archimate`
      in :cite:t:`uv-ucs-architecture`.

      *ArchiMate®* is a registered trademark of The Open Group.
      The diagrams are independently created by Univention GmbH
      and aren't endorsed or certified by The Open Group.

.. glossary::

   OX Consumer
      The *OX Consumer* is the OX Connector component that receives provisioning messages,
      stores work in the connector database, and provisions OX App Suite objects.

   Subscription
      A *subscription* defines the Provisioning Service topics
      for which the OX Consumer receives messages.

   PostgreSQL DB: OX Connector
      The :term:`OX Connector Provisioning Consumer` requires a PostgreSQL database
      for the task queue and object state.
      It helps the connector to keep up on the objects in case of synchronization errors.
      The database isn't part of the OX Connector deployment.

Besides the listed components,
the architecture contains the following ones, described separately
in the architecture overview for Nubus for UCS.
They have the same functionality in both deployments:

* :term:`Identity Store and Directory Service`
* :term:`Provisioning Service`
* :term:`Provisioning API`
* :term:`SOAP API`
* :term:`OX App Suite`

.. _ox-connector-architecture-kubernetes-deployment:

Deployment
==========

You deploy the OX Connector as a Helm release in the Kubernetes cluster.
The release creates a StatefulSet with a main OX Consumer container,
a container that waits for the Provisioning API,
and an initialization container that prepares the connector database.
The consumer uses a configured SQL database for its task queue and object state.
:numref:`ox-connector-architecture-kubernetes-deployment-figure`
shows the deployment view of the components for the OX Connector.

The OX Connector connects to the Provisioning API within the cluster.
Nubus for Kubernetes doesn't expose the Provisioning API outside the cluster.

.. _ox-connector-architecture-kubernetes-deployment-figure:

.. figure:: /images/OX_Connector_Architecture_Kubernetes_deployment.*
   :target: ../_images/OX_Connector_Architecture_Kubernetes_deployment.svg
   :alt: OX Connector image and wait-for-dependency image running in the OX Connector pod with its database.

   Deployment view for OX Connector components

.. _ox-connector-architecture-kubernetes-how-it-works:

How the consumer works
======================

The OX Consumer processes one provisioning message at a time.
:numref:`ox-connector-architecture-kubernetes-behavior-figure`
shows the main processing flow.

.. _ox-connector-architecture-kubernetes-behavior-figure:

.. figure:: /images/OX_Connector_Architecture_Kubernetes_behavior.*
   :target: ../_images/OX_Connector_Architecture_Kubernetes_behavior.svg
   :alt: Provisioning flow from the Nubus directory to OX App Suite through the OX Consumer and its database.

   OX Consumer provisioning flow

The following steps describe the provisioning flow:

#. A change to a selected UDM object creates an event in the Provisioning Service.

#. The Provisioning API sends the event to the OX Consumer subscription.

#. The OX Consumer stores the event as a task in its database.

#. The consumer processes pending tasks in a fixed module order and sends the data
   to the SOAP API in OX App Suite.

#. After successful processing, the consumer stores the object state in its database.

When the message handler returns,
the Provisioning API acknowledges the message.
If an exception escapes the message handler,
the message isn't acknowledged and the Provisioning API redelivers it.
The consumer process then stops so that Kubernetes can restart it
with fresh network connections.

The consumer processes context changes before dependent object types.
It then processes access profiles, users, groups, functional accounts,
shared account permissions, shared accounts, resources, and context deletions.

.. dropdown:: For OX Consumer processing in more detail, click to open.
   :color: info
   :icon: zoom-in

   :numref:`ox-connector-architecture-kubernetes-details-figure`
   shows the task queue, the database of old entries, and the SOAP provisioning step.
   The diagram also shows the relation between the Provisioning API,
   the OX Consumer, and OX App Suite.

   .. _ox-connector-architecture-kubernetes-details-figure:

   .. figure:: /images/OX_Connector_Architecture_Kubernetes_Details_Behavior.*
      :target: ../_images/OX_Connector_Architecture_Kubernetes_Details_Behavior.svg
      :alt: Detailed OX Consumer flow including message reception, task storage, SOAP provisioning, and database state.

      Detailed OX Consumer provisioning flow

      Click to zoom the view.

.. _ox-connector-architecture-kubernetes-attributes:

Provisioned attributes
======================

The OX Consumer uses the same default user attribute mapping
as the OX Connector app for Nubus for UCS.
The mapping provisions user names, email addresses and aliases,
business and personal contact details, organization and address data,
profile images, dates, mailbox quotas, IMAP and SMTP servers,
and user-defined fields.

For information about the shared user attribute mapping,
see :ref:`ox-connector-architecture-ucs-attributes`.

.. _ox-connector-architecture-kubernetes-database:

Database of old entries
=======================

The OX Consumer stores pending tasks and object state
in the configured SQL database.
An initialization container prepares the database
when the OX Connector starts.

When the ``old`` and ``tasks`` tables are empty,
the initialization container requests a prefill
from the Provisioning Service.

For information about the database tables and their purpose,
see :ref:`ox-connector-architecture-ucs-database`.
