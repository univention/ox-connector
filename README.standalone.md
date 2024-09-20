# Nubus provisioning

This document describes the process to QA the `ox-connector` in an openDesk
environment.

## Start an openDesk environment

This process is expected to be run before releasing a new version. See the
current tests status at the bottom of this file to compare your test run. It is
recommended to keep an eye on it during development.

1. Configure `gaia` cluster in your `~/.kube/config`. You may ask a Nubus developer to provide you access.
1. Create your own branch `<username>/tests` in the [openDesk](https://gitlab.opencode.de/bmi/opendesk/deployment/opendesk/) repository.
1. [Run a pipeline](https://gitlab.opencode.de/bmi/opendesk/deployment/opendesk/-/pipelines/new) on your branch with the following variable values:
    * `NAMESPACE`: `uv-<your-username>`
    * `CLUSTER`: `uv-gaia` (this cluster is meant for Nubus developers)
    * `ENV_STOP_BEFORE`: `yes` (only if you want to fresh start and already have things on your namespace)
    * `DEPLOY_SERVICES`: `yes` this will deploy the basic services such as databases
    * `DEPLOY_UMS`: `yes`
    * `DEPLOY_PROVISIONING`: `yes` (this will deploy the `ox-connector`)
    * `DEPLOY_OX`: `yes`
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
    kubectl cp tests ox-connector-0:/tmp -n uv-<your-username>
    kubectl cp share/ ox-connector-0:/usr/local/share/ox-connector/resources/ -n uv-<your-username>
    ```
    > Make sure you are in the root of the `ox-connector` repository.
1. Grab the credentials for the `Administrator` user by running:
    ```bash
    kubectl get secret -n "uv-jconde" ums-nubus-credentials -o jsonpath='{.data.administrator_password}' | base64 -d
    ```
    > Remember to drop the `%` at the end, it is not part of the password.
1. Get a shell in the `ox-connector` pod:
    ```bash
    kubectl --namespace=uv-<your-username> \
    exec --stdin --tty ox-connector-0 -- \
    /bin/bash -c \
    'TESTS_UDM_ADMIN_USERNAME="Administrator" TESTS_UDM_ADMIN_PASSWORD="somepassword" LDAP_MASTER="portal.uv-<username>.gaia.open-desk.cloud" LDAP_BASE="dc=swp-ldap,dc=internal" python3 -m pytest -l -vvv /tmp/tests'
    ```
1. Check the logs of the `ox-connector` pod for any errors:
    ```bash
    kubectl --namespace=uv-<your-username> logs ox-connector-0
    ```

## Tests status

Currently known to fail tests are:

### test_accessprofile ❌
- tests/test_accessprofile.py::test_every_one_right_access_profile[usm-USM] FAILED
- tests/test_accessprofile.py::test_every_one_right_access_profile[activesync-activeSync] FAILED
- tests/test_accessprofile.py::test_every_one_right_access_profile[syncml-syncml] FAILED

### test/test_cache ❌
- tests/test_cache.py::test_add_user FAILED
- tests/test_cache.py::test_rename_user FAILED
- tests/test_cache.py::test_change_context FAILED

> Our cache implementation is different from the one used in the tests.
> While they save the dn as key and the path to a file as value, we store
> the whole object as value. This is why the tests are failing.

### test/test_context ✅

### test/test_function_account ✅

### test/test_functional_account_setting ❌
- tests/test_functional_account_setting.py::test_functional_account_default_container FAILED

### test/test_group ❌
- tests/test_group.py::test_change_context_for_group_multi_user FAILED
- tests/test_group.py::test_change_context_for_group_user FAILED

### tests/test_resource ✅

### tests/test_user ❌
- tests/test_user.py::test_modify_user_set_and_unset_string_attributes[organisation (5/82)] FAILED
- tests/test_user.py::test_modify_user_set_and_unset_string_attributes[oxCountryBusiness (8/82)] FAILED
- tests/test_user.py::test_modify_user_set_and_unset_string_attributes[homeTelephoneNumber (9/82)] FAILED

### tests/test_user_attribute_mapping ❌
All the tests are failing, since we do not support custom mappings.
> We do not ship nor support the file `/var/lib/univention-appcenter/apps/ox-connector/data/AttributeMapping.json`
