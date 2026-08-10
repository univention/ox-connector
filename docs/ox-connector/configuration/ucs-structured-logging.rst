.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-ucs-structured-logging:

Structured logging on UCS
=========================

.. versionadded:: 4.0.0

The :program:`OX Connector` app emits log messages in a structured format
that follows the Nubus platform logging standard.
Each log line contains a fixed set of fields
followed by key-value pairs with context-specific data,
as shown in :numref:`ox-connector-ucs-structured-logging-pattern-listing`.

.. code-block:: none
   :caption: Structured log line format
   :name: ox-connector-ucs-structured-logging-pattern-listing

   <timestamp> <severity:8> [<request ID>] <message>\t| <key=value ...> <source>

The fields have the following meanings:

``timestamp``
   The timestamp is ISO 8601-formatted
   and includes sub-second precision and the time zone,
   for example ``2024-06-01T12:00:00.123456+00:00``.

``severity``
   The log level field has a width of 8 characters,
   for example ``INFO`` or ``WARNING``.
   :envvar:`OX_CONNECTOR_LOG_LEVEL` controls this value.

``request ID``
   The request ID is the sequence number of the provisioning message.
   It groups all log lines that belong to a single provisioning job.
   A dash (``-``) indicates that no job is active.

``message``
   The message is the human-readable description of the event.

``key=value pairs``
   The structured application data uses the ``logfmt`` format,
   for example ``dn="uid=user01,dc=example,dc=com" object_type=users ms=42``.

``source``
   The source is the Python module name that produced the log entry.

.. TODO: Use a valid logging example. See univention/dev/projects/open-xchange/connector#219

.. seealso::

   :external+uv-nubus-manual:ref:`nubus-logging`
      in :cite:t:`uv-nubus-manual`
      for information about the Nubus structured logging format,
      available log levels,
      and integration with log management systems.
