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

1. Checkout opendesk `git@gitlab.opencode.de:bmi/opendesk/deployment/opendesk.git`
1. Create custom config for ox-connector `ox-connector-customization.yaml.gotmpl` in opendesk root folder
    ```
    openXchange:
      # Debug logging is required for tests to get the correct event from the logs
      logLevel: "DEBUG"
      oxDeputyPermissions: true
    ```
1. Create config in opendesk repo `helmfiles/environments/dev/gaia-values.yaml.gotmpl`.
    ```
    ---
    ingress:
      ingressClassName: nginx
    functional:
      authentication:
        twoFactor:
          groups:
            - foo
      externalServices:
        nubus:
          udmRestApi:
            enabled: true
    certificate:
      issuerRef:
        name: letsencrypt-prod-dns
      wildcard: false

    global:
      imagePullPolicy: "Always"
      domain: <namespace>.univention.dev

    # use your test image here when working on a feature branch
    images:
      oxConnector:
        registry: "artifacts.software-univention.de"
        repository: "nubus-dev/images/ox-connector-standalone"
        tag: "0.36.0"

    # enable debug logging and deputy permissions
    customization:
      release:
        oxConnector:
          writableTmpDir: "../../../ox-connector-customization.yaml.gotmpl"

    # running the tests needs some memory
    resources:
      oxConnector:
        limits:
          memory: "3Gi"

    apps:
      cassandra:
        enabled: false
      certificates:
        enabled: true
      clamavDistributed:
        enabled: false
      clamavSimple:
        enabled: false
      collabora:
        enabled: false
      collaboraController:
        enabled: false
      cryptpad:
        enabled: false
      dkimpy:
        enabled: false
      dovecot:
        enabled: true
      element:
        enabled: false
      elementAdmin:
        enabled: false
      elementGroupsync:
        enabled: false
      home:
        enabled: true
      jitsi:
        enabled: false
      mariadb:
        enabled: true
      memcached:
        enabled: true
      migrations:
        enabled: true
      minio:
        enabled: true
      nextcloud:
        enabled: false
      notes:
        enabled: false
      nubus:
        enabled: true
      openproject:
        enabled: false
      oxAppSuite:
        enabled: true
      postfix:
        enabled: true
      postgresql:
        enabled: true
      redis:
        enabled: true
      staticFiles:
        enabled: true
      xwiki:
        enabled: false
    ```
1. Deploy opendesk to gaia `MASTER_PASSWORD="univention" helmfile apply -e dev -n jburgmeier-ox`
1. Run your local tests against the remote k8s deploymend (this is the same mechanism used by the CI tests)
    ```bash
    docker compose run --remove-orphans --rm -ti \
      -e K8S_NAMESPACE="jburgmeier-ox" \
      -e LDAP_BASE="dc=swp-ldap,dc=internal" \
      -e OX_SOAP_SERVER="https://webmail.<namespace>univention.dev" \
      -e DEFAULT_CONTEXT=1 \
      -e TESTS_UDM_ADMIN_USERNAME="Administrator" \
      -e TESTS_UDM_ADMIN_PASSWORD="<some_password>" \
      -e DOMAINNAME="<namespace>.univention.dev" \
      -e PORTAL_HOST="portal.<namespace>.univention.dev" \
      -e LDAP_MASTER="portal.<namespace>.univention.dev" \
    k8s-tests -m "not k8s_skip"
    ```

## Tests status

All tests which need tweaking for Kubernetes have been marked with the marker
`k8s_skip`. They are by default deselected based on the condition `-m "not
k8s_skip"`.

The current status can be inspected in the output of the job
`collect-k8s-skip-tests` and locally with the following command:

```
docker compose run --rm -ti k8s-tests --k8s --collect-only -m k8s_skip tests
```

All deputy permissions test are currently disabled because checking if
deputy permissions are enabled in the deployment is not yet implemented for
k8s backends.

All attribute mapping tests are currently disabled because uploading the
generated `AttributeMapping.json` file is not implemented yet for k8s. It
would require to enhance the `FileUtility` implementation to upload files.

### Status as of 2026-03-13

The following test cases are currently known to fail and marked with `k8s_skip`:

```
<Dir test-env>
  <Dir tests>
    <Module test_functional_account_setting.py>
      <Function test_functional_account_default_container>
    <Module test_group.py>
      <Function test_change_context_for_group_multi_user>
        If a user changes the oxContext, the group needs to update its members
        in the old and in the new context
      <Function test_change_context_for_group_user>
        If a user changes the oxContext, the group should be removed from the old
        context and created in the new context
    <Module test_user.py>
      <Function test_modify_context_admin[True]>
        Adding/Modifying a user with the same name as an OX context admin
        is to be ignored as e.g. writing the password hash of the LDAP
        user into OX will break the authentication from the ox-connector side
      <Function test_existing_user_in_different_context>
        User already exists in OX DB (legacy data?) and a new
        user with the same name is created in UDM. First a another
        context; then the user is moved to the original context
```

 - `test_modify_context_admin[True]>`: Manipulating the OX cache does not work in k8s
 - `test_existing_user_in_different_context`: When log streaming fails log gathering fallsback to polling,
   and in the test we wait for the same dn in to subsequent occosions it might be that
   the first log line is also hit by the second wait. Adding a sleep made the test work, but to fix it
   properly the polling fallback should ignore lines which already provided a hit for a wait.
 - `test_change_context_for_group_multi_user` and `test_change_context_for_group_user`:
   During a context move the old group is deleted because it is empty now but the new gr oup is not created.
   Might be an actual bug in the k8s implementation.

   From the logs:
    ```
    2026-03-13 13:37:01,458 INFO  [backend.remove:271] Deleted user 'user105' in context 104 (id=3).
    2026-03-13 13:37:01,459 INFO  [users.delete_user:557] User was deleted, searching for now empty groups
    2026-03-13 13:37:01,459 INFO  [users.delete_user:559] Found group users with 2 members
    2026-03-13 13:37:01,459 INFO  [users.delete_user:559] Found group group103 with 1 members
    2026-03-13 13:37:01,459 INFO  [users.delete_user:564] Thus, deleting group 4 in 104...
    2026-03-13 13:37:01,512 DEBUG [connectionpool._make_request:452] http://open-xchange-core-mw-admin.jburgmeier-ox.svc.cluster.local:80 "POST /webservices/OXGroupService HTTP/1.1" 200 109
    2026-03-13 13:37:01,513 DEBUG [__init__.run:158] Processed: uid=user105,cn=users,dc=swp-ldap,dc=internal
    2026-03-13 13:37:01,513 INFO  [consumer.modify:386] Updating object OX ID in known objects from 104 to 106
    2026-03-13 13:37:01,514 INFO  [consumer.modify:397] Updating object OX DB ID in known objects from None to 3
    2026-03-13 13:37:01,514 DEBUG [consumer.modify:418] Finished MODIFY of 'users/user' 'uid=user105,cn=users,dc=swp-ldap,dc=internal' ('uid=user105,cn=users,dc=swp-ldap,dc=internal') in 2395.9 ms.
    ```
  - `test_functional_account_default_container`: Maybe some configuration problem
    ```
    E           udm_rest.UnprocessableEntity: PUT https://portal.jburgmeier-ox.univention.dev/univention/udm/settings/directory/cn%3Ddefault%20containers%2Ccn%3Dunivention%2Cdc%3Dswp-ldap%2Cdc%3Dinternal: 422
    E           1 error(s) occurred:
    E           Request argument "ox_functional_accounts" The Preferences: Default Container module has no property ox_functional_accounts.
    ```
