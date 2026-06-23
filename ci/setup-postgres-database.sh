#!/bin/bash
# SPDX-License-Identifier: AGPL-3.0-only
# SPDX-FileCopyrightText: 2026 Univention GmbH

# Create PostgreSQL database and user for ox-connector
set -euo pipefail

NAMESPACE="${1:?Usage: $0 <namespace>}"
DB_NAME="${2:-ox_connector}"
DB_USER="${3:-ox_connector}"
DB_PASSWORD="${4:-univention}"

POSTGRES_ADMIN_PASSWORD="$(kubectl get secret nubus-postgresql-credentials -n "${NAMESPACE}" --template={{.data.admin_password}} | base64 -d)"

echo "Setting up PostgreSQL database for ox-connector in namespace '${NAMESPACE}'"

# Wait for postgresql pod to be ready
echo "Waiting for nubus-postgresql-0 pod to be ready..."
kubectl wait --for=condition=ready pod/nubus-postgresql-0 \
    --namespace="${NAMESPACE}" \
    --timeout=300s

# Create database and user
echo "Creating database '${DB_NAME}' and user '${DB_USER}'..."
kubectl exec -i -n "${NAMESPACE}" nubus-postgresql-0 -- bash << EOF
set -euo pipefail
export PGUSER="postgres"
export PGPASSWORD="${POSTGRES_ADMIN_PASSWORD}"
if psql -tc "SELECT 1 FROM pg_user WHERE usename = '${DB_USER}'" | grep -q 1; then
  echo "User already exists, updating."
  psql -c "ALTER USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}' CONNECTION LIMIT 100"
else
  echo "User does not exist, creating."
  psql -c "CREATE USER ${DB_USER} WITH PASSWORD '${DB_PASSWORD}' CONNECTION LIMIT 100"
fi

psql -tc "SELECT 1 FROM pg_database WHERE datname = '${DB_NAME}'" | grep -q 1 || psql -c "CREATE DATABASE ${DB_NAME}"
psql -c "ALTER DATABASE ${DB_NAME} OWNER TO ${DB_USER}"
psql -c "GRANT ALL PRIVILEGES ON DATABASE ${DB_NAME} TO ${DB_USER}"
EOF

# Verify login with the new user
echo "Verifying login with user '${DB_USER}'..."
kubectl exec -i -n "${NAMESPACE}" nubus-postgresql-0 -- bash << EOF || { echo "ERROR: Login with user '${DB_USER}' failed."; exit 1; }
  export PGUSER='${DB_USER}'
  export PGPASSWORD='${DB_PASSWORD}'
  psql -tc 'SELECT 1' > /dev/null
  echo "Login successful."
EOF

# Verify database is empty
echo "Verifying database '${DB_NAME}' is empty..."
kubectl exec -i -n "${NAMESPACE}" nubus-postgresql-0 -- bash << EOF || exit 1
  export PGUSER='${DB_USER}'
  export PGPASSWORD='${DB_PASSWORD}'
  tables="\$(psql -tc "SELECT count(*) FROM information_schema.tables WHERE table_schema = 'public'")"
  if [ "\$tables" -ne 0 ]; then
    echo "ERROR: Database '${DB_NAME}' is not empty. Found \$tables tables in public schema."
    exit 1
  fi
  echo "Database is empty."
EOF

mkdir -p /tmp
echo "OX_DB_CONNECTION_STRING=postgresql://${DB_USER}:${DB_PASSWORD}@nubus-postgresql.${NAMESPACE}.svc.cluster.local:5432/${DB_NAME}" > ox_db_connection_string.env

echo "Database setup complete."
