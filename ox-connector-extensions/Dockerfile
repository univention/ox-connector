# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023 Univention GmbH

FROM scratch

WORKDIR /dependencies

# UDM hooks, syntax and handlers
COPY udm /dependencies/

# UMC icons and po/xml
COPY umc /dependencies/

# LDAP schemas
COPY ldap /dependencies/

# Extended attributes
COPY share/attrlist.csv /dependencies/share/attrlist.csv
