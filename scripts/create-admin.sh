#!/usr/bin/env bash
##############################################################################
# create-admin.sh
# Creates the first admin user on the Synapse homeserver.
# Run AFTER `docker compose up -d` and after Synapse is healthy.
#
# Usage: ./scripts/create-admin.sh <username> <password>
# Example: ./scripts/create-admin.sh admin MySecurePassword123!
##############################################################################

set -euo pipefail

USERNAME="${1:-}"
PASSWORD="${2:-}"

if [[ -z "$USERNAME" || -z "$PASSWORD" ]]; then
    echo "Usage: $0 <username> <password>"
    echo "Example: $0 admin MySecurePassword123!"
    exit 1
fi

echo "==> Creating admin user: $USERNAME"
docker compose exec synapse \
    register_new_matrix_user http://localhost:8008 \
    -c /data/homeserver.yaml \
    --admin \
    -u "$USERNAME" \
    -p "$PASSWORD"

echo ""
echo "==> Admin user @${USERNAME}:chat.local created successfully."
echo "==> Open https://chat.local and sign in with these credentials."
