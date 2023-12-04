.. SPDX-FileCopyrightText: 2021-2023 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _app-changelog:

*********
Changelog
*********

This changelog documents all notable changes to the OX Connector app. `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`_ is the format and this
project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

2.2.8
=============

Released: 15. December 2023

Changed
-------
The `meta.db` also stores the error message and the filename that causes the error.

Added
-----
The script `get_current_error.py` outputs a json with the contents of the `meta.db`. This json can be used to automate the app health checks.

2.2.7
=============

Released: 7. September 2023

Changed
-------

Allow any string in `OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE` app setting to simplify SSO configurations.

Fixed
-------

Fix `OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE` empty app setting handling (Bug #56523).

Fix error in context change when modifying the context and the username in the same operation (Bug #56525).


2.2.6
=============

Released: 18. August 2023

Changed
-------

The Functional Account login field is now configurable via the app setting `OX_FUNCTIONAL_ACCOUNT_LOGIN_TEMPLATE`.


2.2.5
=============

Released: 16. August 2023

Changed
-------

User context change uses the `UserCopy` service.

2.2.4
=============

Released: 13. July 2023

Changed
-------

The `imaplogin` field is now configurable via the app setting `OX_IMAP_LOGIN`.

2.2.3
=============

Released: 27. June 2023

Fixed
-------

Corrected a typo in the `listener_trigger` script.

2.2.2
=============

Released: 22. June 2023

Fixed
-------

The OX-Connector now prevents a scenario in which values set by users in the App Suite app were overwritten in a wrong way.

2.2.1
=============

Released: 07. June 2023

Changed
-------

The OX-Context of a group is no longer modifiable in the groups module of UMC since the OX-Context of a group is always derived from the OX-Contexts of its users.

2.2.0
=============

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

2.1.4
=====

Released: 31. May 2023

**This version has been revoked**

2.1.3
=====

Released: 21. April 2023

Fixed
-------
Changes to the *oxAccessUSM* attribute are now considered by the provisioning logic.

Changed
-------

Added helper script to remove old listener files from users with empty
*oxContextIDNum* attribute.

Removed *bindpwd* uses from *createextattr.py* script (#55985).

2.1.2
=====

Released: 4. April 2023

Changed
-------

Changes in inst script for compatibility with App Center's OX App Suite.

2.1.1
=====

Released: 9. December 2022

Fixed
-----

Fixed bug that prevented users from creating OX users from |UMC|.

2.1.0
=====

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

2.0.1
=====

Released: 9. September 2022

Fixed
-----

Avoid unnecessary look-ups in the OX database when syncing groups: Users that
appear to not be present in the database will be treated as such instead of
double checking.

Avoid 500 log messages in OX by guarding user look-ups by an `exists` call.

2.0.0
=====

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


1.1.0
=====

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
