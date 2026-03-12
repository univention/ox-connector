.. SPDX-FileCopyrightText: 2021 - 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _consumer-changelog:

*********
Changelog
*********

Find information about deploying *OX Consumer* for user provisioning at :ref:`user-provisioning`.
This changelog documents all notable changes to *OX Consumer*.

This project follows `Keep a Changelog <https://keepachangelog.com/en/1.0.0/>`_ format
and `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

.. _consumer-changelog-v0.36.0:

v0.36.1
=======

Released: 2026-03-12

Fixed
-----

Users can give deputy permissions to other users (`oxDeputyPermissionGivenTo`).
These references have to be updated on changes to that user. This was not done
in case of a move operation in LDAP. This has been fixed.

v0.36.0
=======

Released: 4. Mar 2026

Changed
-------

:program:`OX Consumer` now uses the UDM property ``univentionObjectIdentifier``
instead of ``entryUUID`` for the functional account login template.
A functional account is a shared mailbox and calendar that multiple users share in :program:`OX App Suite`.
If your configuration uses ``entryUUID``,
consult the documentation for :program:`OX App Suite` and :program:`Dovecot`
to update the sign-in configuration to use ``univentionObjectIdentifier``.
Without this update,
users can't sign in to newly provisioned functional accounts.

.. important::

   Before you upgrade your production environment to *OX Consumer* ``0.36.0``,
   test the update in a test environment
   and verify that users can sign in to existing
   and newly created functional accounts.

After you upgrade to *OX Consumer* ``0.36.0``, validate the following:

* Create a new functional account after the upgrade and verify that it was created successfully.
* Verify that members can access the new functional account.
* If validation fails, don't proceed with upgrading additional environments. Contact contracted support before continuing.
