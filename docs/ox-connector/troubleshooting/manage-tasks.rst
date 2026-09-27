.. SPDX-FileCopyrightText: 2026 Univention GmbH
..
.. SPDX-License-Identifier: AGPL-3.0-only

.. _ox-connector-troubleshooting-manage-provisioning-tasks:

Manage provisioning tasks
=========================

Use the *OX Connector* command-line interface to query and manage its database.
The database tracks current tasks,
objects that the *OX Connector* has synchronized,
and errors.

.. tab-set::

   .. tab-item:: Nubus for UCS
      :sync: ucs

      On Nubus for UCS with the *OX Connector* app installed,
      you find the command-line interface at the location shown
      in :numref:`ox-connector-troubleshooting-ucs-manage-provisioning-tasks-listing`.

      .. code-block:: console
         :caption: List all commands of the CLI
         :name: ox-connector-troubleshooting-ucs-manage-provisioning-tasks-listing

         $ /usr/sbin/univention-ox-connector-task-management --help

      The tool operates on the :program:`SQLite` database
      :file:`/var/lib/univention-appcenter/apps/ox-connector/data/ox-connector.db`.
      The terminology of the tool is as follows:

   .. tab-item:: Nubus for Kubernetes
      :sync: kubernetes

      To run the :command:`univention-ox-connector-task-management` command,
      you need to use :command:`kubectl` with the *execute* action on the *OX Connector* pod.

      Replace the placeholder ``<NAMESPACE>`` with the Kubernetes namespace for the *OX Consumer*.

      Use the commands in :numref:`ox-connector-troubleshooting-kubernetes-manage-provisioning-tasks-listing`.
      The example has the pod name ``ox-connector-0``.

      .. code-block:: console
         :caption: Open a shell to the *OX Connector*
         :name: ox-connector-troubleshooting-kubernetes-manage-provisioning-tasks-listing

         $ export NAMESPACE_FOR_CONSUMER="<NAMESPACE>"
         $ kubectl \
            --namespace "$NAMESPACE_FOR_CONSUMER" \
            get pods | grep "ox-connector"
         ox-connector-0    1/1   Running   0  19h

         $ export POD_NAME_FOR_OX_CONNECTOR="ox-connector-0"
         $ kubectl \
            --namespace "$NAMESPACE_FOR_CONSUMER" \
            execute \
            --stdin \
            --tty \
            "$POD_NAME_FOR_OX_CONNECTOR" \
            -- \
            univention-ox-connector-task-management --help

.. glossary::

   Tasks
      A database table managed by the *OX Connector*.
      A row represents an active task.
      The *OX Connector* iterates over all tasks
      and synchronizes them to the *OX App Suite*.

   Old
      A database table managed by the *OX Connector*.
      A row represents the state of an item
      when the *OX Connector* successfully synchronized it.
      The row is a copy of a previous task.
      The *OX Connector* needs it when synchronizing items
      that reference other items,
      for example, groups that contain users.
      The *OX Connector* also stores the database ID assigned by OX
      so that it can look up objects faster.

   Morgue
      A database table managed by the *OX Connector*.
      A row represents a failed task.
      The *OX Connector* or an administrator moved the task to this table,
      so the *OX Connector* doesn't process it actively.
      Administrators can examine items in the morgue and decide how to proceed.

.. _ox-connector-troubleshooting-check-provisioning-health:

Check provisioning health
-------------------------

To check the provisioning health, use the following steps:

#. Inspect the log output of the *OX Connector Provisioning Consumer*.

   .. tab-set::

      .. tab-item:: Nubus for UCS
         :sync: ucs

         To check the provisioning health,
         first inspect the :ref:`log output of the OX Connector Provisioning Consumer <ox-connector-troubleshooting-ucs-log-files-consumer>`
         for warnings and errors.
         For more information, see :ref:`ox-connector-troubleshooting-ucs-log-files`.

      .. tab-item:: Nubus for Kubernetes
         :sync: kubernetes

         To check the provisioning health,
         first inspect the :ref:`log output of the OX Connector Provisioning Consumer <ox-connector-troubleshooting-kubernetes-log-files-consumer>`
         for warnings and errors.
         For more information, see :ref:`ox-connector-troubleshooting-kubernetes-log-files`.

#. Inspect the provisioning queue.
   The following listings show the commands.
   If the number of pending tasks keeps growing after a change in the LDAP directory,
   the :term:`OX Connector Provisioning Consumer`
   or the :term:`Provisioning Service` can't process tasks.

   .. tab-set::

      .. tab-item:: Nubus for UCS
         :sync: ucs

         .. code-block:: console
            :caption: Show pending tasks
            :name: ox-connector-troubleshooting-ucs-check-provisioning-health-listing

            $ /usr/sbin/univention-ox-connector-task-management summarize-tasks
            $ /usr/sbin/univention-ox-connector-task-management search-tasks

      .. tab-item:: Nubus for Kubernetes
         :sync: kubernetes

         To set the proper environment variables in the following listing,
         use the commands in
         :numref:`ox-connector-troubleshooting-kubernetes-manage-provisioning-tasks-listing`.

         .. code-block:: console
            :caption: Show pending tasks
            :name: ox-connector-troubleshooting-kubernetes-check-provisioning-health-listing

            $ kubectl \
               --namespace "$NAMESPACE_FOR_CONSUMER" \
               execute \
               --stdin \
               --tty \
               "$POD_NAME_FOR_OX_CONNECTOR" \
               -- \
               univention-ox-connector-task-management summarize-tasks

            $ kubectl \
               --namespace "$NAMESPACE_FOR_CONSUMER" \
               execute \
               --stdin \
               --tty \
               "$POD_NAME_FOR_OX_CONNECTOR" \
               -- \
               univention-ox-connector-task-management search-tasks

#. Then inspect failed tasks in the morgue.
   This is relevant only if you configured the connector to
   :ref:`ox-connector-limitations-continue-at-conflict`.

   .. tab-set::

      .. tab-item:: Nubus for UCS
         :sync: ucs

         .. code-block:: console
            :caption: Show failed tasks in the morgue
            :name: ox-connector-troubleshooting-ucs-check-provisioning-health-morgue-listing

            $ /usr/sbin/univention-ox-connector-task-management search-morgue

      .. tab-item:: Nubus for Kubernetes
         :sync: kubernetes

         To set the proper environment variables in the following listing,
         use the commands in
         :numref:`ox-connector-troubleshooting-kubernetes-manage-provisioning-tasks-listing`.

         .. code-block:: console
            :caption: Show failed tasks in the morgue
            :name: ox-connector-troubleshooting-kubernetes-check-provisioning-health-morgue-listing

            $ kubectl \
               --namespace "$NAMESPACE_FOR_CONSUMER" \
               execute \
               --stdin \
               --tty \
               "$POD_NAME_FOR_OX_CONNECTOR" \
               -- \
               univention-ox-connector-task-management search-morgue

.. _ox-connector-troubleshooting-handle-failed-tasks:

Handle failed tasks
-------------------

Decide how to handle failed tasks in the morgue.

.. tab-set::

   .. tab-item:: Nubus for UCS
      :sync: ucs

      Use :numref:`ox-connector-troubleshooting-ucs-check-provisioning-health-morgue-listing`
      to find the ``UniventionObjectIdentifier`` of the affected object.
      Replace ``OBJECT_ID`` in the following commands with this identifier.

   .. tab-item:: Nubus for Kubernetes
      :sync: kubernetes

      Use :numref:`ox-connector-troubleshooting-kubernetes-check-provisioning-health-morgue-listing`
      to find the ``UniventionObjectIdentifier`` of the affected object.
      Replace ``OBJECT_ID`` in the following commands with this identifier.

#. **Remove the task from the morgue**:
   The *OX Connector* treats the object as though it had never received the task.
   If the underlying object changes in the LDAP directory,
   the *OX Connector* can synchronize it again and create a new task.

   .. tab-set::

      .. tab-item:: Nubus for UCS
         :sync: ucs

         Run the command in :numref:`ox-connector-troubleshooting-ucs-handle-failed-tasks-remove-listing`.

         .. code-block:: console
            :caption: Remove an item from the morgue
            :name: ox-connector-troubleshooting-ucs-handle-failed-tasks-remove-listing

            $ /usr/sbin/univention-ox-connector-task-management \
               remove-from-morgue \
               --obj-id=OBJECT_ID

      .. tab-item:: Nubus for Kubernetes
         :sync: kubernetes

         Run the command in :numref:`ox-connector-troubleshooting-kubernetes-handle-failed-tasks-remove-listing`.
         To set the proper environment variables in the following listing,
         use the commands in
         :numref:`ox-connector-troubleshooting-kubernetes-manage-provisioning-tasks-listing`.

         .. code-block:: console
            :caption: Remove an item from the morgue
            :name: ox-connector-troubleshooting-kubernetes-handle-failed-tasks-remove-listing

            $ kubectl \
               --namespace "$NAMESPACE_FOR_CONSUMER" \
               execute \
               --stdin \
               --tty \
               "$POD_NAME_FOR_OX_CONNECTOR" \
               -- \
               univention-ox-connector-task-management \
               remove-from-morgue \
               --obj-id=OBJECT_ID

#. **Retry the same task**:
   After you resolve the problem,
   the *OX Connector* copies the failed task back to the task list.
   For example, you might first deactivate a validation rule in *OX App Suite*.

   .. tab-set::

      .. tab-item:: Nubus for UCS
         :sync: ucs

         Run the command in :numref:`ox-connector-troubleshooting-ucs-handle-failed-tasks-retry-listing`.

         .. code-block:: console
            :caption: Retry an item from the morgue
            :name: ox-connector-troubleshooting-ucs-handle-failed-tasks-retry-listing

            $ /usr/sbin/univention-ox-connector-task-management \
               retry-from-morgue \
               --obj-id=OBJECT_ID

      .. tab-item:: Nubus for Kubernetes
         :sync: kubernetes

         Run the command in :numref:`ox-connector-troubleshooting-kubernetes-handle-failed-tasks-retry-listing`.
         To set the proper environment variables in the following listing,
         use the commands in
         :numref:`ox-connector-troubleshooting-kubernetes-manage-provisioning-tasks-listing`.

         .. code-block:: console
            :caption: Retry an item from the morgue
            :name: ox-connector-troubleshooting-kubernetes-handle-failed-tasks-retry-listing

            $ kubectl \
               --namespace "$NAMESPACE_FOR_CONSUMER" \
               execute \
               --stdin \
               --tty \
               "$POD_NAME_FOR_OX_CONNECTOR" \
               -- \
               univention-ox-connector-task-management \
               retry-from-morgue \
               --obj-id=OBJECT_ID

#. **Resynchronize the object**:
   The *OX Connector* adds the object to the task list with its current attributes
   instead of the attributes from the failed synchronization.
   It fetches the object again from the LDAP directory.
   This works only for the first matching object,
   so asterisks might not produce the expected result.

   .. tab-set::

      .. tab-item:: Nubus for UCS
         :sync: ucs

         Run the command in :numref:`ox-connector-troubleshooting-ucs-handle-failed-tasks-resync-listing`.

         .. code-block:: console
            :caption: Re-sync an existing item through UDM
            :name: ox-connector-troubleshooting-ucs-handle-failed-tasks-resync-listing

            $ /usr/sbin/univention-ox-connector-task-management \
               resync-item \
               --obj-id=OBJECT_ID

      .. tab-item:: Nubus for Kubernetes
         :sync: kubernetes

         Run the command in :numref:`ox-connector-troubleshooting-kubernetes-handle-failed-tasks-resync-listing`.
         To set the proper environment variables in the following listing,
         use the commands in
         :numref:`ox-connector-troubleshooting-kubernetes-manage-provisioning-tasks-listing`.

         .. code-block:: console
            :caption: Re-sync an existing item through UDM
            :name: ox-connector-troubleshooting-kubernetes-handle-failed-tasks-resync-listing

            $ kubectl \
               --namespace "$NAMESPACE_FOR_CONSUMER" \
               execute \
               --stdin \
               --tty \
               "$POD_NAME_FOR_OX_CONNECTOR" \
               -- \
               univention-ox-connector-task-management \
               resync-item \
               --obj-id=OBJECT_ID

.. _ox-connector-troubleshooting-resolve-blocked-provisioning:

Resolve blocked provisioning
----------------------------

If provisioning has stopped,
a previous change in Univention Directory Manager (UDM) might be the cause.
The *OX Connector* can't process the change
and retries the action until an administrator resolves the cause.

.. tab-set::

   .. tab-item:: Nubus for UCS
      :sync: ucs

      First, see :ref:`ox-connector-troubleshooting-ucs-log-files`.
      Then look for warnings and errors.
      If the problem isn't temporary, such as a network connectivity problem,
      resolve it manually.

      As a last resort, move the task to the morgue.
      Find the task ID in the log file.
      It follows ``tasks:`` in an entry such as
      ``uid=...; OBJECT_IDENTIFIER; tasks:TASK_ID``.
      Replace ``TASK_ID`` in the command in
      :numref:`ox-connector-troubleshooting-ucs-resolve-blocked-provisioning-morgue-listing`.

      .. code-block:: console
         :caption: Move a task to the morgue
         :name: ox-connector-troubleshooting-ucs-resolve-blocked-provisioning-morgue-listing

         $ /usr/sbin/univention-ox-connector-task-management \
            move-task-to-morgue \
            --task-id=TASK_ID \
            --error-msg="Manual intervention after careful consideration"

   .. tab-item:: Nubus for Kubernetes
      :sync: kubernetes

      First, see :ref:`ox-connector-troubleshooting-kubernetes-log-files`.
      Then look for warnings and errors.
      If the problem isn't temporary, such as a network connectivity problem,
      resolve it manually.

      As a last resort, move the task to the morgue.
      Find the task ID in the log file.
      It follows ``tasks:`` in an entry such as
      ``uid=...; OBJECT_IDENTIFIER; tasks:TASK_ID``.
      Replace ``TASK_ID`` in the command in
      :numref:`ox-connector-troubleshooting-kubernetes-resolve-blocked-provisioning-morgue-listing`.

      To set the proper environment variables in the following listing,
      use the commands in
      :numref:`ox-connector-troubleshooting-kubernetes-manage-provisioning-tasks-listing`.

      .. code-block:: console
         :caption: Move a task to the morgue
         :name: ox-connector-troubleshooting-kubernetes-resolve-blocked-provisioning-morgue-listing

         $ kubectl \
            --namespace "$NAMESPACE_FOR_CONSUMER" \
            execute \
            --stdin \
            --tty \
            "$POD_NAME_FOR_OX_CONNECTOR" \
            -- \
            univention-ox-connector-task-management \
            move-task-to-morgue \
            --task-id=TASK_ID \
            --error-msg="Manual intervention after careful consideration"

.. _ox-connector-troubleshooting-reprovision-all-data:

Re-provision all data
---------------------

To re-provision all data,
recreate the *OX Connector* subscription and enable *prefill*,
as described below.
The :term:`Provisioning Service` sends existing Univention Directory Manager (UDM) objects
from subscribed modules to the *OX Connector*.
The :term:`OX Connector Provisioning Consumer` adds them to its queue.

.. warning::

   Depending on the number of users and groups in the Nubus for UCS LDAP directory,
   this task can take a long time.

   **Avoid re-provisioning all data.**


The Provisioning Service doesn't add deleted UDM objects to the queue.
Therefore, the *OX Connector* doesn't run delete operations during re-provisioning.
Previously deleted UDM objects aren't removed from OX during this procedure.

.. tab-set::

   .. tab-item:: Nubus for UCS
      :sync: ucs

      To re-provision all data,
      run the commands in :numref:`ox-connector-troubleshooting-ucs-reprovision-all-data-listing`
      on the :external+uv-ucs-operation:term:`Primary Directory Node`.
      The commands do the following:

      #. Set up configuration parameters, such as base URL, administrator password, and subscription password.

      #. Delete the existing subscription.

      #. Configure the connector subscription to subscribe to all relevant UDM modules.

      #. Create the subscription using the configuration from the JSON file.

      #. Delete the subscription configuration.

      #. Save the *Provisioning Service* credentials to a file
         in the *OX Connector* configuration directory
         and restrict the file permissions.

      #. Restart the *OX Connector* app.

      .. code-block:: console
         :caption: Re-provisioning all UDM objects to OX App Suite
         :name: ox-connector-troubleshooting-ucs-reprovision-all-data-listing

         $ export BASE_URL="https://$(ucr get ldap/master)/univention/provisioning"
         $ export ADMIN_PASSWORD="$(python3 -c 'import json; print(json.load(open("/etc/provisioning-secrets.json"))["PROVISIONING_API_ADMIN_PASSWORD"])')"
         $ export SUBSCRIPTION_PASSWORD="$(openssl rand -hex 32)"
         $ curl --user "admin:$ADMIN_PASSWORD" \
             -X DELETE "$BASE_URL/v1/subscriptions/ox-connector" || true
         $ umask 077
         $ cat > /tmp/ox-connector-subscription.json <<EOF
         {
           "name": "ox-connector",
           "realms_topics": [
             {"realm":"udm", "topic":"users/user"},
             {"realm":"udm", "topic":"groups/group"},
             {"realm":"udm", "topic":"oxmail/oxcontext"},
             {"realm":"udm", "topic":"oxmail/accessprofile"},
             {"realm":"udm", "topic":"oxresources/oxresources"},
             {"realm":"udm", "topic":"oxmail/functional_account"},
             {"realm":"udm", "topic":"oxmail/shared_account"},
             {"realm":"udm", "topic":"oxmail/shared_account_permission"}
           ],
           "request_prefill": true,
           "password": "$SUBSCRIPTION_PASSWORD"
         }
         EOF
         $ curl --fail --user "admin:$ADMIN_PASSWORD" \
             -H "Content-Type: application/json" \
             -X POST "$BASE_URL/v1/subscriptions" \
             --data @/tmp/ox-connector-subscription.json \
             || { rm -f /tmp/ox-connector-subscription.json; exit 1; }
         $ rm -f /tmp/ox-connector-subscription.json
         $ printf 'export PROVISIONING_API_USERNAME=ox-connector\nexport PROVISIONING_API_PASSWORD=%s\n' \
             "$SUBSCRIPTION_PASSWORD" \
             > /var/lib/univention-appcenter/apps/ox-connector/conf/provisioning.env
         $ chmod 640 /var/lib/univention-appcenter/apps/ox-connector/conf/provisioning.env
         $ univention-app restart ox-connector

   .. tab-item:: Nubus for Kubernetes
      :sync: kubernetes

      Before you can run the commands in
      :numref:`ox-connector-troubleshooting-kubernetes-reprovision-all-data-listing`
      you need to complete the following prerequisites:

      #. Open an access to the *Provisioning API* endpoint.
         See :external+uv-nubus-customization:ref:`customization-api-provisioning-endpoint-access`
         in :cite:t:`uv-nubus-customization`.

      #. Define the following environment variables:

         * ``NAMESPACE_FOR_CONSUMER``,
           see :numref:`ox-connector-troubleshooting-kubernetes-reprovision-all-data-provisioning-pod-name-listing`.
           Replace the placeholder ``<NAMESPACE>`` with the Kubernetes namespace for the *OX Consumer*.

         * ``POD_NAME_FOR_OX_CONNECTOR``,
           see :numref:`ox-connector-troubleshooting-kubernetes-reprovision-all-data-provisioning-pod-name-listing`.

         * ``PROVISIONING_API_ADMIN_SECRET_NAME``,
           see :numref:`ox-connector-troubleshooting-kubernetes-reprovision-all-data-provisioning-secret-listing`

         .. code-block:: console
            :name: ox-connector-troubleshooting-kubernetes-reprovision-all-data-provisioning-pod-name-listing
            :caption: Define ``POD_NAME_FOR_OX_CONNECTOR``

            $ export NAMESPACE_FOR_CONSUMER="<NAMESPACE>"
            $ kubectl \
               --namespace "$NAMESPACE_FOR_CONSUMER" \
               get pods | grep "ox-connector"
            ox-connector-0    1/1   Running   0  19h

            $ export POD_NAME_FOR_OX_CONNECTOR="ox-connector-0"

         .. code-block:: console
            :caption: Define ``PROVISIONING_API_ADMIN_SECRET_NAME``
            :name: ox-connector-troubleshooting-kubernetes-reprovision-all-data-provisioning-secret-listing

            $ kubectl \
               --namespace "$NAMESPACE_FOR_CONSUMER" \
               get secret | grep provisioning-api-admin
            ums-provisioning-api-admin    Opaque  1  73d

            $ export PROVISIONING_API_ADMIN_SECRET_NAME="ums-provisioning-api-admin"

         To re-provision all data,
         run the commands in
         :numref:`ox-connector-troubleshooting-kubernetes-reprovision-all-data-listing`.
         The commands do the following:

         #. Set up configuration parameters, such as base URL, administrator password, and subscription password.

         #. Delete the existing subscription.

         #. Configure the connector subscription to subscribe to all relevant UDM modules.

         #. Create the subscription using the configuration from the JSON file.

         #. Delete the subscription configuration.

         #. Save the *Provisioning Service* credentials to a file
            in the directory where you run the commands
            and restrict the file permissions.

         #. Recreate the pod for the *OX Connector*.

         .. code-block:: console
            :caption: Re-provisioning all UDM objects to OX App Suite
            :name: ox-connector-troubleshooting-kubernetes-reprovision-all-data-listing

            $ export BASE_URL="http://localhost:7777"
            $ export ADMIN_PASSWORD="$(kubectl \
               --namespace "$NAMESPACE_FOR_CONSUMER" \
               get secret \
               $PROVISIONING_API_ADMIN_SECRET_NAME \
               -o json \
               | jq -r ".data.password" \
               | base64 -d)"
            $ export SUBSCRIPTION_PASSWORD="$(openssl rand -hex 32)"
            $ curl --user "admin:$ADMIN_PASSWORD" \
                -X DELETE "$BASE_URL/v1/subscriptions/ox-connector" || true
            $ umask 077
            $ cat > /tmp/ox-connector-subscription.json <<EOF
            {
              "name": "ox-connector",
              "realms_topics": [
                {"realm":"udm", "topic":"users/user"},
                {"realm":"udm", "topic":"groups/group"},
                {"realm":"udm", "topic":"oxmail/oxcontext"},
                {"realm":"udm", "topic":"oxmail/accessprofile"},
                {"realm":"udm", "topic":"oxresources/oxresources"},
                {"realm":"udm", "topic":"oxmail/functional_account"},
                {"realm":"udm", "topic":"oxmail/shared_account"},
                {"realm":"udm", "topic":"oxmail/shared_account_permission"}
              ],
              "request_prefill": true,
              "password": "$SUBSCRIPTION_PASSWORD"
            }
            EOF
            $ curl --fail --user "admin:$ADMIN_PASSWORD" \
                -H "Content-Type: application/json" \
                -X POST "$BASE_URL/v1/subscriptions" \
                --data @/tmp/ox-connector-subscription.json \
                || { rm -f /tmp/ox-connector-subscription.json; exit 1; }
            $ rm -f /tmp/ox-connector-subscription.json
            $ printf 'export PROVISIONING_API_USERNAME=ox-connector\nexport PROVISIONING_API_PASSWORD=%s\n' \
                "$SUBSCRIPTION_PASSWORD" \
                > provisioning.env
            $ chmod 640 provisioning.env
            $ kubectl delete pod "$POD_NAME_FOR_OX_CONNECTOR"

.. caution::

   The *OX Connector* can delete objects based on the data that it receives.
   For example, it deletes a group object when ``isOxGroup = False``.
