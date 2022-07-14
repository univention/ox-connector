.. _app-architecture:

************
Architecture
************

The :program:`OX Connector` app architecture consists of the following elements:

* The operating environment |UCS| with the App Center and the Docker engine
  running OX Connector.

* The OX Connector software inside a Docker image.

* The OpenLDAP LDAP directory in UCS as identity management source for OX App
  Suite.

.. _architecture-overview:

Overview
========

The :program:`OX Connector` app consists of a Docker image with all the software
needed to provision user identities from |UCS| identity management to OX App
Suite. The OX connector connects to the OX App Suite SOAP API and creates, updates,
or deletes object entries in OX App Suite depending on what changed in the UCS
LDAP directory with relevance to OX App Suite.

.. figure:: /images/architecture.*
   :alt: OX Connector app architecture

   OX Connector app architecture

   View focuses on the elements LDAP Directory, Listener, Listener Converter, OX
   Connector with the provisioning script, OX App Suite, and its SOAP API.


.. glossary::

   LDAP
      The OpenLDAP software provides the *LDAP* directory in |UCS|. The LDAP
      directory stores all identity and infrastructure data of the UCS domain. For
      more information, see :ref:`domain-ldap` in :cite:t:`ucs-manual`.

   Listener
      The App Center creates a *Listener* module for the :program:`OX Connector`
      app, when it installs the app on a |UCS| system. The *Listener* writes the
      ``entryUUID`` of the LDAP object that changed, in JSON format to
      :file:`/var/lib/univention-appcenter/listener/ox-connector/{timestamp}.json`.
      Each change creates one file.

      .. index::
         pair: listener; JSON
         see: files; JSON

   Listener Converter
      The *Listener Converter* is a services running on |UCS| with the following
      responsibility:

      #. Process the JSON files from the :term:`Listener` ordered by the
         timestamp in the filename.
      #. Request the LDAP object attributes through |UDM| for each
         ``entryUUID``.

      The converter writes the results in JSON format to
      :file:`/var/lib/univention-appcenter/apps/ox-connector/data/listener/{timestamp}.json`.

      .. index::
         pair: listener converter; JSON
         see: files; JSON

   OX Connector
      *OX Connector* connects the |UCS| identity management with OX App Suite.
      The connector receives data about changes in the LDAP directory. A
      :term:`Script` handles the data, processes it and sends it to the
      :term:`SOAP API` in OX App Suite.

   Script
      The *Script* runs inside the Docker container of the OX Connector. It
      handles the files in JSON format from the :term:`Listener Converter`,
      processes it and sends data to the :term:`SOAP API`.

      The *Script* doesn't run multiple times at the same time.

      It exits upon the first failed :term:`SOAP API` request and repeats once
      the :term:`Listener Converter` triggers the *Script*.

   OX App Suite
      *OX App Suite* is the groupware and collaboration software from Open-Xchange.

   SOAP API
      OX App Suite uses `SOAP <https://en.wikipedia.org/wiki/SOAP>`_ as network
      protocol to receive data and run remote procedure calls. The connector uses
      the SOAP API to create, update, or delete object entries in OX App Suite.

.. _app-how-it-works:

How the connector works
=======================

.. index::
   single: udm modules
   single: provisioning
   see:  synchronization; provisioning
   see: UDM; udm modules
   single: udm modules; users/user
   single: udm modules; groups/group
   single: udm modules; oxmail/oxcontext
   single: udm modules; oxresources/oxresources

The OX Connector reacts on changes in the LDAP directory in |UCS| and relies on
modules in the Univention Directory Manager (UDM) modules. |UDM| is a layer on top
of the LDAP directory in UCS.

UCS provides the following UDM modules:

* ``users/user``
* ``groups/group``

The OX Connector provides the following UDM modules:

* ``oxmail/oxcontext``
* ``oxresources/oxresources``
* ``oxmail/accessprofile``

The OX Connector reacts on changes to the listed UDM modules and sends data to the
SOAP API in OX App Suite.

.. _connector-access-profiles:

Access profiles
---------------

.. index::
   single: udm modules; oxmail/accessprofile

Upon changes in the UDM module ``oxmail/accessprofile``, the connector rewrites
the local file
:file:`/var/lib/univention-appcenter/apps/ox-connector/data/ModuleAccessDefinitions.properties`
and doesn't send data to the SOAP API in OX App Suite. The module handles the
user rights and roles in OX App Suite. Administrators find the *access profiles*
in UMC in the module LDAP directory at :menuselection:`open-xchange -->
accessprofile`.

.. _connector-provisioning:

Provisioning
------------

In detail, the provisioning has the following steps, see
:numref:`sync-procedure`:

.. index::
   single: provisioning; procedure

.. _sync-procedure:

.. figure:: /images/sync-procedure.*
   :alt: provisioning procedure

   Provisioning procedure

#. The :term:`Listener` writes one file per change.

#. The :term:`Listener Converter` writes one file per change with the LDAP object
   attributes.

#. The *Listener Converter* triggers the :term:`Script` in the OX Connector
   Docker container.

#. In the Docker container, the :term:`Script` iterates over the JSON files from
   the :term:`Listener Converter`.

#. After the :term:`SOAP API` received the data and processed them successfully,
   the *Script* deletes each JSON file.

#. The *Listener Converter* waits for 5 seconds and restarts the at step 2.

For more information about the file contents of the :term:`Listener` and
:term:`Listener Converter`, see :ref:`architecture-overview`.

.. _synced-attributes:

Provisioned attributes
======================

.. index::
   pair: provisioning; attributes

The :program:`OX Connector` provisions a lot of attributes to OX App Suite. A
detailed description is beyond the scope of this document.

The OX Connector comes with the source code. The user attributes for
provisioning locate in the function :py:func:`update_user()` in
:file:`univention-ox-provisioning/univention/ox/provisioning/users.py` inside
the Docker container. To view the attributes, for example with :program:`vim`,
run the following command on the UCS system with OX Connector installed. Replace
:samp:`$version` with the proper Python version used in the Connector:

.. code-block:: console
   :caption: Example for how to view the definition of provisioned attributes.

   $ univention-app shell ox-connector \
     cat /usr/lib/python"$version"/site-packages/univention/ox/provisioning/users.py \
     | vim -

Likewise, the attributes for groups, context, and resources locate in the
respective source files in the ``update_*()`` function.

.. _cache-internal-id:

Cache
=====

.. index::
   single: cache
   single: OX App Suite; internal ID
   single: cache; directory
   pair: JSON; cache

.. versionadded:: 2.0.0

:term:`OX App Suite` creates an *internal ID* for every user object it creates
or updates. The OX Connector saves this *internal ID* in the JSON files, when it
processed the objects without errors. The connector doesn't store that ID in the
UCS LDAP directory, but maintains a file based cache on *internal ID*\ s created
by OX App Suite.

The directory for the JSON files is
:file:`var/lib/univention-appcenter/apps/ox-connector/data/listener/old/`.

When the :term:`Listener Converter` updates groups in OX App Suite, the request
to the :term:`SOAP API` must include the internal ID of all group members. The
connector would need to ask the database of OX App Suite for the *internal ID*
of each group member, involving network requests and database queries. To speed
up the processing, the OX Connector uses the *internal ID* from the cache.
