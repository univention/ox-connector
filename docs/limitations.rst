.. Like what you see? Join us!
.. https://www.univention.com/about-us/careers/vacancies/
..
.. Copyright (C) 2021-2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only
..
.. https://www.univention.com/
..
.. All rights reserved.
..
.. The source code of this program is made available under the terms of
.. the GNU Affero General Public License v3.0 only (AGPL-3.0-only) as
.. published by the Free Software Foundation.
..
.. Binary versions of this program provided by Univention to you as
.. well as other copyrighted, protected or trademarked materials like
.. Logos, graphics, fonts, specific documentations and configurations,
.. cryptographic keys etc. are subject to a license agreement between
.. you and Univention and not subject to the AGPL-3.0-only.
..
.. In the case you use this program under the terms of the AGPL-3.0-only,
.. the program is provided in the hope that it will be useful, but
.. WITHOUT ANY WARRANTY; without even the implied warranty of
.. MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE. See the GNU
.. Affero General Public License for more details.
..
.. You should have received a copy of the GNU Affero General Public
.. License with the Debian GNU/Linux or Univention distribution in file
.. /usr/share/common-licenses/AGPL-3; if not, see
.. <https://www.gnu.org/licenses/agpl-3.0.txt>.

.. _app-limitations:

***********
Limitations
***********

To ensure a smooth operation of the :program:`OX Connector` app on UCS, you as
administrator need to know the following limitations.

.. _limit-ox-app-suite-app:

Integration of OX Connector and OX App Suite app
================================================

Starting with version 2.1.2, Univention does support the use of :program:`OX
Connector` towards the :program:`OX App Suite` app from Univention App Center.
The :program:`OX Connector` takes over the provisioning, the :program:`OX App
Suite` ships the actual groupware.

However, the OX Connector needs administrative credentials to create context
objects in OX' database. The installation process doesn't know these
credentials. Thus, you may need to reconfigure the :program:`OX Connector` after
you installed :program:`OX App Suite` successfully. The reconfiguration runs
automatically, if, and only if, both apps locate on the same UCS system.

If not, you find the password on the UCS system that runs :program:`OX App
Suite` in the file :file:`/etc/ox-secrets/master.secret`. The username of the
administrative account is ``oxadminmaster``. You can set the credentials in the
app settings of the :program:`OX Connecor`, see :ref:`app-configuration`.

.. _limit-stop-at-conflict:

OX Connector stops at faulty items
==================================

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

.. admonition:: Design decision

   The OX Connector doesn't provide logic to resolve conflicts automatically,
   because the conflict causes can vary a lot. For example, when connector would
   ignore the conflict and continue, a later operation may refer to the ignored
   item. The connector can't complete it, because the current queue item refers
   to a previous, unprocessed item. The OX Connector could ignore the next
   conflict again, and again. The ignores pile up unresolved conflicts that can
   lead to a heavy conflict or a serious problem with the user provisioning
   without any relation to the actual root cause. Administrators would have
   quite a hard job to resolve the conflict.

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
