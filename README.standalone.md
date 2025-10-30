# Nubus provisioning

This document describes the process to QA the `ox-connector` in a Kubernetes
environment.

## Helm

### Helm unittests

You can run the helm unittests with the following command:

```sh
docker compose -f helm/docker-compose.yaml run --rm test
```

## Test via Nubus and OX Lab deployment

The testing is fully automated within the pipeline in the following files:

- [`./.gitlab-ci/deploy-and-test.yaml`](./.gitlab-ci/deploy-and-test.yaml)
- [`./.gitlab-ci/deploy-ox-lab.yaml`](./.gitlab-ci/deploy-ox-lab.yaml)

The pipeline supports a variable `SKIP_TESTRUN` so that it can be used to create
a deployment.

The tests can run in three different ways:

- In the production image.

  This requires modifications of the *StatefulSet* and also copying the tests
  into the container.

- In the test image.

  This requires modifications of the *StatefulSet*.

  Tests are included in the image already. In case you changed the tests, then
  they have to be copied into the container if you want to run them this way.

- Via the Kubernetes API.

  This allows to run against an unmodified production setup. We have seen some
  instabilities in this approach. It works well for running only some tests, but
  it does not deliver stable results when running the full test suite.

  Pytest has to be run with the parameter `--k8s` in this case.

## Test via openDesk deployment

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

All tests which need tweaking for Kubernetes have been marked with the marker
`k8s_skip`. They are by default deselected based on the condition `-m "not
k8s_skip"`.

The current status can be inspected in the output of the job
`collect-k8s-skip-tests` and locally with the following command:

```
pytest --k8s --collect-only -m k8s_skip tests
```

This does require a deployment currently because the `test_deputy_permission.py`
module does initialize the OX SOAP client during collection already.

### Status as of 2025-10-30

The following test cases are currently known to fail and marked with `k8s_skip`:

```
<Dir connector>
  <Dir tests>
    <Module test_cache.py>
      <Function test_missing_user_cache_entry_gets_reloaded_during_group_creation>
    <Module test_deputy_permission.py>
      <Function test_create_deputy_permission[00000-00000-True]>
      <Function test_create_deputy_permission[00000-00000-False]>
    <Module test_functional_account_setting.py>
      <Function test_functional_account_default_container>
    <Module test_group.py>
      <Function test_change_context_for_group_multi_user>
      <Function test_change_context_for_group_user>
    <Module test_resource.py>
      <Function test_unset_all_attributes_resource>
    <Module test_user.py>
      <Function test_modify_context_admin[False]>
      <Function test_modify_context_admin[True]>
```
