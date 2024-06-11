# SouvAP provisioning

## Start a sovereign-workplace environment with deployed tests

This process is expected to be run before releasing a new version. See the
current tests status at the bottom of this file to compare your test run. It is
recommended to keep an eye on it during development.

1. Having [tilt](https://tilt.dev/) installed in your machine.

2. Configure `gaia` cluster in your `~/.kube/config`. Steps for doing so are in the DevOps Wiki at [K8s-cluster-legacy](https://gitlab.souvap-univention.de/groups/souvap/devops/-/wikis/K8s-cluster-legacy#gaia-development-cluster-for-univention-souvap-dev-team).

3. Create your own branch `<username>/tests` in the [sovereign-workplace](https://gitlab.souvap-univention.de/souvap/devops/sovereign-workplace) repository.

4. [Run a pipeline](https://gitlab.souvap-univention.de/souvap/devops/sovereign-workplace/-/pipelines/new?ref=<your-username>/tests&var[NAMESPACE]=uv-<your-username>&var[CLUSTER]=gaia&var[BASE_DOMAIN]=open-desk.cloud&var[ENV_STOP_BEFORE]=yes&var[DEPLOY_SERVICES]=yes&var[DEPLOY_UCS]=yes&var[DEPLOY_PROVISIONING]=yes&var[DEPLOY_KEYCLOAK]=yes&var[DEPLOY_OX]=yes&var[RUN_TESTS]=no) on your branch with the following variable values:
    * `NAMESPACE`: `uv-<your-username>`
    * `CLUSTER`: `gaia` (this cluster is meant for SouvAP developers)
    * `BASE_DOMAIN`: `open-desk.cloud`
    * `ENV_STOP_BEFORE`: `yes` (only if you want to fresh start and already have things on your namespace)
    * `DEPLOY_SERVICES`: `yes` this will deploy the basic services such as clamAV
    * `DEPLOY_UCS`: `yes`
    * `DEPLOY_PROVISIONING`: `yes` (this will deploy the `ox-connector`)
    * `DEPLOY_KEYCLOAK`: `yes`
    * `DEPLOY_OX`: `yes``
    * `RUN_TESTS`: `no` (this would run the tests for everything deployed if enabled, but we will manually test our component)

5. Retrive secrets from the newly created deployment with `kubectl --namespace="uv-<your-username>" describe ConfigMap ox-connector > configmap.ox-connector.txt` or `helmfile-docker write-values --namespace="uv-<your-username>"` (in the `sovereign-workplace` repo)

6. In `helm/ox-connector/` copy `tilt_values.yaml.example` to `tilt_values.yaml` and add the missing secrets. (The example has been created by combining `values-oxconnector.yaml` and `values-oxconnector.gotmpl` from `sovereign-workplace/helmfile/apps/provisioning/`.)

7. The standalone `ox-connector` image used in the stack does not
include tests. Since it is a multi-staged build, there is a build-target to includ the
tests. The Tiltfile defines a custom parameter to change the target to `test` with `tilt up --stream=true -- --target="test"`.
(See all custom parameters with `tilt up --stream=true -- --help"`
Instead of using paramters you could rename `tilt_config.json.example` to `tilt_config.json`. (see [more on tilt](https://tilt.dev/))


## Hotfix UCS container

This needs to be run on every deployment to run the tests, since UDM REST API is causing issues on the UCS container due to the `oxContext` field. More debugging needs to be done here, but it is out of the scope for now.

1. Make sure the right Kubernetes credentials are in `~/.kube/config`. See above!
2. Find your Namespace with `kubectl get namespaces`
3. Find the `univention-corporate-container` Pod with `kubectl --namespace=<your-namespace> get pods`
4. Get a shell with `kubectl --namespace=uv-<your-username> exec --stdin --tty <pod-name> -- /bin/bash`
5. Edit the `module.py` with `vim /usr/lib/python3/dist-packages/univention/admin/rest/module.py`
6. Modify the `def set_properties()` function by adding two after line 3437 to decode bytes:
```diff
--- /usr/lib/python3/dist-packages/univention/admin/rest/module.py.orig
+++ /usr/lib/python3/dist-packages/univention/admin/rest/module.py
@@ -3434,7 +3434,11 @@
         if representation['policies']:
             obj.policies = functools.reduce(lambda x, y: x + y, representation['policies'].values())
         try:
+            MODULE.debug(representation['properties'])
             properties = PropertiesSanitizer(_copy_value=False).sanitize(representation['properties'], module=module, obj=obj)
+            if isinstance(properties.get("oxContext"), bytes):
+                properties["oxContext"] = properties["oxContext"].decode()
+            MODULE.debug(properties)
         except MultiValidationError as exc:
             multi_error = exc
             properties = representation['properties']
```
7. Restart the UDM-REST-Service with `systemctl restart univention-directory-manager-rest`

> To help debugging tests, having a look at `/var/log/univention/directory-manager-rest.log` may come in handy. Execute `tail --follow --lines=100 /var/log/univention/directory-manager-rest.log` on that pod.

## Running the tests

1. Get a shell with `kubectl --namespace=uv-<your-username> exec --stdin --tty ox-connector-0 -- /bin/bash`
1. You need a fresh `ModuleAccessDefinitions.properties` to run the tests, so do the following to keep the permissions untouched:
`echo "" > /var/lib/univention-appcenter/apps/ox-connector/data/ModuleAccessDefinitions.properties`
2. Run the tests as follows: 
#### For Jenkins UCS, or use PORTAL_HOST instead of LDAP_MASTER for other environments
`TESTS_UDM_ADMIN_USERNAME="someuser" TESTS_UDM_ADMIN_PASSWORD="somepassword" LDAP_MASTER="" LDAP_BASE="dc=swp-ldap,dc=internal" python3 -m pytest -l -vvv tests`
3. Inspect the listener logs if failures take place: `/var/log/univention/listener_modules/listener_handler.log`
4. Empty the file and re-run until needed: `echo "" > /var/log/univention/listener_modules/listener_handler.log`

> Notice this tests cannot really be run by unit, since they kind of run in cascade.

## Tests status

Currently known to fail tests are:
- `tests/test_group.py`
    - `test_change_context_for_group_user`
    - `test_change_context_for_group_multi_user`
- `tests/test_cache.py`
- `tests/test_user_attribute_mapping.py`

> This fails are due to OX configuration on SouvAP deployment not allowing
> for usernames to be changed, as well as displaynames (since they are already
taken). A ticked should exist targeting this issues if this part of the document
is in place.
