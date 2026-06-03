#!/usr/bin/env bash
##############################################################################
# generate-dev-cert.sh
# Generates a self-signed TLS certificate for local development.
# For production: replace with Let's Encrypt (certbot) certificate.
#
# Usage: ./scripts/generate-dev-cert.sh
# Output: ssl/cert.pem, ssl/key.pem
##############################################################################

set -euo pipefail

SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(dirname "$SCRIPT_DIR")"
SSL_DIR="$PROJECT_DIR/ssl"

mkdir -p "$SSL_DIR"

echo "==> Generating self-signed TLS certificate for local development..."
echo "    Domain: chat.local"
echo "    Output: ssl/cert.pem, ssl/key.pem"
echo ""

openssl req -x509 \
  -newkey rsa:4096 \
  -keyout "$SSL_DIR/key.pem" \
  -out "$SSL_DIR/cert.pem" \
  -sha256 \
  -days 365 \
  -nodes \
  -subj "/C=CA/ST=BC/L=Surrey/O=KPU Group 7/CN=chat.local" \
  -addext "subjectAltName=DNS:chat.local,DNS:localhost,IP:127.0.0.1"

echo ""
echo "==> Certificate generated successfully:"
echo "    $SSL_DIR/cert.pem"
echo "    $SSL_DIR/key.pem"
echo ""
echo "==> To trust this cert on macOS (Apple M1):"
echo "    sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ssl/cert.pem"
echo ""
echo "==> Add to /etc/hosts for local domain resolution:"
echo "    echo '127.0.0.1 chat.local' | sudo tee -a /etc/hosts"
