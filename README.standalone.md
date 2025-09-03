# Nubus provisioning

This document describes the process to QA the `ox-connector` in an openDesk
environment.

## Start an openDesk environment

This process is expected to be run before releasing a new version. See the
current tests status at the bottom of this file to compare your test run. It is
recommended to keep an eye on it during development.

1. Configure `zendis` cluster in your `~/.kube/config`. You may ask a Nubus developer to provide you access.
1. Create your own branch `<username>/tests` in the [openDesk](https://gitlab.opencode.de/bmi/opendesk/deployment/opendesk/) repository.
1. [Run a pipeline](https://gitlab.opencode.de/bmi/opendesk/deployment/opendesk/-/pipelines/new) on your branch with the following variable values:
    * `NAMESPACE`: `uv-<your-username>`
    * `CLUSTER`: `dev` (this cluster is meant for Zendis developers)
    * `ENV_STOP_BEFORE`: `yes` (only if you want to fresh start and already have things on your namespace)
    * `DEBUG_ENABLE`: `yes`
    * `DEPLOY_SERVICES`: `yes` this will deploy the basic services such as databases
    * `DEPLOY_UMS`: `yes`
    * `DEPLOY_ELEMENT`: `yes` (for testing integrations with ox)
    * `DEPLOY_OX`: `yes` (this will deploy the `ox-connector`)
    * `DEPLOY_NEXTCLOUD`: `yes` (for testing integrations with ox)
1. Install the dependencies and prepare the environment:
    ```bash
    kubectl --namespace=uv-<your-username> \
    exec -it ox-connector-0 -- \
    /bin/bash -c \
    'python3 -m pip install pytest uritemplate --break-system-packages; mkdir -p /usr/local/share/ox-connector/resources/'
    ```
1. The standalone `ox-connector` image used in the deployment does not include
tests, so you need to copy them:
    ```bash
    kubectl cp tests ox-connector-0:/ -n uv-<your-username>
    kubectl cp share/ ox-connector-0:/usr/local/share/ox-connector/resources/ -n uv-<your-username>
    ```
    > Make sure you are in the root of the `ox-connector` repository. 

1. As an alternative to step 4 and 5, you could modify your statefulset to use the `ox-connector-standalone-test` image, that already includes test and test dependencies.
Remember to increase the resources of the pod to at least `4Gi` memory. Also, it's mandatory to mount an `emptyDir` in `/tmp`.
It is also recommended to set the pyest dir to a writeabke location, for example subdir of `/tmp`, otherwise the consumer might crash with authentication errors.

1. Grab the credentials for the `Administrator` user by running:
    ```bash
    kubectl get secret -n "uv-<your-username>" ums-nubus-credentials -o jsonpath='{.data.administrator_password}' | base64 -d
    ```
    > Remember to drop the `%` at the end if you are using zsh - it is not part of the password.
1. Get a shell in the `ox-connector` pod:
    ```bash
    kubectl --namespace=uv-<your-username> \
    exec --stdin --tty ox-connector-0 -- \
    /bin/bash -c \
    'TESTS_UDM_ADMIN_USERNAME="Administrator" TESTS_UDM_ADMIN_PASSWORD="somepassword" STANDALONE_KUBERNETES_TESTS=1 LDAP_MASTER="portal.uv-<username>.opendesk.site" LDAP_BASE="dc=swp-ldap,dc=internal" python3 -m pytest -o cache_dir=/tmp/.pytest_cache -l -vvv /tests'
    ```
1. Check the logs of the `ox-connector` pod for any errors:
    ```bash
    kubectl --namespace=uv-<your-username> logs ox-connector-0
    ```

## Tests status

FYI: Executing the test as explained before, leads to some leftovers in the system, as users/ id ,etc.
It's higly recomended to execute them in a fresh deployment.  

Currently known to fail tests are:

### test_accessprofile ✅

### test/test_cache ✅

Our cache implementation is different from the one used in the tests.
While they save the dn as key and the path to a file as value, we store
the whole object as value. This is why the tests are failing.

The tests can be run with `STANDALONE_KUBERNETES_TESTS=1` to use the correct caching
but for the `tests/test_cache.py::test_create_group_with_user_not_in_cache` test to succeed
the `consumer.py` must also be started with `DEBUG_RELOAD_OX_DB_ID=1` to allow manipulating the
cache from outside.

### test/test_context ✅

### test/test_function_account ✅

### test/test_functional_account_setting ❌
```
FAILED tests/test_functional_account_setting.py::test_functional_account_default_container - udm_rest.UnprocessableEntity: PUT https://portal.uv-jconde.opendesk.site/univention/udm/settings/directory/cn%3Ddefault%20containers%2Ccn%3Dunivention%2Cdc%3Dswp-ldap%2Cdc%3Dinternal: 422
1 error(s) occurred:
Request argument "ox_functional_accounts" The Preferences: Default Container module has no property ox_functional_accounts.
```

### test/test_group ❌
```
FAILED tests/test_group.py::test_change_context_for_group_multi_user - Failed: Listener_trigger did NOT handle cn=group304,cn=groups,dc=swp-ldap,dc=internal for 60.0 seconds.
FAILED tests/test_group.py::test_change_context_for_group_user - Failed: Listener_trigger did NOT handle cn=group311,cn=groups,dc=swp-ldap,dc=internal for 60.0 seconds.
```

> For some reason, the wait_for_listener is timing out when listening for the group changes.

### tests/test_resource ✅

### tests/test_user ❌
```
FAILED tests/test_user.py::test_modify_context_admin[True] - FileNotFoundError: [Errno 2] No such file or directory: 'update-ox-db-cache'
```

### tests/test_user_attribute_mapping ❌
All the tests are failing, since we do not support custom mappings.
> We do not ship nor support the file `/var/lib/univention-appcenter/apps/ox-connector/data/AttributeMapping.json`
