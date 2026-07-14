#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2023-2026 Univention GmbH

# Source provisioning env file if present
APP_CONF="/var/lib/univention-appcenter/apps/ox-connector/conf"
PROVISIONING_ENV="$APP_CONF/provisioning.env"
if [[ -f "$PROVISIONING_ENV" ]]; then
    echo "Sourcing provisioning env from $PROVISIONING_ENV"
    set -a
    source "$PROVISIONING_ENV"
    set +a
fi

python3 "/var/lib/univention-appcenter/apps/${APP_ID}/data/resources/migrate-credentials-file.py" /var/lib/univention-appcenter/apps/${APP_ID}/data/secrets/*.secret

if [[ -d "/var/lib/univention-appcenter/apps/${APP_ID}/data/conf/ca-certificates" ]]; then
  cp /var/lib/univention-appcenter/apps/"${APP_ID}"/data/conf/ca-certificates/* "/usr/local/share/ca-certificates/"
fi

old_db_path="/var/lib/univention-appcenter/apps/${APP_ID}/data/listener/ox-connector.db"
new_db_path="/var/lib/univention-appcenter/apps/${APP_ID}/data/ox-connector.db"
if [[ -f "${old_db_path}" ]]; then
  echo "Moving databse do new location"
  mv "${old_db_path}" "${new_db_path}"
  rm -Rf "/var/lib/univention-appcenter/apps/${APP_ID}/data/listener/"
fi

python3 -c "from univention.ox.provisioning.db import initialize_db; initialize_db(set_permissions=True)"

update-ca-certificates

# Write credentials file for univention/ox/soap/config.py
python3 <<EOF
import os
import json

ox_credentials_file = os.environ["OX_CREDENTIALS_FILE"]
ox_master_admin = os.environ["OX_MASTER_ADMIN"]
ox_master_password = os.environ["OX_MASTER_PASSWORD"]

if os.path.exists(ox_credentials_file):
  content = json.load(open(ox_credentials_file))
else:
  content = {}

content["master"] = {
  "adminuser": ox_master_admin,
  "adminpass": ox_master_password,
}

os.makedirs(os.path.dirname(ox_credentials_file), exist_ok=True)
json.dump(content, open(ox_credentials_file + ".tmp", "w"), sort_keys=True, indent=2)
os.rename(ox_credentials_file + ".tmp", ox_credentials_file)
EOF

exec "$@"
