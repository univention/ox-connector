.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _configure-database:

********************
Configure a database
********************

.. versionadded:: 0.41.0

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
see ``oxDbConnectionString`` in :ref:`user-provisioning-configuration`.
