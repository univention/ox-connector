.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-install-on-ucs:

Install on Nubus for UCS
========================

As an administrator,
you can install the *OX Connector* app
with Univention App Center.

Before you start,
make sure that your environment meets the :ref:`prerequisites-app-center`.
Identify the required app settings.

You can install the app in Nubus for UCS in the following ways:

* Install with a web browser through the *Management UI*.
  See :ref:`ox-connector-install-on-ucs-with-browser`.

* Install from the command line on Nubus for UCS.
  See :ref:`ox-connector-install-on-ucs-with-command-line`.

.. seealso::

   :external+uv-ucs-operation:ref:`lifecycle-app-center`
      in :cite:t:`uv-ucs-operation`
      to learn how to install apps with Univention App Center.

.. _ox-connector-install-on-ucs-with-browser:

Install with a web browser
--------------------------

.. index::
   single: installation; with web browser

To install the *OX Connector* with the *Management UI* in Nubus,
use the following steps.

.. index::
   pair: installation; administrator
   pair: installation; domain admins

Before you start,
make sure that you have a user account
with access to administrative management modules.

For more information,
see :external+uv-nubus-manual:ref:`nubus-authentication-sign-in-choose-user-account`
in :cite:t:`uv-nubus-manual`.

#. In a web browser,
   :external+uv-nubus-manual:ref:`sign in <nubus-authentication-sign-in>`
   to the *Management UI*.

#. Open the *App Center* management module.

#. Select *OX Connector*
   or search for it,
   and then open the app.

#. Click :guilabel:`Install`.

#. Configure the *App settings* for your environment.
   For a reference, see :ref:`ox-connector-configuration-ucs-app-settings`.

#. Click :guilabel:`Start Installation`.

#. Verify that App Center shows the *OX Connector* app as installed.

.. seealso::

   :external+uv-ucs-operation:ref:`lifecycle-app-center-installation`
      in :cite:t:`uv-ucs-operation`
      for information about app installations.

.. _ox-connector-install-on-ucs-with-command-line:

Install from the command line
-----------------------------

.. index::
   single: installation; with command-line

To install the *OX Connector* app from the command line,
use the following steps:

#. Open a terminal
   or connect to a remote shell.
   Use a user account that has administrative rights,
   for example ``root``.

#. Determine the app settings for your environment.
   To pass custom settings to the app during installation,
   use the command template in :numref:`ox-connector-install-on-ucs-with-command-line-listing`.

   Replace the following placeholders:

   - ``SETTING_KEY`` with the app setting name.
   - ``SETTING_VALUE`` with the value.

   For an example,
   see :numref:`ox-connector-install-on-ucs-with-command-line-example-listing`.

   For a reference, see :ref:`ox-connector-configuration-ucs-app-settings`.

#. Prepare credentials for the installation command.
   Before you run the installation command,
   make sure that you can provide the password
   for the domain administrator account,
   such as ``Administrator``.

   .. tip::

      To use a different account,
      pass the account name with ``--username``
      and the password file with ``--pwdfile``.
      For more information,
      see :command:`univention-app install -h`.

#. Install the *OX Connector* app
   with the :command:`univention-app install` command.

   The following command shows the syntax
   for passing app settings during installation.

   .. code-block:: console
      :caption: Install *OX Connector* from the command line
      :name: ox-connector-install-on-ucs-with-command-line-listing

      $ univention-app install ox-connector --set SETTING_KEY=SETTING_VALUE

   The following example shows multiple app settings
   in one installation command.

   .. code-block:: console
      :caption: Example: Set app settings for *OX Connector* during installation
      :name: ox-connector-install-on-ucs-with-command-line-example-listing

      $ univention-app install ox-connector --set \
        OX_MASTER_ADMIN="oxadminmaster" \
        OX_MASTER_PASSWORD="SECURE_PASSWORD" \
        LOCAL_TIMEZONE="Europe/Berlin" \
        OX_LANGUAGE="de_DE" \
        DEFAULT_CONTEXT="10" \
        OX_SMTP_SERVER="smtp://my-smtp.example.com:587" \
        OX_IMAP_SERVER="imap://my-imap.example.com:143" \
        OX_SOAP_SERVER="https://my-ox.example.com"

   .. caution::

      Command-line passwords can appear in the shell history or process list.
      Use this method only on a trusted system.

#. Verify that App Center shows the *OX Connector* app as installed.
   You must check the installed state in App Center.
