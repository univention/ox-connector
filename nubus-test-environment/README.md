
# Nubus deployment with the Ox extension

To add this extension to your new or existing Nubus deployment, add the content of `nubus-values.yaml` to the
`values.yaml` of your Nubus deployment.

This will install the extension, which adds the LDAP schema, udm hooks and creates the extended attributes,
creates the openxchange ldap user and a portal tile for all the domain users in the domain and a tile for
the domain admins linking to the functional mailboxes.

If you already have a Nubus deployment, you can just simply add the values to the `values.yaml` and rerun your helm
upgrade with the new values.
