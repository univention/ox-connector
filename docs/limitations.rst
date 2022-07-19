.. _app-limitations:

***********
Limitations
***********

To ensure a smooth operation of the :program:`OX Connector` app on UCS, you as
administrator need to know the following limitations.

.. _limit-ox-app-suite-app:

Incompatible OX Connector and OX App Suite app
==============================================

Univention doesn't support the use of :program:`OX Connector` towards the
:program:`OX App Suite` app from Univention App Center. Both apps use different
and incompatible approaches to provision objects to the database of OX App
Suite.

The OX Connector requires that the OX App Suite **isn't and was never**
installed on any UCS system in your domain. Otherwise, the UCS LDAP still has
schema files installed that conflict with the schema files from the OX
Connector.

.. _limit-stop-at-conflict:

OX Connector stops at faulty items
==================================

When the :program:`OX Connector` encounters a faulty queue item that it can't
process, it stops the provisioning at the item and logs the filename with its
path in the :term:`Listener Converter` log file, see :ref:`log-files`.

Despite the stop, the :term:`Listener` continues to add items to the queue.
After the administrator removed the faulty queue item, the Listener Converter
continues to process the queue and also takes care of the added items.

As administrator, you need to resolve that conflict manually when it happens,
see :ref:`provision-stopped`. After the conflict resolution, the connector
continues to process the provisioning queue.

.. admonition:: Design decision

   The OX Connector doesn't provide logic to resolve conflicts automatically,
   because the conflict causes can vary a lot. For example, when connector would
   ignore the conflict and continue, a later operation may refer to the ignored
   item. The connector can't complete it, because the current queue item refers
   to a previous, unprocessed item. The OX Connector could ignore the next
   conflict again, and again. The ignores pile up unresolved conflicts that can
   lead to a heavy conflict or a serious problem with the user provisioning
   without any relation to the actual root cause. Administrators would have
   quite a hard job to resolve the conflict.

.. _limit-access-profiles:

No plausibility validation in access profile rights
===================================================

The :program:`OX Connector` app doesn't evaluate permission level for created
*access profiles* and tries to create any access profile.

For more information, see `OX App Suite Permission Level
<https://oxpedia.org/wiki/index.php?title=AppSuite:Permission_Level>`_.

The OX Connector already provides ready-to-use *access profiles* for OX App Suite
users. Administrators can create custom *access profiles* in UMC in the *LDAP
directory* module at :menuselection:`Domain --> LDAP directory` at the directory
location ``open-xchange/accessprofiles/``.
