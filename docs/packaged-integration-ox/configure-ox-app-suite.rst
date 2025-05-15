.. SPDX-FileCopyrightText: 2025 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _configure-ox-app-suite:

************************
Configure *OX App Suite*
************************

*OX App Suite* uses LDAP to retrieve certain attributes on the user objects directly.

How to configure LDAP and OpenID Connect in *OX App Suite* is beyond the scope of this document.

.. important::

   Although this section provides a reference for the configuration values for LDAP in *OX App Suite*,
   Univention doesn't provide support for the configuration of LDAP.

This section provides a reference for the configuration values
that operators need to configure in *OX App Suite*
to connect to the *Directory Service* in Nubus for Kubernetes.

.. _configure-ox-app-suite-ldap:

LDAP authentication
===================

This section provides some guidance on the values
that you need to choose in the LDAP authentication
configuration of *OX App Suite*.
They apply to deployments in Kubernetes cluster and on Linux server systems
and locate in the :file:`/opt/open-xchange/etc/ldapauth.properties` properties file of OX App Suite.

``java.naming.provider.url``
   URL to the LDAP server in the format :samp:`ldap://{host}:389/{baseDN}`.

   :``host``: DNS name of the *LDAP server* of Nubus for Kubernetes.

   :``baseDN``: The LDAP base DN to the *Directory Service* in Nubus for Kubernetes.
      It's the value of the template variable ``ldapBaseDn``.

``bindDN``
   The DN for the *LDAP search user*
   that looks like :samp:`uid=oxSystemUser,cn=users,{{{ ldapBaseDn }}}`.
   Replace :samp:`{{{ ldapBaseDn }}}` with your actual LDAP base DN.

``bindDNPassword``
   ``bindDNPassword`` configures the password for the *LDAP search user*
   that you configure in ``bindDN``.
   Use the same value for the password
   that you defined in :numref:`install-packaged-integration-helm-chart-values-listing`.

.. seealso::

   `LDAP Properties in App Suite configuration <https://documentation.open-xchange.com/components/middleware/config/8/#mode=features&feature=LDAP>`_
      for more information about configuration values regarding LDAP authentication.

   `Configuration in openDesk <https://gitlab.opencode.de/bmi/opendesk/deployment/opendesk/-/blob/174c73c012e911342644bdcb89d22b35be9baa36/helmfile/apps/open-xchange/values-openxchange.yaml.gotmpl#L440-L444>`_
      for an example,
      how openDesk configures LDAP in a Kubernetes installation of OX App Suite.

.. _configure-ox-app-suite-context-id:

Lookup of user's context id
===========================

Every user account in OX App Suite belongs to a context.
During the sign-in procedure, OX App Suite needs to determine the user's OX context.
The following configuration example shows the context ID lookup
through the mail mapping.

`com.openexchange.mailmapping.ldap.contextIdAttribute <https://documentation.open-xchange.com/components/middleware/config/8/#mode=search&term=com.openexchange.mailmapping.ldap.contextIdAttribute>`_
  The OX packaged integration defines the LDAP attribute ``oxContextIDNum``
  for holding the context ID.
  Use the LDAP attribute name as value for the configuration here.

`com.openexchange.mailmapping.ldap.contextNameAttribute <https://documentation.open-xchange.com/components/middleware/config/8/#mode=search&term=com.openexchange.mailmapping.ldap.contextNameAttribute>`_
   Use the LDAP attribute ``oxContextName`` as value for the configuration here.
   It contains the context name.

.. seealso::

   `Mail Properties in App Suite configuration <https://documentation.open-xchange.com/components/middleware/config/8/#mode=features&feature=Mail>`_
      for more information about configuration values regarding mail configuration.
