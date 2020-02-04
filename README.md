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

```
ucr set ox/joinscript/skip=yes ox/listener/enabled=false
univention-app install oxseforucs
```

*IMPORTANT!*

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


### Build

How to build the container. On a UCS:

```
GIT_SSL_NO_VERIFY=1 git clone https://git.knut.univention.de/univention/open-xchange/provisioning.git
cd provisioning
./build_docker_image
# creates docker-test-upload.software-univention.de/ox-connector:1.0.0
```

(This checks out certain submodules. There are some flaws when the submodules branch changes. You may need to remove and re-clone the whole repository sometimes?)

### Install during Development Phase

For now, follow docker build instructions in Build. Then

```
#univention-app dev-set ox-connector DockerImage=docker-test-upload.software-univention.de/ox-connector:1.0.0 Volumes=ox-connector:/  # tbd
univention-app install ox-connector --do-not-pull --set OX_MASTER_PASSWORD="$(cat /etc/ox-secrets/master.secret)"
service univention-directory-manager-rest reload  # Bug 50253
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
cd /usr/local/share/oxconnector/tests/
py.test context.py
```

## Release

Build and push the container:

```bash
$ rsync -av -n --delete --exclude .git --exclude appsuite --exclude __pycache__ ./ root@docker.knut.univention.de:ox-provisioning/
# All OK? Then repeat the above command with the '-n'.
$ ssh root@docker.knut.univention.de
$ cd ox-provisioning
$ ./build_docker_image --release --push
```

Transfer Appcenter configuration to App Provider Portal:

```bash
./push_config_to_appcenter
```

