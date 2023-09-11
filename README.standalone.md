# SouvAP provisioning

## Testing ox-connector on SouvAP environment

First of all you will need a SouvAP deployment on a cluster. You can get one up
and running [here](https://gitlab.souvap-univention.de/souvap/devops/sovereign-workplace/-/pipelines/new?ref=jconde/ox-connector-tests&var[NAMESPACE]=jconde&var[CLUSTER]=gaia&var[BASE_DOMAIN]=open-desk.cloud&var[DEPLOY_SERVICES]=yes&var[DEPLOY_KEYCLOAK]=yes&var[DEPLOY_UCS]=yes&var[DEPLOY_PROVISIONING]=yes&var[DEPLOY_OX]=yes&var[ENV_STOP_BEFORE]=yes&var[RUN_TESTS]=no).
If the branch does not exist, you can create one yourself.

1. Access to [DevOps gitlab](gitlab.souvap-univention.de) may need to be
requested to @trossner or @dkaminski. This will enable access with your
project's credentials.
2. On [sovereign-workplace](https://gitlab.souvap-univention.de/souvap/devops/sovereign-workplace)
you will need to create a branch (usually with no changes) to run a pipeline,
since permissions for running the main branch are reserved.
3. Run a pipeline on your branch with the following variable values:`
    * `NAMESPACE`: `<your_username>`
    * `CLUSTER`: `gaia` (this cluster is meant for SouvAP developers)
    * `BASE_DOMAIN`: `open-desk.cloud`
    * `DEPLOY_SERVICES`: `yes` this will deploy the basic services such as clamAV
    * `DEPLOY_KEYCLOAK`: `yes`
    * `DEPLOY_UCS`: `yes`
    * `DEPLOY_PROVISIONING`: `yes` (this will deploy the `ox-connector`)
    * `DEPLOY_OX`: `yes`
    * `ENV_STOP_BEFORE`: `yes` (only if you want to fresh start and already have things on your namespace)`
    * `RUN_TESTS`: `no` (this would run the tests for everything deployed if enabled, but we will manually test our component)
4. The `ox-connector` image used in the stack is standalone and does not 
include tests. Since it is a multi-staged build, there is a tag including the
tests. Therefore you will need to deploy the staged build with the tests
included. You can use `tilt up` (see [more on tilt](https://tilt.dev/)) on this
repository to do just that (first clone the [sovereign-workplace](https://gitlab.souvap-univention.de/souvap/devops/sovereign-workplace))
on the parent folder (parallel to `provisioning` repository) and change
`helmfile/apps/provisioning/values-oxconnector.yaml` with the full values
including the templated ones under `values-oxconnector.gotmpl`. If you want to
know some values and don't have access to the vault, ask @trossner or
@jconde for them.

## Hotfix UCS container

This needs to be run on every deployment to run the tests, since UDM REST API is causing issues on the UCS container due to the `oxContext` field. More debugging needs to be done here, but it is out of the scope for now.

1. `vim /usr/lib/python3/dist-packages/univention/admin/rest/module.py`
2. Edit the following on `def set_properties()` function:
```python
try:
  MODULE.debug(representation['properties'])
  properties = PropertiesSanitizer...
  if isinstance(properties.get("oxContext"), bytes):
       properties["oxContext"] = properties["oxContext"].decode()
  MODULE.debug(properties)
```
3. `systemctl restart univention-directory-manager-rest`

> To help debugging tests, having a look at `/var/log/univention/directory-manager-rest.log` may come in handy.

## Running the tests

1. You need a fresh `ModuleAccessDefinitions.properties` to run the tests, so do the following to keep the permissions untouched:
`echo "" > /var/lib/univention-appcenter/apps/ox-connector/data/ModuleAccessDefinitions.properties`
2. Run the tests as follows: `TESTS_UDM_ADMIN_USERNAME="someuser" TESTS_UDM_ADMIN_PASSWORD="somepassword" python3 -m pytest -l -vvv tests`
3. Inspect the listener logs if failures take place: `/var/log/univention/listener_modules/listener_handler.log`
4. Empty the file and re-run until needed: `echo "" > /var/log/univention/listener_modules/listener_handler.log`

> Notice this tests cannot really be run by unit, since they kind of run in cascade.

## Tests status

Currently known to fail tests are:
- `tests/test_user.py`
    - `test_rename_user`
    - `test_remove_user`
    - `test_enable_and_disable_user`
    - `test_change_context`
    - `test_existing_user_in_different_context`
- `tests/test_resource.py`
    - `test_modify_resource`
    - `test_remove_resource`
    - `test_change_context_resource`
- `tests/test_group.py`
    - `test_modify_group`
    - `test_rename_user`
    - `test_change_context_for_group_user`
    - `test_change_context_for_group_multi_user`

> This fails are due to OX configuration on SouvAP deployment not allowing
> for usernames to be changed, as well as displaynames (since they are already
taken). A ticked should exist targeting this issues if this part of the document
is in place.
