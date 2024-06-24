#!/bin/sh
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2024 Univention GmbH

echo "Copying the plugins into the target"
cp -av /plugins/udm-hooks.d /target/admin-hooks.d
cp -av /plugins/udm-syntax.d /target/admin-syntax.d
cp -av /plugins/udm-handlers /target/admin-handlers
cp -av /plugins/umc-icons /target/umc-icons

cp -av /plugins/umc-modules/ /target/umc-modules
cp -av /plugins/ldap-schema/ /target/ldap-schema
