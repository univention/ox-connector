# OX Provisioning App

**APP VERSION 1.0.0**

This App connects to UCS' Identity Management with OX' database.

It does that by running a script each time the LDAP database in UCS is changed (only on the possibly relevant changes, of course). The script calls OX' SOAP API and adds / modifies / removes entries in OX according to the entries that were changed in UCS.

More specifically, the script runs whenever something changed in the following UDM modules (UDM is UCS' layer over OpenLDAP):

* oxmail/oxcontext
* users/user
* groups/group
* oxresources/oxresource

# Setup

## What to do on your OX server

OX needs to allow SOAP requests. This means that connections from the UCS machine need to be allowed to `/webservices` in the web server configuration.

You need to have set up an admin user in OX (one that can create contexts). Name and password of that user will be referenced in the next section as `OX_MASTER_ADMIN` and `OX_MASTER_PASSWORD`.

## What to do on your UCS server

To install the App, do the following:

```shell
# this is done because it is a preview version of the app, not yet released for the public
univention-install univention-appcenter-dev
univention-app dev-use-test-appcenter

univention-app install ox-connector=1.0.0 --set \
  OX_MASTER_ADMIN="oxadminmaster"  `# the name of the "root" user in OX itself` \
  OX_MASTER_PASSWORD=""  `# the password of the ox admin` \
  OX_CONTEXT_DEFAULT_QUOTA="1048576"  `# default quota for new contexts in MB` \
  LOCAL_TIMEZONE="Europe/Berlin"  `# default timezone for new users` \
  OX_LANGUAGE="de_DE"  `# default language for for new users` \
  DEFAULT_CONTEXT="10"  `# default context for users` \
  OX_SMTP_SERVER="smtp://my-smtp-server.mydomain.de:587"  `# default smtp server` \
  OX_IMAP_SERVER="imap://my-imap-server.mydomain.de:143"  `# default imap server` \
  OX_SOAP_SERVER="my-ox-server.mydomain.de"  `# the server where ox is installed`
```

Check if everything is set up by logging into UMC and open any user. The user module should now have a tab "Apps" where you can activate Open-Xchange and set a lot of OX specific attributes.

# Usage

All steps are done on UCS.

## Contexts

Add a new context like this:

`udm oxmail/oxcontext create cn=open-xchange --set hostname=... --set oxintegrationversion=... --set oxDBServer=... --set oxQuota=... --set contextid=... --set name=...`

But we only use `oxQuota`, `contextid`, and `name`.

For each context that is created by UDM, the App automatically creates a context admin and names it `oxadmin-context$id` (except for the `DEFAULT_CONTEXT`, where it is just `oxadmin`). It stores the password here: `/var/lib/univention-appcenter/apps/ox-connector/data/secrets/context$id`.

## Users

Add a new user by going into UMC's user module and use the Open Xchange user template for adding a new user. When opening a user (that is flagged as an OX user) the form will show a dedicated OX tab with a lot of specific fields.

## Group

Groups need to be activated in UDM:

`udm groups/group modify --dn ... --set isOxGroup=OK`

Groups will be automatically added to those contexts where its members are members in.

Setting `isOxGroup=Not` will remove the group from OX.

## What does not work at the moment?

* Changing the context of a user
* Unsetting attributes. You can only set them during creation or modify them to another value

## Caveats

* The last object state is saved on disk so that we can compute the difference between two changes. This is one file per object and may lead to slow access times if there are a lot of objects that ran at least once through the App
* The context objects can only be manipulated using the command line, we will make it accessible to UMC in the future
* OX specific UDM names are subject to change until the final release
* More specifically, we may consider dropping some OX specific attributes and use general user attributes instead
* Installing the OX Provisioning App alongside Open Xchange in the same UCS domain may cause problems and/or confusion due to UDM modules being double registered

We work on all but the last point. This may well be a caveat in the final release.

# Troubleshooting

## Logging

The App logs to this file (the file is log rotated)

`/var/log/univention/listener_modules/ox-connector.log`

## When the provisioning stops working

This is likely caused by a previous change in UDM that just cannot be processed. In this case the Provisioning App does not know what to do and will just retry this one action over and over again until the problem is fixed.

You should find hints in the log file above. If this is not a temporary problem (network connection to the OX server is disrupted), you may have to take manual actions.

As a last resort, you can just delete the flawed file. Its name is in the log file and should be somewhere here:

`/var/lib/univention-appcenter/apps/ox-connector/data/listener/`
