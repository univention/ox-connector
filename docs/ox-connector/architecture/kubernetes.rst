.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-architecture-kubernetes:

************************
For Nubus for Kubernetes
************************

The :program:`OX Connector` provisions selected identity data
from Nubus for Kubernetes into *OX App Suite*.
It receives directory changes through the *Provisioning API*.
It sends create, update, and delete requests to the *OX App Suite SOAP API*.

Before you continue reading, ensure you know :ref:`ox-connector-architecture-common`.

.. _ox-connector-architecture-kubernetes-overview:

Overview
========

The :program:`OX Connector` runs as an *OX Connector Provisioning Consumer* in the Kubernetes cluster.
The consumer receives changes from the *Provisioning Service*
for selected Univention Directory Manager (UDM) modules.
It processes the changes and provisions the corresponding *OX App Suite* objects.
:numref:`ox-connector-architecture-kubernetes-components-figure`
shows the following components, their boundaries, and dependencies:

#. :term:`Identity Store and Directory Service`
#. :term:`Directory Manager`
#. :term:`Provisioning Service`
#. :term:`Provisioning API`
#. :term:`OX Connector Provisioning Consumer`
#. :term:`OX App Suite`

.. _ox-connector-architecture-kubernetes-components-figure:

.. figure:: /images/OX_Connector_Architecture_Kubernetes_components.*
   :target: ../_images/OX_Connector_Architecture_Kubernetes_components.svg
   :alt: Nubus for Kubernetes components that provision directory data to OX App Suite through the OX Connector.

   OX Connector components for Nubus for Kubernetes

.. glossary::

   Subscription
      A *subscription* defines the *Provisioning Service* topics
      for which the *OX Connector Provisioning Consumer* receives messages.

   PostgreSQL database: OX Connector
      The :term:`OX Connector Provisioning Consumer` requires a PostgreSQL database
      for the task queue and object state.
      The database helps the connector keep track of objects
      when synchronization errors occur.
      The database isn't part of the *OX Connector* deployment.

For descriptions of shared components,
see :ref:`ox-connector-architecture-common`.

.. _ox-connector-architecture-kubernetes-deployment:

Deployment
==========

You deploy the *OX Connector* as a Helm release in the Kubernetes cluster.
The release creates a StatefulSet with the following containers:

* A main OX Connector container
* A container that waits for the *Provisioning API*
* An initialization container that prepares the connector database

The consumer uses a configured PostgreSQL database for its task queue and object state.
:numref:`ox-connector-architecture-kubernetes-deployment-figure`
shows the deployment of the *OX Connector* components.

.. _ox-connector-architecture-kubernetes-deployment-figure:

.. figure:: /images/OX_Connector_Architecture_Kubernetes_deployment.*
   :target: ../_images/OX_Connector_Architecture_Kubernetes_deployment.svg
   :alt: OX Connector image and wait-for-dependency image running in the OX Connector pod with its database.

   Deployment view for *OX Connector* components

.. _ox-connector-architecture-kubernetes-how-it-works:

OX Connector Provisioning Consumer behavior
===========================================

The *OX Connector* connects to the *Provisioning API* within the cluster.
Nubus for Kubernetes doesn't expose the *Provisioning API* outside the cluster.

The :term:`OX Connector Provisioning Consumer` processes one provisioning message at a time.
:numref:`ox-connector-architecture-kubernetes-behavior-figure`
shows the main processing flow.

.. _ox-connector-architecture-kubernetes-behavior-figure:

.. figure:: /images/OX_Connector_Architecture_Kubernetes_behavior.*
   :target: ../_images/OX_Connector_Architecture_Kubernetes_behavior.svg
   :alt: Provisioning flow from the Nubus directory to OX App Suite through the OX Consumer and its database.

   OX Consumer provisioning flow

The following list describes the provisioning flow:

#. A change to a subscribed UDM object creates an event in the *Provisioning Service*.

#. The *Provisioning API* sends the event to the *OX Consumer* subscription.

#. The *OX Consumer* stores the event as a task in its database.

#. The consumer processes the event and sends its data to the *SOAP API* in *OX App Suite*.

#. After successful processing, the consumer stores the object state in its database.

When the message handler returns successfully,
the *Provisioning API* acknowledges the message.
If an exception escapes the message handler,
the *Provisioning API* doesn't acknowledge the message and redelivers it.
The consumer process then stops.
Kubernetes restarts the process with fresh network connections.

The consumer processes context changes before dependent object types.
It then processes the following object types:

* Context changes
* Access profiles
* Users
* Groups
* Functional accounts
* Shared account permissions
* Shared accounts
* Resources
* Context deletions

.. dropdown:: Detailed OX Connector Provisioning Consumer processing, click to open.
   :color: info
   :icon: zoom-in

   :numref:`ox-connector-architecture-kubernetes-details-figure`
   shows the task queue, the database for *OX Connector*,
   and the SOAP provisioning step.
   The diagram also shows the relation between the *Provisioning API*,
   the *OX Consumer*, and *OX App Suite*.

   .. _ox-connector-architecture-kubernetes-details-figure:

   .. figure:: /images/OX_Connector_Architecture_Kubernetes_Details_Behavior.*
      :target: ../_images/OX_Connector_Architecture_Kubernetes_Details_Behavior.svg
      :alt: Detailed OX Consumer flow including message reception, task storage, SOAP provisioning, and database state.

      Detailed OX Consumer provisioning flow

      Click the diagram to zoom in.

.. _ox-connector-architecture-kubernetes-attributes:

Provisioned attributes
======================

For information about provisioned attributes,
see :ref:`ox-connector-architecture-common`.

.. _ox-connector-architecture-kubernetes-database:

Database of stored object state
===============================

The :term:`OX Connector Provisioning Consumer` stores pending tasks
and object state in the configured SQL database.
An initialization container prepares the database when the *OX Connector* starts.

When the ``old`` and ``tasks`` tables are empty,
the initialization container requests a *prefill* from the *Provisioning Service*.
It skips the request if its configuration doesn't enable resynchronization
or if it can't access the required credentials.

For information about stored object state and OX internal IDs,
see :ref:`ox-connector-architecture-common`.
