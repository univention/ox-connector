OX Provisioning App
===================

A provisioning App that connects UCS' IDM with OX' database. This is done via the App Center's listener integration and OX' SOAP API.

The App itself is a Docker container that brings nothing but the files needed to speak to the SOAP server.

* App name: `TODO`
* AppID: `ox-connector`

Scope
-----

The following UDM objects are covered:

* Contexts
* Users
* Groups
* Resources


Dev
---

How to build the container:

`./build_docker_image`

Preferrably on the UCS you want to install the App on (see Install)

Release
-------

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

Install
-------

For now, follow docker build instructions in Dev. Then

`univention-app install ox-connector --do-not-pull`


Install OX on UCS
-----------------

The whole point is to decouple OX and the integration. Yet, we want to run against a real OX. Setup a (different?) UCS server with OX:

```
ucr set ox/joinscript/skip=yes ox/listener/enabled=false
univention-app install oxseforucs
```

Tests
-----

There shall be a lot of tests. These can be executed like this:

```
univention-app shell ox-connector
cd /usr/local/share/oxconnector/tests/
py.test context.py
```
