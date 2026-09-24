.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-configuration-kubernetes:

Configuration for Nubus for Kubernetes
======================================

Use this reference to configure the :program:`OX Connector`
on Nubus for Kubernetes.
This page uses the published :program:`OX Connector` Helm Chart
to provide the Helm Chart values reference.

.. _ox-connector-configuration-kubernetes-database:

Configure a database
--------------------

.. versionadded:: v0.41.0

   Add in *OX Connector* for Kubernetes version v.0.41.0.

To support the shared accounts feature,
the *OX Connector* requires a PostgreSQL database to store account references.
PostgreSQL is the only tested and supported database for the *OX Connector*.
The database isn't part of the OX App Suite packaged and the OX Connector integration.
You need to provide it separately.

Before you install or upgrade to a version ≥ 0.41.0,
ensure the following requirements for the database for the *OX Connector* in PostgreSQL:

* You have created an empty database for the *OX Connector*.
* You have created a dedicated database user for the *OX Connector* with the ``ALL PRIVILEGES`` privilege.

For information about how to configure the database connection,
see :envvar:`openXchange.oxDbConnectionString` in :ref:`ox-connector-install-on-kubernetes-prepare-ox-consumer`.

.. _ox-connector-configuration-kubernetes-helm-chart-reference:

Helm Chart references values
----------------------------

..
   The included reference is generated.
   To update it, run docs/ox-connector/update-helm-values-reference.py.

.. only:: not spelling and not linkcheck

   .. include:: reference-values-kubernetes.txt
