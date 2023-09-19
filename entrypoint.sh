#!/bin/bash

# Abort on nonzero exitstatus [-e]
set -o errexit
# Abort on unbound variable [-u]
set -o nounset
# Don't hide errors within pipes
set -o pipefail

# Set sane defaults for some optional variables
export DOMAINNAME="${DOMAINNAME:-}"
export OX_MASTER_ADMIN="${OX_MASTER_ADMIN:-}"
export OX_MASTER_PASSWORD="${OX_MASTER_PASSWORD:-}"
export LOCAL_TIMEZONE="${LOCAL_TIMEZONE:-Europe/Berlin}"
export OX_LANGUAGE="${OX_LANGUAGE:-de_DE}"
export DEFAULT_CONTEXT="${DEFAULT_CONTEXT:-1}"
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

mkdir -p "/var/lib/univention-appcenter/apps/ox-connector/data/listener"
chown -R "listener:root" "/var/lib/univention-appcenter/apps/ox-connector/data"
chmod -R "0744" "/var/lib/univention-appcenter/apps/ox-connector/data"

# Write credentials file for univention/ox/soap/config.py
JSON_STRING=$(
  jq \
    --null-input \
    --arg user "${OX_MASTER_ADMIN}" \
    --arg pass "${OX_MASTER_PASSWORD}" \
    '{"master": {adminuser: $user, adminpass: $pass}}'
  )

if [[ ! -f "${OX_CREDENTIALS_FILE}" ]]; then
  mkdir --parents "/etc/ox-secrets"
  echo "${JSON_STRING}" > "${OX_CREDENTIALS_FILE}"
fi
chown "listener:root" "${OX_CREDENTIALS_FILE}"
chmod "0600" "${OX_CREDENTIALS_FILE}"


echo "starting listener with access profiles and contexts"

UDL_PID_FILE="/var/lib/univention-directory-listener/pid"
[ -f "$UDL_PID_FILE" ] && rm -f "$UDL_PID_FILE"

LISTENER_STATUS_FILE="/var/lib/univention-directory-listener/handlers/listener_handler"
[ -f "$LISTENER_STATUS_FILE" ] && rm -f "$LISTENER_STATUS_FILE"

/usr/sbin/univention-directory-listener \
  -x \
  -d "${DEBUG_LEVEL}" \
  -b "${LDAP_BASE_DN}" \
  -D "cn=admin,${LDAP_BASE_DN}" \
  -n "${NOTIFIER_SERVER}" \
  -m "/usr/lib/univention-directory-listener/system" \
  -c "/var/lib/univention-directory-listener" \
  -y "${LDAP_PASSWORD_FILE}" \
  -g \
  "${TLS_START_FLAGS}"

echo "waiting for contexts and access profiles to be initialized"
while true; do
    LISTENER_STATUS="-1 (Univention Directory Listener not running yet)"
  if [ -f "$LISTENER_STATUS_FILE" ]; then
    LISTENER_STATUS=$(cat /var/lib/univention-directory-listener/handlers/listener_handler)
  fi
  echo "contexts and access profiles listener status: $LISTENER_STATUS"
  if [ "$LISTENER_STATUS" = "3" ]; then
    echo "contexts and access profiles already initialized and ready"
    echo "####### logs from contexts and access profiles listener #######"
    cat /var/log/univention/listener.log
    echo "####### end of logs from contexts and access profiles listener #######"
    pkill -f univention-directory-listener
    break
  else
    echo "contexts and access profiles not initialized yet"
    sleep 1
  fi
done

echo "preinitialization listener finished"
[ -f "$UDL_PID_FILE" ] && rm -f "$UDL_PID_FILE"
[ -f "$LISTENER_STATUS_FILE" ] && rm -f "$LISTENER_STATUS_FILE"

touch /tmp/initialized.lock

exec "$@"
