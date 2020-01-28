OX Provisioning App
===================

A provisioning App that connects UCS' IDM with OX' database. This is done via the App Center's listener integration and OX' SOAP API.

The App itself is a Docker container that brings nothing but the files needed to speak to the SOAP server.

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

`docker build . -t "ox-listener:1.0"`
