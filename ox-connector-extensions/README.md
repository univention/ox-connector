# OX Connector Extensions

This creates a "package" for UDM hooks and syntaxes, LDAP schemas, UMC modules and icons...


## Description
As `container-ldap server`, `container-udm-rest`, `container-umc` and `stack-data`
will all have dependencies on this project, this is a way to package and access
them from other images in the registry without needing to copy plain text
between repositories.

The result is a 9kB image that packages and ships all the components needed by
another repositories. This image also adheres to the versioning in place for
other images in this repository.
