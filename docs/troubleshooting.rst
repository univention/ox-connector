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

.. _app-troubleshooting:

***************
Troubleshooting
***************

When you encounter problems with the operation of the :program:`OX Connector`
app, this section provides information where you can look closer into and to
get an impression about what's going wrong.

.. _log-files:

Log files
=========

The :program:`OX Connector` app produces different logging information in
different places.

.. index::
   pair: listener converter; log file

Listener Converter: :file:`/var/log/univention/listener_modules/ox-connector.log`
   Contains log information from the :term:`Listener Converter` about create,
   update and delete actions of objects.

   It also shows warnings and errors when the OX Connector configuration isn't
   correct, or the connector can't establish a connection to the :term:`SOAP
   API`.

.. index::
   single: log file; app center

App Center: :file:`/var/log/univention/appcenter.log`
   Contains log information around activities in the App Center.

   The App Center writes OX Connector relevant information to this file, when
   you run app lifecycle tasks like install, update and uninstall or when you
   change the app settings.

.. index::
   single: log file; domain join

Domain join: :file:`/var/log/univention/join.log`
   Contains log information from the join processes. When the App Center install
   OX Connector, the app also joins the domain.

.. _health-check:

Health check
============

.. index::
   pair: listener converter; health check
   pair: listener; health check

First, have a look at the log file for the :term:`Listener Converter` and look
for warnings and errors, see :ref:`log-files`.

The OX Connector has a good health when the number of files for provisioning
for the :term:`Listener` and the :term:`Listener Converter` is low. For a quick
verification, run the following command on the UCS system with the OX Connector
installed:

.. code-block:: console
   :caption: Verify the number of unprocessed files for the :term:`Listener`.

   $ DIR_LISTENER="/var/lib/univention-appcenter/listener/ox-connector"
   $ ls -1 "$DIR_LISTENER"/*.json 2> /dev/null | wc -l
   0

.. code-block:: console
   :caption: Verify the number of unprocessed files for the :term:`Listener Converter`.

   $ DIR_CONVERTER="/var/lib/univention-appcenter/apps/ox-connector/data/listener"
   $ ls -1 "$DIR_CONVERTER"/*.json 2> /dev/null | wc -l
   0

The :term:`Listener Converter` logs consecutive errors in the log file, for
example:

.. code-block:: text

   INFO    This is consecutive error #{some number}

Such entries indicate that the provisioning has issues with processing the
queue. For more information, see :ref:`trouble-queue`.

.. _provision-stopped:

Provisioning stops working
==========================

.. index::
   single: provisioning; stopped
   single: provisioning; faulty item

When the provisioning stopped working, a previous change in |UDM| is a
probable reason and the OX Connector doesn't know how to proceed. The connector
retries the action over and over again until an administrator repairs the cause
manually.

First, see the :ref:`log-files` and look for warnings and errors. If it's not a
temporary problem like for example network connectivity, the fix requires manual
action.

As a last resort, the administrator can delete the flawed file. The log file
reveals the flawed file and its path, see :ref:`queue-delete-one`.

.. _trouble-queue:

Queuing
=======

.. index::
   single: provisioning; queue
   see: queue; provisioning

The queue for provisioning consists of JSON files. :ref:`app-how-it-works`
describes the connector's data processing. Administrators can manually intervene
with the queue in the following cases.

.. _queue-delete-one:

Delete one item from the queue
------------------------------

Administrators can remove an item in the queue, if the connector can't process
it and interrupts the provisioning process. The connector retries to
provision this item and continually fails.

To find and remove the problematic item from the queue, follow these steps:

#. Open the log file of the :term:`Listener Converter`. For the log file
   location, see :ref:`log-files`.

#. Find the filename of the item that the *Listener Converter* retries to
   provision. For example, the log file shows:

   .. code-block:: text

      Error while processing /var/lib/univention-appcenter/apps/ox-connector/data/listener/$timestamp.json

   ``$timestamp`` has the format ``%Y-%m-%d-%H-%M-%S``.

#. Remove the problematic item:

   .. code-block:: console

      $ rm /var/lib/univention-appcenter/apps/ox-connector/data/listener/$timestamp.json

.. _queue-reprovision-one:

Re-provision one specific UDM object
------------------------------------

The OX Connector allows to re-provision one UDM object to OX App Suite. The
following snippet provisions one user object:

.. code-block:: bash
   :caption: Re-provision one UDM object

   DN="uid=user100,cn=users,$(ucr get ldap/base)"
   ENTRY_UUID="$(univention-ldapsearch -b "$DN" + | grep entryUUID | awk '{ print $2 }')"
   cat > /var/lib/univention-appcenter/listener/ox-connector/$(date +%Y-%m-%d-%H-%M-%S).json <<- EOF
   {
       "entry_uuid": "$ENTRY_UUID",
       "dn": "$DN",
       "object_type": "users/user",
       "command": "modify"
   }
   EOF

.. _queue-reprovision-all:

Re-provision all data
---------------------

.. warning::

   Depending on the number of users and groups in the UCS LDAP directory, this
   task may take a lot of time.

   **Reprovisioning all data isn't recommended.**

The following command reads all |UDM| objects from the |UCS| LDAP directory and
adds them to the provisioning queue:

.. code-block:: console
   :caption: Re-provisioning all UDM objects to OX App Suite

   $ univention-directory-listener-ctrl resync ox-connector

The re-provisioning won't run any *delete* operations, because the Listener
only adds existing UDM objects to the queue.

.. caution::

   The OX Connector may decide to delete objects based on data in the JSON
   files. For example ``isOxGroup = Not`` in a group object.

.. _cache-rebuild:

Rebuild cache
=============

.. index::
   single: cache; rebuild

The *internal ID* of objects in the database of OX App Suite can become
corrupted, for example after a backup restore of the database. For more
information about the cache, see :ref:`cache-internal-id`.

To rebuild the cache, run the following commands:

.. code-block:: console
   :caption: Rebuild cache for *internal ID*

   $ univention-app shell ox-connector
   /oxp # update-ox-db-cache --delete
   /oxp # update-ox-db-cache

.. versionchanged:: 2.0.0

   Rebuild the cache after an update to version 2.0.0, because previous
   versions didn't maintain the cache for the *internal ID*.

   Otherwise, the OX Connector app falls back into the much slower mechanism and
   runs a database query per user during the provisioning.

.. tip::

   Retrieve all users per context in one request
      Rebuilding the cache may take a long time and depends on the amount of
      users in the OX App Suite database.

      :command:`update-ox-db-cache --build-cache` can speed up the rebuild,
      because it retrieves all users of a context with one request.

.. warning::

   .. index::
      single: cache; memory consumption
      single: cache; system load

   Memory consumption
      On the UCS system with the OX Connector, the rebuild process may use up to
      1 GB memory per 10,000 users in the database for OX App Suite.

   System load
      Furthermore, the process may generate a lot of load on the OX App Suite
      system and the OX Connector app.

Collect information for support ticket
======================================

Before you open a support ticket, make sure to collect and provide relevant
details about your case, so that the Univention Support team can help you:

* `Provide relevant details about your environment
  <https://help.univention.com/faq#posting-guidelines>`_.

* Provide the relevant messages and tracebacks from  :ref:`log-files`,
  specifically the :term:`Listener Converter`.

* Describe the steps that can reproduce the faulty behavior.

* Describe the expected behavior.

* Provide data from the provisioning that causes the error.

