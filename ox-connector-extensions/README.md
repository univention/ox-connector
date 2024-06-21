# OX Connector Extensions

This creates a "package" for UDM hooks and syntaxes, LDAP schemas, UMC modules and icons...


## Description
As `container-ldap server`, `container-udm-rest`, `container-umc` and `stack-data`
will all have dependencies on this project, this is a way to package and access
them from other images in the registry without needing to copy plain text
between repositories.

The result is an image that packages and ships all the components needed by
another repositories. This image also adheres to the versioning in place for
other images in this repository.

More information can be found in [ADR-0010](https://git.knut.univention.de/univention/decision-records/-/blob/fbc84283e1655f0730a998939baac1846f38ca4f/nubus/deployment/0010-extension-bundles.md).
