.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-changelog-app:

**************************
Changelog OX Connector app
**************************

This changelog documents all notable changes to the :term:`OX Connector` app.
It follows the `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_ format
and adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

.. _app-changelog-v4.0.0:

v4.0.0
======

Released: 2026-09-16

Changed
-------

The container image for the OX Connector changed from
*Alpine Linux* to a *UCS Base Image*.
In most cases, this change has no effect.
If manual workflows rely on properties of the underlying OX Connector image,
adjust them.
The image also updates Python from ``3.9`` to ``3.13``.

The *OX Connector* app now uses :ref:`ox-connector-ucs-structured-logging`.

The OX Connector no longer receives changes from the UCS LDAP directory
through the App Center *Listener* mechanism.
It now subscribes to the Nubus *Provisioning Service*
through the *Provisioning API*.
The *Provisioning Consumer* inside the app container receives the changes directly,
without the intermediate JSON files.
The database location changed from
:file:`/var/lib/univention-appcenter/apps/ox-connector/data/listener/ox-connector.db`
to :file:`/var/lib/univention-appcenter/apps/ox-connector/data/ox-connector.db`.
During an update,
the app automatically moves existing databases.

The OX Connector depends on the *Provisioning Service*.
During installation or upgrade,
you can set the provisioning parameters.
For more information,
see :external+uv-manual:ref:`nubus-provisioning-service`.

Removed
-------

The following tools have been removed:

* ``rebuild-old.db``
* ``remove-from-ox-db-cache``
* ``update-ox-db-cache``
* ``check_sync_status.py``
* ``get_current_error.py``

They used deprecated database calls and didn't work correctly.
Use ``univention-ox-connector-task-management`` instead.

.. _app-changelog-v3.2.3:

v3.2.3
======

Released: 2026-07-06

Added
-----

For *OX Shared Accounts*, the following attributes are now explicitly synchronized:

* ``Language``
* ``Timezone``
* ``SMTP server``
* ``IMAP server``

The *OX Connector* takes these values from its global configuration.
You can't change them for individual shared accounts.

.. _app-changelog-v3.2.2:

v3.2.2
======

Released: 2026-06-25

Added
-----

The :envvar:`OX_SHARED_ACCOUNT_IDENTIFIER` setting lets you set the name of an *OX Shared Account*.

Fixed
-----

The lookup for existing OX users before their creation could fail in some cases.
It used the UDM object's username for the search
instead of the configured :envvar:`OX_USER_IDENTIFIER` value.

.. _app-changelog-v3.2.1:

v3.2.1
======

Released: 2026-06-10

Added
-----

Added a migration script for *OX Functional Accounts* to *OX Shared Accounts*.
Use the script to migrate existing functional accounts to shared accounts.
For more information, see :ref:`ox-connector-usage-shared-accounts-migration`.

.. _app-changelog-v3.2.0:

v3.2.0
======

Released: 2026-05-22

Added
-----

Added support for *OX Shared Accounts*.
You can now create UDM objects for shared accounts and their corresponding permissions.
For more information, see :ref:`ox-connector-usage-shared-accounts`.

.. _app-changelog-v3.1.0:

v3.1.0
======

Released: 2026-03-17

Removed
-------

The ``groups`` property in the *Functional Accounts* module has been removed.
Adding groups to *Functional Accounts* was never supported,
so it wasn't available in the Univention Management Console (UMC).
The logic that still made it possible to set groups through direct
Univention Directory Manager access has been removed.

.. important::

    If groups were used as *Functional Account* members,
    add their members directly to the *Functional Account*.
    Attempting to add a group to a *Functional Account* will raise an error in UDM after this update.

.. _app-changelog-v3.0.2:

v3.0.2
======

Released: 2026-03-12

Fixed
-----

Users can grant deputy permissions to other users through
``oxDeputyPermissionGivenTo``.
The OX Connector now updates these references when the affected user moves in LDAP.

.. _app-changelog-v3.0.1:

v3.0.1
======

Released: 2025-10-06

Changed
-------

The sub-command
:command:`/usr/sbin/univention-ox-connector-task-management resync-item`
can now resynchronize items from the morgue and the old table.

After consecutive errors, the *OX Connector* increases the delay between runs.
This prevents log files from filling with repeated error messages.
The delay increases with each consecutive error, up to 20 minutes.

Added
-----

Added the sub-command
:command:`/usr/sbin/univention-ox-connector-task-management rewrite-ox-db-id`.

Added the sub-command
:command:`/usr/sbin/univention-ox-connector-task-management export-old`.

.. _app-changelog-v3.0.0:

v3.0.0
======

Released: 2025-09-29

Changed
-------

The *OX Connector App* now stores its task queue in an SQLite database instead of JSON files.
The database stores pending tasks and data for objects
that the connector has already processed.
GDBM-based key-value stores have been removed.
Some helper scripts no longer work:
``rebuild-old.db``, ``remove-from-ox-db-cache``, and ``check_sync_status.py``.
Existing monitoring plugins might need adjustment.

The app automatically migrates existing data,
but the migration can take time depending on your environment.

Added
-----

You can configure the *OX Connector App* to continue processing the queue after an error.
By default, it stops after the first error, so its behavior remains unchanged.

For more information, see :envvar:`OX_CONNECTOR_STOP_ON_ERROR`.

.. _app-changelog-v2.3.5:

v2.3.5
======

Released: 12. August 2025

Removed
-------

The resource manager field has been removed from the UMC.
The property remains available on OX resources in UDM, where you can view and edit it.

There are no functional changes in the application.

.. _app-changelog-v2.3.4:

v2.3.4
======

Released: 23. July 2025

Fixed
-----

Fixed the OX Resources UDM handler, which prevented the OX Connector from working with UCS 5.2-2.

.. _app-changelog-v2.3.3:

v2.3.3
======

Released: 10. June 2025

Fixed
-----

UDM now prevents you from creating an OX Context with an ID
that another context already uses.

Changed
-------

Creating a new user in OX can now convert an existing OX guest account
with the same email address.
Note that this requires OX 8.36.36, which isn't currently present in the *App Center*.
Also note that this only works for creating users;
modifying users (or similar) won't have this feature.
If the *OX Connector* can't send this ``convertguest`` flag,
the old behavior applies: Guest accounts with the same email address as the user being processed
will block further processing until the error is resolved.

.. _app-changelog-v2.3.2:

v2.3.2
======

Released: 4. June 2025

Fixed
-----

The *OX Connector App* uses an internal key-value store to track object states.
The keys are the distinguished names (DNs) of LDAP objects.
Previously, the connector stored the DNs as provided.
It now normalizes and converts them to lowercase.
The app normalizes existing key-value store keys during an upgrade.
Use :command:`univention-app shell ox-connector rebuild-old.db` for this migration.

When you changed a user with the same name as a context administrator
through UDM or UMC, an edge case could cause the *OX Connector*
to change the OX context administrator in the OX database.
This could cause authorization and synchronization issues for the OX context administrator.

Changed
-------

In certain cases, changes to an OX user weren't immediately reflected in OX,
so the *OX Connector* couldn't retrieve the correct database ID.
The *OX Connector App* now retries the lookup several times.

.. _app-changelog-v2.3.1:

v2.3.1
======

Released: 16. Apr 2025

Added
-----

You can now specify a log level for the *OX Connector*.
For more information, see :ref:`ox-connector-configuration-ucs-app-settings`.

Changed
-------

The app setting :envvar:`OX_CONNECTOR_LOG_LEVEL` is used to specify the log level of the ox-connector.

Fixed
-----

The ``oxContext`` attribute syntax has changed from a string to an integer.

.. _app-changelog-v2.3.0:

v2.3.0
======

Released: 27. Mar 2025

Added
-----

Added support for provisioning
`OX deputy permissions <https://documentation.open-xchange.com/8/middleware/permissions_and_capabilities/deputy_permission.html>`_
through the *OX Connector App*.
OX deputy permissions let a user act on behalf of another user in OX App Suite,
which provides delegated access to email and calendars.
Administrators can configure these permissions to control the access level
and actions that deputies can perform.

You can now add external CA certificates to the container.
For more information, see :ref:`ox-connector-ucs-additional-certificates`.

Changed
-------

The app setting :envvar:`OX_IMAP_LOGIN` can contain all attribute names as placeholders.
While the *OX Connector* still replaces the default value ``{}`` with the user's email address,
you can set it to ``{univentionObjectIdentifier}``, for example, given that such an attribute exists.

Fixed
-----

Translations now work correctly.

.. _app-changelog-v2.2.15:

v2.2.15
=======

Released: 17. Feb 2025

Changed
-------

Improved the error message when the :envvar:`OX_USER_IDENTIFIER`
or :envvar:`OX_GROUP_IDENTIFIER` app setting isn't configured correctly.

Improved the error message when an object requires re-provisioning.

Fixed
-----

The documentation wasn't explicit about setting the administrative password
in the app settings for the *OX Connector App*.

The internal key-value store that tracks user objects now handles DN keys case-insensitively.

.. _app-changelog-v2.2.14:

v2.2.14
=======

Released: 29. Oct 2024

Changed
-------

Access profile names can now include special characters.

.. _app-changelog-v2.2.13:

v2.2.13
=======

Released: 17. Sep 2024

Changed
-------

Previously, the OX Connector didn't change the
``default_sender_address`` user preference when you changed an OX user in UDM.
When a UDM change updates ``primaryMailAddress``, and the previous address was
the user's ``default_sender_address``, the OX Connector updates
``default_sender_address`` to the new email address.

.. _app-changelog-v2.2.12:

v2.2.12
=======

Released: 28. Aug 2024

Changed
-------

You can now add LDAP containers to the list of default containers for functional accounts
and select the container before creating a new functional account in UMC.
For more information, see the :ref:`ox-connector-usage-functional-accounts`.

.. _app-changelog-v2.2.11:

v2.2.11
=======

Released: 23. May 2024

Fixed
-----

Fixed a bug that prevented the removal of Open-Xchange contexts.

.. _app-changelog-v2.2.10:

v2.2.10
=======

Released: 26. April 2024

Changed
-------

The performance of the OX Connector has been improved.

.. _app-changelog-v2.2.9:

v2.2.9
======

Released: 12. April 2024

Added
-----

You can now change the attribute mapping between Open-Xchange and UCS
through the :command:`change_attribute_mapping.py` script.
For more information, see :ref:`ox-connector-configuration-ucs-user-attribute-mapping`.

.. _app-changelog-v2.2.8:

v2.2.8
======

Released: 16. January 2024

Changed
-------

The :file:`meta.db` file also stores the error message
and the filename associated with the error.

Added
-----

The :command:`get_current_error.py` script outputs a JSON object
containing the contents of the :file:`meta.db` file.
You can use this output to automate app health checks.

The app settings :envvar:`OX_USER_IDENTIFIER` and :envvar:`OX_GROUP_IDENTIFIER` have been added.
They give control over which UDM property is used as the unique identifier for users and groups in *OX App Suite*.

Added the :command:`check_sync_status.py` script.
You can use it to identify data inconsistencies between UDM, OX App Suite,
and listener files.

.. _app-changelog-v2.2.7:

v2.2.7
======

Released: 7. September 2023

Changed
-------

The :envvar:`OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE` app setting can now contain any string,
which simplifies SSO configurations.

Fixed
-------

Fixed handling of an empty :envvar:`OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE` app setting,
see :uv:bug:`56523`.

Fixed an error when you changed both the context and username in the same operation,
see :uv:bug:`56525`.

.. _app-changelog-v2.2.6:

v2.2.6
======

Released: 18. August 2023

Changed
-------

The *Functional Account* login field is now configurable through the app setting :envvar:`OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE`.


.. _app-changelog-v2.2.5:

v2.2.5
======

Released: 16. August 2023

Changed
-------

User context changes now use the ``UserCopy`` service.

.. _app-changelog-v2.2.4:

v2.2.4
======

Released: 13. July 2023

Changed
-------

The ``imaplogin`` field is now configurable through the app setting :envvar:`OX_IMAP_LOGIN`.

.. _app-changelog-v2.2.3:

v2.2.3
======

Released: 27. June 2023

Fixed
-------

Corrected a typo in the :command:`listener_trigger` script.

.. _app-changelog-v2.2.2:

v2.2.2
======

Released: 22. June 2023

Fixed
-------

The *OX Connector App* now prevents values set by users in the *App Suite* app
from being overwritten incorrectly.

.. _app-changelog-v2.2.1:

v2.2.1
======

Released: 07. June 2023

Changed
-------

You can no longer change a group's OX context in the UMC groups module.
The OX Connector derives the context from the group's users.

.. _app-changelog-v2.2.0:

v2.2.0
======

Released: 01. June 2023

Changed
-------

Removed use of old ``oxDrive`` and ``oxAccessUSM`` UDM properties.
The *OX Connector* only uses the ``oxmail/accessprofile`` objects to control access rights.

The *OX Connector* now supports duplicate ``oxDisplayName`` values.

The *OX Connector* only sets a user's ``default_sender_address``, ``language``, and ``timezone``
when initially creating a user.
Afterwards, any user can configure their settings in the *OX App Suite* front-end.

The OX connector can handle user files in :file:`listener/old/` without the ``oxContext`` attribute.

Deprecated
----------

``oxTimeZone`` and ``oxLanguage`` remain available as UDM attributes,
but the *OX Connector* no longer evaluates them.
It uses the values from the app settings instead.

``oxDisplayName`` remains available and is evaluated.
A later version will use a user's original ``displayName`` value.

.. _app-changelog-v2.1.4:

v2.1.4
======

Released: 31. May 2023

**This version has been revoked**

.. _app-changelog-v2.1.3:

v2.1.3
======

Released: 21. April 2023

Fixed
-----

Changes to the ``oxAccessUSM`` attribute are now considered by the provisioning logic.

Changed
-------

Added a helper script that removes old listener files for users
with an empty ``oxContextIDNum`` attribute.

Removed ``bindpwd`` uses from ``createextattr.py`` script, see :uv:bug:`55985`.

.. _app-changelog-v2.1.2:

v2.1.2
======

Released: 4. April 2023

Changed
-------

Updated the ``inst`` script for compatibility with the App Center *OX App Suite*.

.. _app-changelog-v2.1.1:

v2.1.1
======

Released: 9. December 2022

Fixed
-----

Fixed a bug that prevented users from creating OX users
in the Univention Management Console.

.. _app-changelog-v2.1.0:

v2.1.0
======

Released: 14. November 2022

Fixed
-----

Removed the unnecessary ``gid_ox`` syntax for OX group names.
All valid group names in UCS are now accepted in OX.

Avoided an unnecessary group ``change`` operation that can fail for large groups
and cause the *OX Connector* to repeatedly try to delete an already deleted
user.

Changed the ``oxcontext`` ``contextid`` syntax from a string to an integer.

Changed
-------

Refactored the internal project structure.

Updated scripts and internal files.

Added
-----

Prepared support for Univention *OX App Suite*.

.. _app-changelog-v2.0.1:

v2.0.1
======

Released: 9. September 2022

Fixed
-----

Avoided unnecessary OX database lookups when synchronizing groups.
The OX Connector treats users that aren't in the database as absent
without performing a second lookup.

Avoided 500 log messages in OX by checking that users exist before looking them up.

.. _app-changelog-v2.0.0:

v2.0.0
======

Released: 26. April 2022

Added
-----

.. index::
   pair: functional mailbox; changelog
   single: udm modules; oxmail/functional_account

With OX App Suite 7.10.6 Open-Xchange added *Functional Mailboxes* to OX App Suite,
see :cite:t:`ox-app-suite-features-7-6-10`.
OX App Suite shares functional mailboxes among other users in the same context.

For more information, see :ref:`ox-connector-usage-functional-accounts`.

.. _app-changelog-v1.1.0:

v1.1.0
======

Added
-----

.. index::
   pair: access profiles; changelog
   single: udm modules; oxmail/accessprofile

OX App Suite supports access rights and can grant them individually to users.
The *OX Connector App* supports *access profiles* through the
:file:`ModuleAccessDefinitions.properties` file.

The connector generates the file locally on the UCS system
each time an administrator modifies objects in the Univention Directory Manager module ``oxmail/accessprofile``.
It doesn't provision the data to *OX App Suite* directly.
The *OX Connector* uses the *access profiles*
and sets the attribute ``oxAccess`` during provisioning.

For limitations, see :ref:`ox-connector-limitations-access-profiles-rights`.
