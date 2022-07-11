.. _doc-entry:

##############################
OX Connector app documentation
##############################

Welcome to the documentation about the :program:`OX Connector` app. The app
installs a connector to provision selected users and groups to a remote OX App
Suite installation through the OX SOAP API. The app **doesn't** install OX App
Suite to |UCS|.

This document addresses system administrators, who:

* operate |UCS| and OX App Suite.
* want to centrally manage users and groups in |UCS|.
* want to provision permitted users to OX App Suite.

This document covers the following topics:

#. :ref:`app-installation` about prerequisites and how to install with web
   browser and command-line.

#. :ref:`app-configuration` with a reference list about the app settings of the
   OX Connector app.

#. :ref:`app-architecture` of the app, how the connector works and the connector
   cache.

#. :ref:`app-limitations` of the app.

#. :ref:`app-troubleshooting` about log files, health check, queuing and rebuild
   the cache.

#. :ref:`app-changelog` about what changed in the different app versions.

.. only:: html

   Additionally an :ref:`genindex`: List of words and associated pointers to the content.


This document doesn't cover the following topics:

* Installation, setup and usage of OX App Suite, see
  :cite:t:`ox-app-suite-admin-guide`.
* Installation, setup and usage of |UCS|, see :cite:t:`ucs-manual`.

To understand this document, you need to know the following concepts and
tasks:

* Use and navigate in a remote shell on Debian GNU/Linux derivative Linux
  distributions like |UCS|. For more information, see `Shell and Basic Commands
  <deb-admin-handbook-shell_>`_ from *The Debian Administrator's Handbook*,
  :cite:t:`deb-admin-handbook-shell`.

* :ref:`Manage an app through Univention App Center
  <uv-manual:computers-softwareselection>` in :cite:t:`ucs-manual`.

Your feedback is welcome and highly appreciated. If you have comments,
suggestions, or criticism, please `send your feedback
<https://www.univention.com/feedback/?ox-connector=generic>`_ for document
improvement.

.. toctree::
   :hidden:
   :numbered:
   :maxdepth: 1

   installation
   configuration
   architecture
   limitations
   troubleshooting

.. toctree::
   :hidden:

   changelog
   bibliography
