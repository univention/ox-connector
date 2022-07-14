.. _app-changelog:

*********
Changelog
*********

This changelog documents all notable changes to the OX Connector app. `Keep a
Changelog <https://keepachangelog.com/en/1.0.0/>`_ is the format and this
project adheres to `Semantic Versioning <https://semver.org/spec/v2.0.0.html>`_.

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
