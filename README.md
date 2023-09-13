# OX Provisioning App

A provisioning App that connects UCS' IDM with OX' database. This is done via the App Center's listener integration and OX' SOAP API.

The App itself is a Docker container that brings nothing but the files needed to speak to the SOAP server.

* App name: `TODO`
* AppID: `ox-connector`

## Scope

The following UDM objects are covered:

* Contexts
* Users
* Groups
* Resources

## How it works

The App Center creates a listener for the App directly on the UCS server, it is installed on, based on the following attribute in the ini file:

`ListenerUDMModules = oxmail/oxcontext, users/user`

The listener then writes on each and every change a file with only :

`/var/lib/univention-appcenter/listener/ox-connector/$timestamp.json`

Additionally, a service runs on UCS: The "listener converter". It converts the afore mentioned json file into another json file. The first file (from the listener) basically only writes the entryUUID of the object. The converter uses UDM and dumps the attribute of the object to

`/var/lib/univention-appcenter/apps/ox-connector/data/listener/$timestamp.json`

When done converting all files it found in the directory of the listener, the converter looks in its own directory: Are there any JSON files? If yes, it triggers a script in the container of the App:

```
docker cp ... /var/cache/univention-appcenter/.../ox-connector.listener_trigger:/tmp/listener_trigger`
docker exec ... /tmp/listener_trigger
```

The trigger file, shipped by the App itself, runs and shall find and process all files in `/var/lib/univention-appcenter/apps/ox-connector/data/listener/` (this directory is mounted automatically).

It has to iterate over all files it finds. Every file it processed successfully, it shall delete.

After the trigger script finishes, the converter waits 5 seconds and repeats converting files and running the trigger again (if there are new files or files from a prior, unsuccessful run of the trigger).

To summarize:

 * The App Center takes care of putting JSON files into the container
 * The files contain the information about one and only one object. It may be of Context, User, ...
 * The files are ordered by timestamp
 * The logic how to process these is in a script that runs inside the container
 * The script can process the files in order
 * The script will not run twice at the same time
 * The script exits on the first failed SOAP call. It can repeat processing the JSON file after 5 seconds because it runs again
 * Proper Queue Management is not yet implemented. But you may do `rm /var/lib/univention-appcenter/apps/ox-connector/listener/$broken.json` at any time

## Setup (Dev and QA)

The whole point is to decouple OX and the integration. Yet, we want to run against a real OX.

### Setup OX

Install the OX App Suite app on a UCS system in a separate domain. The domains
for OX App Suite and OX Connector must not be the same. Otherwise, you
encounter problems regarding LDAP schema and more.

```
#ucr set ox/joinscript/skip=yes  # we provide a join script. but we need some setup steps nonetheless (creation of the ox master admin)
ucr set ox/listener/enabled=false  # we provide the listener
# OX uses LDAP (settings) of the UCS server with the connector app:
ucr set \
    ox/cfg/authplugin.properties/com.openexchange.authentication.ucs.baseDn=dc=ucs,dc=local \
    ox/cfg/authplugin.properties/com.openexchange.authentication.ucs.bindDn=cn=testvm,cn=dc,cn=computers,dc=ucs,dc=local \
    ox/cfg/authplugin.properties/com.openexchange.authentication.ucs.ldapUrl=ldaps://testvm.ucs.local:7636 \
    ox/cfg/authplugin.properties/com.openexchange.authentication.ucs.bindPassword=s3cr3t
univention-app install oxseforucs
```

**IMPORTANT!**

The SOAP endpoints are not avaiable by default. You need to modify `/etc/apache2/conf-available/proxy_http_ox_100_appsuite.conf`. This needs to be in there:

```
<Location /webservices>
    # restrict access to the soap provisioning API
    Order Deny,Allow
    Allow from all  # <- this changed. you may want to be more subtle, but this works
    Allow from 127.0.0.1
    # you might add more ip addresses / networks here
    # Allow from 192.168 10 172.16
</Location>
```

### Setup OX connector

On the system where the OX connector app should be installed, install the UCS mail server app first::

    univention-app install mailserver

Then install the OX connector app::

    univention-app install ox-connector --set \
      OX_MASTER_ADMIN="oxadminmaster" \
      OX_MASTER_PASSWORD="s3cr3t" \
      LOCAL_TIMEZONE="Europe/Berlin" \
      OX_LANGUAGE="de_DE" \
      DEFAULT_CONTEXT="10" \
      OX_SMTP_SERVER="smtp://$(hostname -f):587" \
      OX_IMAP_SERVER="imap://$(hostname -f):143" \
      OX_SOAP_SERVER="https://my-ox-server.mydomain.de"

* The password for `OX_MASTER_PASSWORD` is the content of `/etc/ox-secrets/master.secret` on OX server.
* The mail server for `OX_SMTP_SERVER` and `OX_IMAP_SERVER` has just been installed on this host.
* The value for `OX_SOAP_SERVER` is the FQDN of the server where OX is installed.

When the app was installed, the SSL CA certificate of the OX server must be imported into the apps Docker container::

    root@m151:~# univention-app shell ox-connector
    /oxp # wget --no-check-certificate https://my-ox-server.mydomain.de/ucs-root-ca.crt -O /usr/local/share/ca-certificates/soap-server.crt
    /oxp # update-ca-certificates
    # ignore "WARNING: ca-certificates.crt does not contain exactly one certificate or CRL: skipping"

Now when users are created on the host with the OX connector app, they will have a mailbox on it, and
OX will use it.

### Build

How to build the container. On a UCS:

```
GIT_SSL_NO_VERIFY=1 git clone https://git.knut.univention.de/univention/open-xchange/provisioning.git
cd provisioning
./build_docker_image
# creates docker-test-upload.software-univention.de/ox-connector:2.2.7
```

(This checks out certain submodules. There are some flaws when the submodules branch changes. You may need to remove and re-clone the whole repository sometimes?)

### Install during Development Phase

For now, follow docker build instructions in Build. Then

```
#univention-app dev-set ox-connector DockerImage=docker-test-upload.software-univention.de/ox-connector:2.2.7 Volumes=ox-connector:/  # tbd
univention-app install ox-connector --do-not-pull --set OX_MASTER_PASSWORD="$(cat /etc/ox-secrets/master.secret)"
service univention-directory-manager-rest restart  # Bug 50253
```

### Double check

Here you can follow what the App does:

`tail -f /var/log/univention/listener_modules/ox-connector.log`

### Dev

On your laptop:

`devsync ~/git/provisioning/ /var/lib/docker/volumes/ox-connector/_data/`  # tbd

### Tests

There shall be a lot of tests. These can be executed like this:

```
univention-app shell ox-connector
python3 -m pytest -l -v tests
```

### Pre-commit

There is pre-commit running automatically on the pipeline, so make sure to
install the hooks to run before every commit.

```
pre-commit install
pre-commit run --all-files
```

Now pre-commit will run on every commit and will warn you (and apply changes)
so you can add the changes to the commit.

## Release

Besides the necessary steps for an app update, make sure to apply the following
steps **before** release of a new app version for the OX Connect app.

1. [ ] - Update the `DOC_TARGET_VERSION` variable in
   [.gitlab-ci.yml](.gitlab-ci.yml) to the new app version. The variable makes
   sure that the new app version has a dedicated documentation.

2. [ ] - Add an appropriate changelog entry to
   [docs/changelog.rst](docs/changelog.rst) and follow the recommendation at
   https://keepachangelog.com/en/1.0.0/.

3. [ ] - Update the link to the app documentation in the app description to the
   appropriate version link.

4. [ ] - Push the updated documentation to the docs.univention.de repository.
   Manually trigger the *production* in the docs pipeline.

5. [ ] - After running the *production* job for the documentation in the
   pipeline, update the symlink `latest` the new version in the
   [ox-connector-app directory of the docs.univention.de
   repository](https://git.knut.univention.de/univention/docs.univention.de/-/tree/master/ox-connector-app).

6. [ ] - To deploy the documentation, trigger the *deploy* job in the pipeline
   of the docs.univention.de repository.


Build and push the container:

```bash
$ make clean
$ rsync -av -n --delete --exclude .git --exclude appsuite --exclude __pycache__ ./ --exclude venv --exclude .pytest_cache --exclude requirements_all.txt docker.knut.univention.de:ox-provisioning/
# All OK? Then repeat the above command with the '-n'.
$ ssh docker.knut.univention.de
$ cd ox-provisioning
$ ./build_docker_image --release --push
```

Transfer Appcenter configuration to App Provider Portal:

```bash
./push_config_to_appcenter
```

## Standalone Service

In this repository you can also find an image on `Dockerfile.standalone` which
consists of the same code shipped on Univention AppCenter with some glue code
to make it work with [Univention Directory Listener](https://docs.software-univention.de/developer-reference/5.0/en/listener/index.html),since [AppCenter provisioning](https://docs.software-univention.de/app-center/5.0/en/identity_management.html#provisioning)
is not available in an stand-alone environment.

### Development setup

Please look into the [base container image](https://git.knut.univention.de/univention/customers/dataport/upx/container-listener-base#preparation)
on which Univention Directory Listener is installed. An ansible playbook is
provided there to ease the development setup.

> Note a `docker-compose.override.yaml` will be created, as well as a `secret`
and a `ssl` folder. All of them are needed for development on this repository.

## Testing

Three scenarios must be tested:

1. OX connector and OX installed in k8s (SouvWP).
2. OX connector and OX installed both in UCS by the apps `ox-connector` and `oxseforucs`.
3. OX connector installed in UCS by the app `ox-connector` and OX separately (platform irrelevant).

The test suite found in the `tests` directory can be executed in each environment using the following services:

1. TODO: Jaime: TILT at ...
2. Jenkins job that installs the OX connector (using app `ox-connector`) and OX (using app `oxseforucs`) on the same UCS primary: https://jenkins2022.knut.univention.de/job/UCS-5.0/job/UCS-5.0-4/view/all/job/product-test-component-ox-appsuite/ (replace `5.0-4` with the current stable UCS release).
3. Jenkins job that installs the OX connector app (using app `ox-connector`) on a UCS primary and OX on a Debian Buster system (another UCS primary, not joined to the 1st), using `apt-get` from OX' original repo, exactly how the OX documentation describes it. The UCS integration (`oxseforucs`) is _not_ used.: https://jenkins2022.knut.univention.de/job/UCS-5.0/job/UCS-5.0-4/view/all/job/product-test-component-ox-connector/ (replace `5.0-4` with the current stable UCS release).
