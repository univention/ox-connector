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

.. _app-changelog:

*********
Changelog
*********

This changelog documents all notable changes to the OX Connector app. `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`_ is the format and this
project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

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
