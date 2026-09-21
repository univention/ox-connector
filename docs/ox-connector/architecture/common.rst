.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-architecture-common:

*******************
Shared architecture
*******************

This page describes architecture components and connector behavior
common to Nubus for UCS and Nubus for Kubernetes.

For deployment-specific details, see
:ref:`ox-connector-architecture-ucs`
and :ref:`ox-connector-architecture-kubernetes`.

.. _ox-connector-architecture-common-components:

Common architecture components
==============================

The OX Connector has the following common architecture components:

.. glossary::

   Identity Store and Directory Service
      The *Identity Store and Directory Service* includes the OpenLDAP software
      that provides the LDAP directory in Nubus.
      The LDAP directory stores identity and infrastructure data in the domain.
      For more information,
      see :external+uv-ucs-operation:ref:`domain-infrastructure-ldap-directory`
      in :cite:t:`uv-ucs-operation`.

   Directory Manager
      The *Directory Manager* is an abstraction layer of directory objects
      in the *Identity Store and Directory Service*.
      For more information,
      see :external+uv-nubus-kubernetes-architecture:ref:`component-directory-manager`
      in :cite:t:`uv-nubus-kubernetes-architecture`.

   Provisioning Service
      The OX Connector subscribes to the *Provisioning Service*
      through the :term:`Provisioning API` for the Univention Directory Manager (UDM)
      modules that it provisions.
      For information about change processing, consumer registration, and *prefill*,
      see :external+uv-nubus-kubernetes-architecture:ref:`component-provisioning-service`
      in :cite:t:`uv-nubus-kubernetes-architecture`.

   Provisioning API
      The OX Connector subscribes through the *Provisioning API*
      for the UDM modules that it provisions.
      For information about the API and consumer registration,
      see :external+uv-nubus-kubernetes-architecture:ref:`component-provisioning-service-consumer-registration-http-rest-api`
      in :cite:t:`uv-nubus-kubernetes-architecture`.

   OX Connector
      *OX Connector* connects Nubus identity management to OX App Suite.
      The connector receives data about changes in the LDAP directory.
      A :term:`OX Connector Provisioning Consumer` handles the data,
      processes it, and sends it to the :term:`SOAP API` in OX App Suite.

   OX Connector Provisioning Consumer
      The *OX Connector Provisioning Consumer* is the *OX Connector* component
      that receives provisioning messages,
      stores work in the connector database, and provisions *OX App Suite* objects.

   OX App Suite
      *OX App Suite* is the groupware and collaboration software from Open-Xchange.

   SOAP API
      *OX App Suite* provides a *SOAP API* for receiving data
      and running remote procedure calls.
      The connector uses the *SOAP API* to create, update, or delete *OX App Suite* objects.

.. _ox-connector-architecture-common-attributes:

Provisioned attributes
======================

The OX Connector maps UDM attributes to OX App Suite attributes.
The default user attribute mapping provisions the following attributes:

* User names, email addresses, and aliases
* Business and personal contact details
* Organization and address data
* Profile images and dates
* Mailbox quotas
* IMAP and SMTP servers
* User-defined fields

.. _ox-connector-architecture-common-database-object-state:

Database of object state
========================

OX App Suite assigns an *internal ID* to each object that it creates or updates.
After successfully processing an object, the connector stores its state,
including the internal ID, in a local database.
The connector doesn't store the internal ID in the LDAP directory.

The connector uses stored internal IDs for operations that require them.
For example, when it updates a group through the :term:`SOAP API`,
the request must include the internal ID of each group member.
This avoids a remote lookup in OX App Suite for each group member.
