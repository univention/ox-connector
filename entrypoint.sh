#!/bin/bash

# Abort on nonzero exitstatus
set -o errexit
# Abort on unbound variable
set -o nounset
# Don't hide errors within pipes
set -o pipefail

# Prepare Univention Directory Listener configuration
export PYTHON_DIST_PACKAGES="/usr/local/lib/python3.7/dist-packages"
. /listener-base-entrypoint.sh

# Set sane defaults for some optional variables
export DOMAINNAME="${DOMAINNAME:-}"
export OX_MASTER_ADMIN="${OX_MASTER_ADMIN:-}"
export OX_MASTER_PASSWORD="${OX_MASTER_PASSWORD:-}"
export LOCAL_TIMEZONE="${LOCAL_TIMEZONE:-Europe/Berlin}"
export OX_LANGUAGE="${OX_LANGUAGE:-de_DE}"
export DEFAULT_CONTEXT="${DEFAULT_CONTEXT:-10}"
export OX_SMTP_SERVER="${OX_SMTP_SERVER:-}"
export OX_IMAP_SERVER="${OX_IMAP_SERVER:-}"
export OX_SOAP_SERVER="${OX_SOAP_SERVER:-}"
export OX_CREDENTIALS_FILE="${OX_CREDENTIALS_FILE:-/etc/ox-secrets/ox-contexts.json}"

# Test variables which should not be empty
check_required_variables() {
  var_names=(
    "DOMAINNAME"
    "OX_MASTER_ADMIN"
    "OX_MASTER_PASSWORD"
    "OX_SMTP_SERVER"
    "OX_IMAP_SERVER"
    "OX_SOAP_SERVER"
  )
  for var_name in "${var_names[@]}"; do
    if [[ -z "${!var_name:-}" ]]; then
      echo "ERROR: '${var_name}' is unset."
      var_unset=true
    fi
  done

  if [[ -n "${var_unset:-}" ]]; then
    exit 1
  fi
}
check_required_variables

# For test-code in univention/ox/provisioning/__init__.py:run
touch /tmp/test.log && \
chmod 777 /tmp/test.log && \

# Write credentials file for univention/ox/soap/config.py
JSON_STRING=$(
  jq \
    --null-input \
    --arg con "master" \
    --arg user "${OX_MASTER_ADMIN}" \
    --arg pass "${OX_MASTER_PASSWORD}" \
    '{"$con": {adminuser: $user, adminpass: $pass}}'
  )
echo "${JSON_STRING}" > "${OX_CREDENTIALS_FILE}"

exec "$@"