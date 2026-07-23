.. SPDX-FileCopyrightText: 2021 - 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _app-installation:

************
Installation
************

The :program:`OX Connector` app connects the UCS identity management with the OX
App Suite database. For more information about how it works, see
:ref:`app-how-it-works`.

.. _app-prerequisites:

Prerequisites
=============

.. index::
   see: installation; prerequisites
   single: prerequisites

The prerequisites moved to the consolidated *OX Connector for Nubus* manual.
For current prerequisite information,
see :external+uv-ox-connector:ref:`ox-connector-prerequisites`.

.. _prerequisite-ox-app-suite:

OX App Suite server
-------------------

.. index::
   single: prerequisites; OX App Suite

This section moved to the consolidated *OX Connector for Nubus* manual.
For current prerequisite information,
see :external+uv-ox-connector:ref:`prerequisites-ox-app-suite`.

.. _prerequisite-ucs-domain:

UCS domain
----------

.. index::
   single: prerequisites; ucs domain

This section moved to the consolidated *OX Connector for Nubus* manual.
For current prerequisite information,
see :external+uv-ox-connector:ref:`prerequisites-app-center`.

.. _install-on-ucs:

Installation on UCS system
==========================

As administrator, you can install the :program:`OX Connector` app like any other
app from Univention App Center.
Make sure to fulfill the prerequisites in
:external+uv-ox-connector:ref:`ox-connector-prerequisites`.

UCS offers two different ways for app installation:

* With the web browser in the UCS management system

* With the command-line

For general information about Univention App Center and how to use it for software
installation, see :ref:`uv-manual:software-appcenter` in :cite:t:`ucs-manual`.

.. _install-with-browser:

With the web browser
--------------------

.. index::
   single: installation; with web browser

To install :program:`OX Connector` from the UCS management system, use the
following steps:

#. Use a web browser and sign in to the UCS management system.

#. Open the *App Center*.

#. Select or search for *OX Connector* and open the app with a click.

#. To install the OX Connector, click :guilabel:`Install`.

#. Adjust the *App settings* to your preferences. For a reference, see
   :ref:`app-configuration`.

#. To start the installation, click :guilabel:`Start Installation`.

.. note::

   .. index::
      pair: installation; administrator
      pair: installation; domain admins

   To install apps, the user account you choose for login to the UCS management
   system must have domain administration rights, for example the username
   ``Administrator``. User accounts with domain administration rights belong to
   the user group ``Domain Admins``.

   For more information, see :ref:`uv-manual:delegated-administration` in
   :cite:t:`ucs-manual`.

.. _install-with-command-line:

With the command-line
---------------------

.. index::
   single: installation; with command-line

.. highlight:: console

To install the :program:`OX Connector` app from the command-line, use the following
steps:

#. Sign in to a terminal or remote shell with a username with administration
   rights, for example ``root``.

#. Adjust the settings to your preferences with the appropriate installation
   command. For a reference, see :ref:`app-configuration`. To pass customized
   settings to the app during installation, see the following command template:

   .. code-block::

      $ univention-app install ox-connector --set $SETTING_KEY=$SETTING_VALUE

   **Example**:

   .. code-block::

      $ univention-app install ox-connector --set \
        OX_MASTER_ADMIN="oxadminmaster" \
        OX_MASTER_PASSWORD="some secure password" \
        LOCAL_TIMEZONE="Europe/Berlin"` \
        OX_LANGUAGE="de_DE" \
        DEFAULT_CONTEXT="10" \
        OX_SMTP_SERVER="smtp://my-smtp.example.com:587" \
        OX_IMAP_SERVER="imap://my-imap.example.com:143" \
        OX_SOAP_SERVER="https://my-ox.example.com"


   .. note::

      The installation process asks for the password of the domain administrator
      ``Administrator``. To use another username and password for installation,
      pass different values with the options ``--username`` and ``--pwdfile``.
      For more information, see :command:`univention-app install -h`.
