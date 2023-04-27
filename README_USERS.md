# OX Provisioning App

**APP VERSION 2.1.4**
**OX VERSION 7.10.6**

This App connects to UCS' Identity Management with OX' database.

It does that by running a script each time the LDAP database in UCS is changed (only on the possibly relevant changes, of course). The script calls OX' SOAP API and adds / modifies / removes entries in OX according to the entries that were changed in UCS.

More specifically, the script runs whenever something changed in the following UDM modules (UDM is UCS' layer over OpenLDAP):

* oxmail/oxcontext
* users/user
* groups/group
* oxresources/oxresources
* oxmail/accessprofile (does not hit the SOAP API, only rewrites a local file)

# Setup

## What to do in your UCS domain

The UCS Primary Node needs to have the refint LDAP module enabled. It provides referential integrity in case a user is deleted, changes the username, etc.

To do that, run the following commands on your UCS Primary Node. Note that this is not necessary if you install the App on said Node, the App will do it for you.

```shell
ucr set ldap/refint=true
service slapd restart
```

## What to do on your OX server

OX needs to allow SOAP requests. This means that connections from the UCS machine need to be allowed to `/webservices` in the web server configuration.

You need to have set up an admin user in OX (one that can create contexts). Name and password of that user will be referenced in the next section as `OX_MASTER_ADMIN` and `OX_MASTER_PASSWORD`.

## What to do on your UCS server

To install the App, do the following:

```shell
univention-app install ox-connector=2.1.4 --set \
  OX_MASTER_ADMIN="oxadminmaster"  `# the name of the "root" user in OX itself` \
  OX_MASTER_PASSWORD=""  `# the password of the ox admin` \
  LOCAL_TIMEZONE="Europe/Berlin"  `# default timezone for new users` \
  OX_LANGUAGE="de_DE"  `# default language for for new users` \
  DEFAULT_CONTEXT="10"  `# default context for users` \
  OX_SMTP_SERVER="smtp://my-smtp-server.mydomain.de:587"  `# default smtp server` \
  OX_IMAP_SERVER="imap://my-imap-server.mydomain.de:143"  `# default imap server` \
  OX_SOAP_SERVER="https://my-ox-server.mydomain.de"  `# the server where ox is installed`
```

Check if everything is set up by logging into UMC and open any user. The user module should now have a tab "Apps" where you can activate Open-Xchange and set a lot of OX specific attributes.

## The settings

The App Settings can be set during the installation (see above) or during runtime:

`univention-app configure ox-connector --set OX_IMAP_SERVER=...`

Technically, the software comes in a Docker container. When running the command above, this container is removed and reinitialized with the new settings. No data is lost as we save everything outside the container.

There are some settings that need further discussion

### OX_SOAP_SERVER

This variable describes where to look for the OX server from within the Docker container. This means that the name must be resolvable. Furthermore, if you are using HTTPS (which is highly recommended), you also need to make sure that the container may verify the certificate of the OX server. Using a self signed certificate may lead to a more complex setup. You may add your certificate and test the connection by going into the container: `univention-app shell ox-connector`.

### DEFAULT_CONTEXT

This is the ID of the "default context", i.e. the context id when adding ''new'' users to OX. This setting is still explicit, though: It is saved on the LDAP object and will not change, should you ever change the default context. In fact, to do that, it is not sufficient to change the App Setting in the App: You need to change three UDM objects, too:

```shell
udm settings/extended_attribute modify \
  --dn "cn=oxContextUser,cn=open-xchange,cn=custom attributes,cn=univention,$(ucr get ldap/base)" \
  --set default=...
udm settings/extended_attribute modify \
  --dn "cn=oxContextResource,cn=open-xchange,cn=custom attributes,cn=univention,$(ucr get ldap/base)" \
  --set default=...
udm settings/usertemplate modify \
  --dn "cn=open-xchange groupware account,cn=templates,cn=univention,$(ucr get ldap/base)" \
  --set oxContext=...
```

The Default Context is not created by the App automatically. You may add the context (see below).

# Usage

All steps are done on UCS.

## Contexts

Add a new context like this:

`udm oxmail/oxcontext create --position cn=open-xchange --set oxQuota=... --set contextid=... --set name=...`

For each context that is created by UDM, the App automatically creates a context admin and names it `oxadmin-context$id` (except for the `DEFAULT_CONTEXT`, where it is just `oxadmin`). It stores the password here: `/var/lib/univention-appcenter/apps/ox-connector/data/secrets/contexts.json`.

Unlike all other objects, adding a context requires the Master Password for OX. If you do not intend to create contexts via this App, you do not need to specify those credentials.

In that case, you need to create the contexts in OX itself and provide the credentials of these contexts in the file `/var/lib/univention-appcenter/apps/ox-connector/data/secrets/contexts.json`. The entry for context 10 looks like:

```json
{
  "10": {
    "adminpass": "s3cr3t",
    "adminuser": "oxadmin"
  }
}
```

*NEW IN 1.1.1*

This file was added in version 1.1.1 of the App. Prior to this version, passwords where stored in separate files within the same folder as `contexts.json`. A migration happens automatically upon App upgrade.

## Users

Add a new user by going into UMC's user module and use the Open Xchange user template for adding a new user. When opening a user (that is flagged as an OX user) the form will show a dedicated OX tab with a lot of specific fields.

## Group

Groups need to be activated in UDM:

`udm groups/group modify --dn ... --set isOxGroup=OK`

Groups will be automatically added to those contexts where its members are members in. If the last member of the group leaves her context, the group is deleted.

Setting `isOxGroup=Not` will remove the group from OX.

## Access profiles

*NEW IN 1.1.0*

OX knows access rights that can be granted to each user individually. The App supports these through a file called
`ModuleAccessDefinitions.properties`

It works like the file of the OX installation with the same name but it is only evaluated locally and does not need to be in sync with any file on the OX server. The file is recreated each time a UDM object of the module `oxmail/accessprofile` is modified. Users will be granted the rights according to their attribute `oxAccess`.

**ATTENTION**: The App does not evaluate if the permissions you chose are sane in that OX may reject them! Not all access rights can be combined. Check your OX documentation on this topic.

## Functional accounts

*NEW IN 2.0.0*

OX added the API to add "secondary accounts" via SOAP API with version 7.10.6. The connector can add those objects via the UDM module `oxmail/function_account`. You can create, modify, delete these objects just like groups. Technically, one secondary account is created per user added to the UDM object. Those users can now use this mail address (i.e., receive and write mails). Use cases would be an address like "helpdesk@...".

**ATTENTION**: This is the reason why you must have version 7.10.6 of OX. Otherwise the connector will not work because of missing API endpoints. If you are still using an older version of OX, you have to install an older version of the connector as well.

### Update from 1.0.x

During the update of the App from 1.0 to 1.1, we will migrate all users after creating some default permission sets. These are *none*, *webmail*, *pim*, *groupware*, *premium* (similar to the old, static choices) as well as *webmail_drive* and *pim_drive* which add OX Drive access to the former profiles.

Consequently, the user's property oxDrive has been removed.

All users that had *webmail* as their oxAccess plus oxDrive will now be changed in LDAP as they now get *webmail_drive*. This may lead to a lot of tasks for the App without really changing anything.

You can work around this auto update by doing the following

```
DIR=/var/lib/univention-appcenter/apps/ox-connector/data/resources
touch $DIR/migrate-user-access-profiles-results
# UPDATE APP - the auto migration will be disabled
python $DIR/migrate-user-access-profiles.py \
  --write \
  --file $DIR/migrate-user-access-profiles-results
less $DIR/migrate-user-access-profiles-results
```

You may actually change this file. Maybe after you set your `oxmail/accessprofile` objects correctly.

If you feel confident with the results, run the `python` command above again. This time without `--write` but with `--apply`.

## Caveats

* Installing the OX Provisioning App alongside Open Xchange in the same UCS domain may cause problems and/or confusion due to UDM modules being double registered
* Groups and Functional accounts have an implicit context id. It depends on the users they include. If a user enters or leaves a group or if they change their context, this may have an impact on their groups and accounts. While groups are synced after such a change, Functional accounts are not! In order to correct things after such an event, you would need to resync the account. See the [Queue Tooling](#resync-of-one-specific-udm-object) section. Any manual change on the UDM object also works.

# Troubleshooting

## Logging

The App logs to this file (the file is log rotated)

`/var/log/univention/listener_modules/ox-connector.log`

## When the provisioning stops working

This is likely caused by a previous change in UDM that just cannot be processed. In this case the Provisioning App does not know what to do and will just retry this one action over and over again until the problem is fixed.

You should find hints in the log file above. If this is not a temporary problem (network connection to the OX server is disrupted), you may have to take manual actions.

As a last resort, you can just delete the flawed file. Its name is in the log file and should be somewhere here:

`/var/lib/univention-appcenter/apps/ox-connector/data/listener/`

## Queue Tooling

The connector works with as described above. It saves the changed objects in JSON files. These files are queued in a directory: `/var/lib/univention-appcenter/apps/ox-connector/data/listener/`. The queue is processed by the App software inside a Docker container. As the data is transferred from UCS to the OX Connector via JSON, you can in fact manipulate the queue. There are no convenient tools for that, but as the files are rather simple, it is still possible to...

### Delete an item from the queue

If an item in the queue turns out to be unprocessable, one may remove it. Otherwise the queue processing will stop there. It is retried, but may fail every time. It can be deleted with

`rm /var/lib/univention-appcenter/apps/ox-connector/data/listener/$item.json`

(where item is the problematic file; in fact, the name is a timestamp)

### Resync of everything

This is not recommended as it may take a lot of time. But this command should re-read all UDM objects and put them in the queue in their current state.

`univention-directory-listener-ctrl resync ox-connector`

Note that this will not actively trigger any "delete" operations as only the currently existing objects are re-queued. Yet, the Connector may decide to delete objects based on the data in the JSON files (e.g., "isOxGroup = Not" in a group object).

### Resync of one specific UDM object

If somehow one change did not make it into OX, you may just trigger a resync of that one object. This snippet resyncs one user:

```shell
DN="uid=user100,cn=users,$(ucr get ldap/base)"
ENTRY_UUID="$(univention-ldapsearch -b "$DN" + | grep entryUUID | awk '{ print $2 }')"
cat > /var/lib/univention-appcenter/listener/ox-connector/$(date +%Y-%m-%d-%H-%M-%S).json <<- EOF
{
    "entry_uuid": "$ENTRY_UUID",
    "dn": "$DN",
    "object_type": "users/user",
    "command": "modify"
}
EOF
```

## Caches

*NEW IN 1.2.0*

When users are created / modified, they get an internal ID in OX' database. This ID is not present in LDAP.

When modifying a group, the request to OX needs to include the internal IDs of its members. To get these, the connector could ask the database for each of the group's members. In order to speed things up, the JSON files from the Listener are enriched by the App with that internal database ID. You can see them when examining any OX user JSON in `/var/lib/univention-appcenter/apps/ox-connector/data/listener/old/*.json` (the directory, where each successfully processed JSON file is put).

If this cache should get corrupted (e.g., the OX database was restored from a previous backup), you can do the following:

```shell
univention-app shell ox-connector
update-ox-db-cache --delete
update-ox-db-cache
```

Note that this command may be useful when updating to version 1.2.0. Older versions did not save the internal ID in the JSON files and the App would fall back to the much slower "one database lookup per user" mechanism.

Also note that renewing the cache can take a long time, depending on the amount of users you already have in your database. You can try to speed things up with `update-ox-db-cache --build-cache`. This will not retrieve one user at a time, but get all users of a context at once. Be aware that this may easily take up 1GB RAM per 10k users and may result in a lot of load on your OX server and the App itself.
