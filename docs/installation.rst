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

Before you as administrator can install the :program:`OX Connector` app, you
need to make sure that your environment fulfills the prerequisites.

.. _prerequisite-ox-app-suite:

OX App Suite server
-------------------

.. index::
   single: prerequisites; ox app suite

For the *OX App Suite* server, you must ensure the following prerequisites:

#. The environment requires an installed OX App Suite instance. This
   documentation assumes that an OX App Suite installation already exists.

   For limitations about the :program:`OX App Suite` app from Univention App
   Center and the connector, see :ref:`limit-ox-app-suite-app`.

   For installation of OX App Suite, see :cite:t:`ox-app-suite-admin-guide`.

#. The OX App Suite instance must allow SOAP requests, so that the UCS system,
   where the :ref:`administrator installs the OX Connector app
   <install-on-ucs>`, can connect to ``/webservices``.

#. You have to set up an administrator user in OX App Suite that can create OX
   contexts.

   The OX Connector can manage OX contexts. The installation of the :program:`OX
   Connector` app needs username and password for that user and references them
   in the setting :envvar:`OX_MASTER_ADMIN` and :envvar:`OX_MASTER_PASSWORD`.

   For manually managing OX contexts without the OX Connector, see
   :ref:`usage-contexts`.

.. _prerequisite-ucs-domain:

UCS domain
----------

Another prerequisite needs some steps in the UCS domain. To use the :program:`OX
Connector` app, the central LDAP directory needs the *referential integrity*
overlay enabled. The overlay ensures that UDM objects provided by the OX
Connector keep their integrity and always reference user objects correctly in
the LDAP directory.

.. tab:: OX Connector on |UCSPRIMARYDN|

   .. index::
      single: ox connector; primary directory node
      single: installation; primary directory node

   If you install :program:`OX Connector` on |UCSPRIMARYDN|, the app already
   takes care of the necessary step. No further action required.

.. tab:: OX Connector on other system roles

   .. index::
      single: ox connector; other system roles
      single: installation; other system roles

   If you install :program:`OX Connector` on other :ref:`uv-manual:system-roles`
   than the |UCSPRIMARYDN|, you need to run the following commands:

   .. code-block:: console
      :caption: Activate OpenLDAP *referential integrity* overlay on |UCSPRIMARYDN|.
      :name: prerequisite-activate-referential-integrity-overlay

      $ ucr set ldap/refint=true
      $ service slapd restart

For more information about the *referential integrity* overlay, see
:cite:t:`openldap-referential-integrity-overlay`.

.. _install-on-ucs:

Installation on UCS system
==========================

As administrator, you can install the :program:`OX Connector` app like any other
app with Univention App Center. Make sure to fulfill the
:ref:`app-prerequisites`.

UCS offers two different ways for app installation:

* With the web browser in the UCS management system

* With the command-line

For general information about Univention App Center and how to use it for software
installation, see :ref:`uv-manual:software-appcenter` in :cite:t:`ucs-manual`.

.. _install-with-browser:

With the web browser
--------------------

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

   To install apps, the user account you choose for login to the UCS management
   system must have domain administration rights, for example the username
   ``Administrator``. User accounts with domain administration rights belong to
   the user group ``Domain Admins``.

   For more information, see :ref:`uv-manual:delegated-administration` in
   :cite:t:`ucs-manual`.

.. _install-with-command-line:

With the command-line
---------------------

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
