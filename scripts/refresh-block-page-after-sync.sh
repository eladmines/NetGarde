#!/usr/bin/env bash
# Regenerate HTTPS cert SANs from blocked-domains.conf and restart block-page.
set -euo pipefail

REPO_ROOT="${NETGARDE_REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
cd "$REPO_ROOT"

sudo bash "$REPO_ROOT/scripts/block-page-tls/generate-certs.sh" "${1:-/etc/dnsmasq.d/blocked-domains.conf}"
docker compose up -d block-page
docker compose restart block-page
echo "block-page restarted with updated TLS SANs"
