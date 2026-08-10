.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-ucs-structured-logging:

Use structured logging on UCS
=============================

.. versionadded:: 4.0.0

The :program:`OX Connector` app emits log messages in a structured format
consistent with the Nubus platform logging standard. Each log line contains a
fixed set of fields followed by key-value pairs with context-specific data:

.. code-block:: none
   :caption: Structured log line format

   <timestamp> <severity:8> [<request ID>] <message>\t| <key=value ...> <source>

The fields have the following meaning:

``timestamp``
   ISO 8601 formatted timestamp with sub-second precision and timezone,
   for example ``2024-06-01T12:00:00.123456+00:00``.

``severity``
   Log level, padded to 8 characters, for example ``INFO`` or
   ``WARNING``. Controlled by :envvar:`OX_CONNECTOR_LOG_LEVEL`.

``request ID``
   Sequence number of the provisioning message that groups all log lines
   belonging to a single provisioning job. A dash (``-``) indicates that
   no job is active.

``message``
   Human-readable description of the event.

``key=value pairs``
   Structured application data in ``logfmt`` format, for example
   ``dn="uid=user01,dc=example,dc=com" object_type=users ms=42``.

``source``
   Python module name that produced the log entry.

Example log output:

.. code-block:: none
   :caption: Example structured log lines from the OX Connector

   2026-07-14T06:23:48.635+00:00 INFO     [         -] Listening for changes in topics    | topics="{'groups/group', 'oxresources/oxresources', 'oxmail/oxcontext', 'oxmail/accessprofile', 'oxmail/shared_account_permission', 'oxmail/functional_account', 'oxmail/shared_account', 'users/user'}" _source=consumer.start_listening_for_changes:62
   2026-07-14T06:23:51.942+00:00 INFO     [        25] Received message    | topic=users/user sequence_number=25 num_delivered=1 _source=consumer.handle_message:87
   2026-07-14T06:23:51.943+00:00 INFO     [        25] Enqueuing task    | obj=46d6f555-e1ef-4136-8cf8-b4e0cb897d2e module=users/user _source=consumer.handle_message:113
   2026-07-14T06:23:51.943+00:00 INFO     [        25] Task created    | task="uid=t3user,cn=users,dc=swp-ldap,dc=internal (46d6f555-e1ef-4136-8cf8-b4e0cb897d2e; users/user; tasks:None)" _source=db.enqueue_task:314
   2026-07-14T06:23:51.969+00:00 INFO     [        25] Processing Task    | task="uid=t3user,cn=users,dc=swp-ldap,dc=internal (46d6f555-e1ef-4136-8cf8-b4e0cb897d2e; users/user; tasks:25)" _source=consumer._process_all_tasks_with_db:173
   2026-07-14T06:23:51.975+00:00 INFO     [        25] No old data found    | id=46d6f555-e1ef-4136-8cf8-b4e0cb897d2e _source=db.get_old:403
   2026-07-14T06:23:51.975+00:00 INFO     [        25] Load old object from db    | obj="Object('users/user', 'uid=t3user,cn=users,dc=swp-ldap,dc=internal')" _source=consumer._process_all_tasks_with_db:176
   2026-07-14T06:23:51.976+00:00 INFO     [        25] Creating object    | object="Object('users/user', 'uid=t3user,cn=users,dc=swp-ldap,dc=internal')" _source=users.create_user:346
   2026-07-14T06:23:51.976+00:00 INFO     [        25] Searching for username in context    | username=t3user context=1 _source=users.get_user_id:330
   2026-07-14T06:23:52.596+00:00 INFO     [        25] Using default user attribute mapping    | _source=users.get_user_mapping:136
   2026-07-14T06:23:52.795+00:00 INFO     [        25] Created object in context.    | object_type=user name=t3user context=1 object_id=6 _source=backend.create:227
   2026-07-14T06:23:52.796+00:00 INFO     [        25] Changing user to profile    | user=6 user_access=opendesk_standard _source=users.set_user_rights:307
   2026-07-14T06:23:52.878+00:00 INFO     [        25] Looking for groups of this user to be created in the context id    | _source=users.create_user:422
   2026-07-14T06:23:52.888+00:00 INFO     [        25] Created entry in old db    | entry="uid=t3user,cn=users,dc=swp-ldap,dc=internal (46d6f555-e1ef-4136-8cf8-b4e0cb897d2e; users/user; old:None)" _source=db.move_task_to_old:373
   2026-07-14T06:23:52.893+00:00 INFO     [        25] Deleted task    | task="uid=t3user,cn=users,dc=swp-ldap,dc=internal (46d6f555-e1ef-4136-8cf8-b4e0cb897d2e; users/user; tasks:25)" _source=db.move_task_to_old:385
   2026-07-14T06:23:52.944+00:00 INFO     [         -] Message 25 was acknowledged.    | _source=api.acknowledge_message_with_retries:163

.. seealso::

   `Structured logging — Nubus Manual <https://docs.software-univention.de/nubus-manual/latest/en/logging.html#nubus-logging-structured>`_
      for a complete description of the Nubus structured logging format,
      available log levels, and how to integrate with log management systems.
