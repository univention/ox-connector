.. SPDX-FileCopyrightText: 2021 - 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _app-limitations:

***********
Limitations
***********

To ensure a smooth operation of the :program:`OX Connector` app on UCS, you as
administrator need to know the following limitations.

.. _limit-ox-app-suite-app:

Integration of OX Connector and OX App Suite app
================================================

Starting with version 2.1.2,
Univention supports the use of the :program:`OX Connector`
for the :program:`OX App Suite` app from Univention App Center.
The :program:`OX Connector` handles the provisioning,
while the :program:`OX App Suite` delivers the actual groupware.

However, the OX Connector needs administrative credentials
to create context objects in the database for the :program:`OX App Suite`.
The installation process doesn't know these credentials.
Therefore, you need to verify the configuration of the :program:`OX Connector`
after you have successfully installed :program:`OX App Suite`.
The reconfiguration runs automatically
if, and only if, both apps locate on the same UCS system.

If not,
you find the password in the file :file:`/etc/ox-secrets/master.secret`
on the UCS system running :program:`OX App Suite`.
The username of the administrative account is ``oxadminmaster``.
You need to set the credentials in the app settings of the :program:`OX Connecor`,
see :ref:`app-configuration`.

.. _how-the-connector-handles-fauly-items:

How the Connector handles faulty items
======================================

The :program:`OX Connector` knows two strategies how to handle faulty items it
can't synchronize. You can choose which strategy to use: :ref:`settings`.

.. _limit-continue-at-conflict:

OX Connector continues after faulty items
-----------------------------------------

.. index::
   single: provisioning; faulty item

When the :program:`OX Connector` encounters a faulty queue item that it can't
process, it continues with the next queue items. The faulty item is put aside
for the Administrator to examine at a later stage. The problem is written in
the log file, see :ref:`log-files`.

The app ships a CLI to manage the list of errors, see
:ref:`app-troubleshooting`. 

As administrator, you need to monitor the list of errors manually and decide
what to do (delete or retry). Meanwhile, the :program:`OX Connector` continues
to process data it gets from the :term:`Listener`.

Note that certain errors are excluded from that behavior. When the :program:`OX
Connector` encounters a problem that hints to a network error, it retries this
one task over and over again as continuing will most probably result in the
same error for all items anyway. Synchronizing objects from the UDM module
``oxmail/oxcontext`` will also be retried as these objects are extremely
important to by in sync. All following items in the queue will likely fail,
therefore the app does not just continue in this case. The strategy of stopping
instead of continuing is also described in the next chapter
:ref:`limit-stop-at-conflict`.

.. _limit-stop-at-conflict:

OX Connector stops at faulty items
----------------------------------

.. index::
   single: provisioning; faulty item

When the :program:`OX Connector` encounters a faulty queue item that it can't
process, it stops the provisioning at the item and logs the filename with its
path in the :term:`Listener Converter` log file, see :ref:`log-files`.

Despite the stop, the :term:`Listener` continues to add items to the queue.
After the administrator removed the faulty queue item, the Listener Converter
continues to process the queue and also takes care of the added items.

As administrator, you need to resolve that conflict manually when it happens,
see :ref:`provision-stopped`. After the conflict resolution, the connector
continues to process the provisioning queue.

.. _limit-access-profiles:

No plausibility validation in access profile rights
===================================================

.. index::
   single: access profiles; plausibility
   single: OX App Suite; permission level
   see: permission level; OX App Suite

The :program:`OX Connector` app doesn't evaluate permission level for created
*access profiles* and tries to create any access profile.

For more information, see `OX App Suite Permission Level
<https://oxpedia.org/wiki/index.php?title=AppSuite:Permission_Level>`_.
