.. SPDX-FileCopyrightText: 2021 - 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _app-changelog:

*********
Changelog
*********

This changelog documents all notable changes to the OX Connector app. `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`_ is the format and this
project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

.. _app-changelog-v4.0.0:

v4.0.0
======

Released: TBA

Changed
-------

The *Docker image* of the OX Connector has been changed from *Alpine Linux* to
a *UCS Base Image*. In many cases, this should have no effect, but manual
workflows may need adjustments if you assumed certain properties of the
underlying image of the App. One striking change is the update from *Python
3.9* to *Python 3.13*.

Removed
-------

The following tools have been deleted: `rebuild-old.db`,
`remove-from-ox-db-cache`, `update-ox-db-cache`, `check_sync_status.py`,
`get_current_error.py`. They used deprecated database calls and did not work
properly. You can do all meaningful manipulation with the tool
`univention-ox-task-management`.

.. _app-changelog-v3.2.3:

v3.2.3
======

Released: 2026-07-06

Added
-----

For *OX Shared Accounts*, the following attributes are now explicitly
synchronized: `Language`, `Timezone`, `SMTP server`, `IMAP server`. They are
all taken from the global configuration of the OX Connector and cannot be
changed individually.

.. _app-changelog-v3.2.2:

v3.2.2
======

Released: 2026-06-25

Added
-----

The new setting `OX_SHARED_ACCOUNT_IDENTIFIER` can be used to adjust the name
of an *OX Shared Account*.

Fixed
-----

A safeguard when finding existing OX users before their actual creation was
broken in some cases. It always used the username of the UDM object for the
search and did not take the configured `OX_USER_IDENTIFIER` into account.

.. _app-changelog-v3.2.1:

v3.2.1
======

Released: 2026-06-10

Added
-----

Migration script for *OX Functional Accounts* into *OX Shared Accounts*.
You can now migrate your old functional account to the new shared account using the provided script.
For more information, see :ref:`usage-shared-accounts-migration`.

.. _app-changelog-v3.2.0:

v3.2.0
======

Released: 2026-05-22

Added
-----

Support for *OX Shared Accounts*.
You can now add UDM objects for shared account and corresponding shared account permissions.
For more information, see :ref:`usage-shared-accounts`.

.. _app-changelog-v3.1.0:

v3.1.0
======

Released: 2026-03-17

Removed
-------

The property `groups` in the Functional Accounts module has been removed.
Adding groups to Functional Accounts was never supported
and thus not an available option in the Univention Management Console.
The logic that still made it possible to set groups via direct Univention Directory Manager access
has been removed.

.. important::
    If groups were used as Functional Account members,
    please add their members directly to the Functional Account.
    Attempting to add a group to a Functional Account will raise an error in UDM after this update.

.. _app-changelog-v3.0.2:

v3.0.2
======

Released: 2026-03-12

Fixed
-----

Users can give deputy permissions to other users (`oxDeputyPermissionGivenTo`).
These references have to be updated on changes to that user. This was not done
in case of a move operation in LDAP. This has been fixed.

.. _app-changelog-v3.0.1:

v3.0.1
======

Released: 2025-10-06

Changed
-------

The sub-command :program:`/usr/sbin/univention-ox-connector-task-management
resync-item` can now re-sync from the morgue and from the old table.

In case of consecutive errors, the OX Connector now sleeps longer and longer
between runs. This is done to prevent log files filling up with the same error
rather quickly. The delay between runs increases with every consecutive error
up to 20 minutes.

Added
-----

Added the sub-command
:program:`/usr/sbin/univention-ox-connector-task-management
rewrite-ox-db-id`.

Added the sub-command
:program:`/usr/sbin/univention-ox-connector-task-management
export-old`.

.. _app-changelog-v3.0.0:

v3.0.0
======

Released: 2025-09-29

Changed
-------

The App now stores its queue of tasks in a `SQLite` database instead of having
all data in JSON files. This includes the tasks as well as the data of those
objects already seen. GDBM based key value stores have been removed. For now,
some helper scripts will not work anymore, namely `rebuild-old.db`,
`remove-from-ox-db-cache`, `check_sync_status.py`. Existing monitoring plugins
may need adjustments.

Migration of old data is automated but may take some time depending on your
environment.

Added
-----

The App can now be configured in a way that it *does not* stop on the first
error it encounters but instead continues to process the queue. This option is
deactivated by default, meaning the behavior does not change. Note that we may
eventually release another version and enable that feature.

.. _app-changelog-v2.3.5:

v2.3.5
======

Released: 12. August 2025

Removed
-------

The Resource manager field in the UMC has been removed. Ox resources still have that property
in UDM, and can be edited or consulted.

There are no functional changes in the application.

.. _app-changelog-v2.3.4:

v2.3.4
======

Released: 23. July 2025

Fixed
-----

Fix OX Resources UDM handler preventing the OX Connector from working with UCS 5.2-2.

.. _app-changelog-v2.3.3:

v2.3.3
======

Released: 10. June 2025

Fixed
-----

UDM now actively prevents to create an OX Context with an ID already taken by
another context.

Changed
-------

Creating a new user in OX can now convert an existing OX guest account with the
same e-mail address. Note that this requires OX 8.36.36, which is currently not
present in the App Center. Also note that this only works for creating users;
modifying users (or similar) will not have this feature. If the OX Connector
cannot send this `convertguest` flag, the old behavior applies: Guest accounts
with the same e-mail address as the user being processed will block further
processing until the error is resolved.

.. _app-changelog-v2.3.2:

v2.3.2
======

Released: 4. June 2025

Fixed
-----

To keep track of certain object states, the App uses an internal key value
store. The keys used are the distinguished names (DNs) of the LDAP objects.
These have been stored as provided in the past. From now on, the DNs are
normalized and lower-cased. Existing keys in that key value store are fixed
during upgrade. For that, the new command `univention-app shell ox-connector
rebuild-old.db` has been added.

When a user with the same name as a context admin was changed via UDM or UMC,
there was an edge case which could lead to the OX connector changing an OX
context admin in the OX database. This could lead to authorization issues for
OX context admins and hence to synchronization issues for the OX connector.

Changed
-------

In certain cases, the modification of an OX user was not immediately reflected
on OX' side, so that the Connector may not get the correct database ID. The App
now retries in these cases a few times, assuming that the data will eventually
be retrievable.

.. _app-changelog-v2.3.1:

v2.3.1
======

Released: 16. Apr 2025

Added
-----

The administrator can now specify a log level for the ox-connector, see :ref:`settings`.

Changed
-------

The app setting :envvar:`OX_CONNECTOR_LOG_LEVEL` is used to specify the log level of the ox-connector.

Fixed
-----

The syntax for the `oxContext` attribute has been changed from string to integer.


.. _app-changelog-v2.3.0:

v2.3.0
======

Released: 27. Mar 2025

Added
-----

Allow provisioning of `OX deputy permissions <https://documentation.open-xchange.com/8/middleware/permissions_and_capabilities/deputy_permission.html>`_
through the :program:`OX Connector` app.
OX deputy permissions allow a user to act on behalf of another user in OX App Suite,
providing delegated access to email and calendars.
Administrators can configure these permissions to control the level of access and actions
that deputies can perform.

The administrator can now add external ca-certificates to the container, see :ref:`additional-ca-certificates`.

Changed
-------

The app setting :envvar:`OX_IMAP_LOGIN` can contain all attribute names as placeholders.
While the connector still replaces the default value ``{}`` with the user's email address,
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

Improved error message in case app settings `OX_USER_IDENTIFIER` or
`OX_GROUP_IDENTIFIER` are not correctly configured.

Improve error message in case re-provisioning for a object is required.

Fixed
-----

The documentation wasn't explicit about setting the administrative password
in the app settings for the *OX Connector App*.

The internal key value store for tracking user objects handles the key (dn)
case insensitive now.

.. _app-changelog-v2.2.14:

v2.2.14
=======

Released: 29. Oct 2024

Changed
-------

Allow special characters for the name of the access profile.

.. _app-changelog-v2.2.13:

v2.2.13
=======

Released: 17. Sep 2024

Changed
-------

When changing an OX user in UDM, the OX attribute `default_sender_address` was
left untouched. That is because it is a user preference, not "core data". Now,
if an OX user is changed in UDM so that the `primaryMailAddress` changes and
this has been the user's `default_sender_address`, it is overwritten to the new
mail address - as this makes sense in next to all scenarios and would be
considered an error if not done automatically.

.. _app-changelog-v2.2.12:

v2.2.12
=======

Released: 28. Aug 2024

Changed
-------

You can now add LDAP containers to the list of default containers for
functional accounts and select the container before creating a new
functional account in UMC, see the :ref:`usage-functional-accounts` for more
information.

.. _app-changelog-v2.2.11:

v2.2.11
=======

Released: 23. May 2024

Changed
-------

Fixes a bug which prevents the removal of Open-Xchange contexts.

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

It's now possible to change the attribute mapping between Open-Xchange and UCS
through the script :program:`change_attribute_mapping.py`.
For more information, see :ref:`conf-user-attribute-mapping`.

.. _app-changelog-v2.2.8:

v2.2.8
======

Released: 16. January 2024

Changed
-------

The `meta.db` also stores the error message and the filename that causes the error.

Added
-----

The script `get_current_error.py` outputs a json with the contents of the `meta.db`. This json can be used to automate the app health checks.

The app settings `OX_USER_IDENTIFIER` and `OX_GROUP_IDENTIFIER` have been added. They give control over which UDM property is used as the unique
identifier for users and groups in OX.

The script `check_sync_status.py` has been added. It can be used to identify data inconsistencies between UDM, OX and the listener files.

.. _app-changelog-v2.2.7:

v2.2.7
======

Released: 7. September 2023

Changed
-------

Allow any string in `OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE` app setting to simplify SSO configurations.

Fixed
-------

Fix `OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE` empty app setting handling (Bug #56523).

Fix error in context change when modifying the context and the username in the same operation (Bug #56525).


.. _app-changelog-v2.2.6:

v2.2.6
======

Released: 18. August 2023

Changed
-------

The Functional Account login field is now configurable via the app setting `OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE`.


.. _app-changelog-v2.2.5:

v2.2.5
======

Released: 16. August 2023

Changed
-------

User context change uses the `UserCopy` service.

.. _app-changelog-v2.2.4:

v2.2.4
======

Released: 13. July 2023

Changed
-------

The `imaplogin` field is now configurable via the app setting `OX_IMAP_LOGIN`.

.. _app-changelog-v2.2.3:

v2.2.3
======

Released: 27. June 2023

Fixed
-------

Corrected a typo in the `listener_trigger` script.

.. _app-changelog-v2.2.2:

v2.2.2
======

Released: 22. June 2023

Fixed
-------

The OX-Connector now prevents a scenario in which values set by users in the App Suite app were overwritten in a wrong way.

.. _app-changelog-v2.2.1:

v2.2.1
======

Released: 07. June 2023

Changed
-------

The OX-Context of a group is no longer modifiable in the groups module of UMC since the OX-Context of a group is always derived from the OX-Contexts of its users.

.. _app-changelog-v2.2.0:

v2.2.0
======

Released: 01. June 2023

Changed
-------

Removed use of old *oxDrive* and *oxAccessUSM* UDM properties. The OX Connector only
uses the *oxmail/accessprofile* objects to control access rights.

The OX Connector does not require the *oxDisplayName* to be unique anymore.

The OX connector only sets a user's *default_sender_address*, *language*, and *timezone* when initially creating a user. Afterwards, any user can configure their settings in the OX App suite front-end.

The OX connector can handle user files in *listener/old/* without the *oxContext* attribute.

Deprecated
----------

*oxTimeZone* and *oxLanguage* still exist as UDM attributes. But they are not evaluated anymore (see above in Changed; the Connector sets these attributes to the value set in the App Settings instead).

*oxDisplayName* still exists and is evaluated. At some later version, we will use the original *displayName* of a user.

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

Changes to the *oxAccessUSM* attribute are now considered by the provisioning logic.

Changed
-------

Added helper script to remove old listener files from users with empty
*oxContextIDNum* attribute.

Removed *bindpwd* uses from *createextattr.py* script (#55985).

.. _app-changelog-v2.1.2:

v2.1.2
======

Released: 4. April 2023

Changed
-------

Changes in inst script for compatibility with App Center's OX App Suite.

.. _app-changelog-v2.1.1:

v2.1.1
======

Released: 9. December 2022

Fixed
-----

Fixed bug that prevented users from creating OX users from |UMC|.

.. _app-changelog-v2.1.0:

v2.1.0
======

Released: 14. November 2022

Fixed
-----

Remove the use of unnecessary `gid_ox` syntax for OX group names. All valid
group names in UCS are now accepted in OX.

Avoid unnecessary group `change`` operation that can fail in large groups and
lead to an infinite loop where the ox-connector tries to delete an
already deleted user.

Change `oxcontext` `contextid` syntax from string to integer.

Changed
-------

Refactor of internal project structure.

Update of scripts and internal files.

Added
-----

Prepare support for Univention OX App suite.

.. _app-changelog-v2.0.1:

v2.0.1
======

Released: 9. September 2022

Fixed
-----

Avoid unnecessary look-ups in the OX database when syncing groups: Users that
appear to not be present in the database will be treated as such instead of
double checking.

Avoid 500 log messages in OX by guarding user look-ups by an `exists` call.

.. _app-changelog-v2.0.0:

v2.0.0
======

Released: 26. April 2022

Added
-----

.. index::
   pair: functional mailbox; changelog
   single: udm modules; oxmail/functional_account

With OX App Suite 7.10.6 Open-Xchange added *Functional Mailboxes* to OX App
Suite, see :cite:t:`ox-app-suite-features-7-6-10`. OX App Suite shares
functional mailboxes among other users in the same context.

For more information, see :ref:`usage-functional-accounts`.

.. _app-changelog-v1.1.0:

v1.1.0
======

Added
-----

.. index::
   pair: access profiles; changelog
   single: udm modules; oxmail/accessprofile

OX App Suite knows access and can grant them individually to users. The
:program:`OX Connector` app supports *access profiles* through the file
:file:`ModuleAccessDefinitions.propertiers`.

The connector generates the file locally on the UCS system each time an
administrator modifies objects in the |UDM| module ``oxmail/accessprofile``. It
doesn't provision the data to OX App Suite directly. The connector uses the
*access profiles* and sets the attribute ``oxAccess`` during provisioning.

For limitations, see :ref:`limit-access-profiles`.
