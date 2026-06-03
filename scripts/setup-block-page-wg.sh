#!/usr/bin/env bash
# Ensure NetGarde block-page is reachable on the WireGuard gateway IP (default 10.0.0.1:80).
# Run on EC2 after docker compose up: sudo bash scripts/setup-block-page-wg.sh
set -euo pipefail

REPO_ROOT="${NETGARDE_REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
WG_IF="${WG_IF:-wg0}"
BLOCK_PAGE_IP="${BLOCK_PAGE_IP:-10.0.0.1}"

cd "$REPO_ROOT"

if ! ip link show "$WG_IF" &>/dev/null; then
  echo "error: $WG_IF not found. Start WireGuard first." >&2
  exit 1
fi

if ! ip -4 -o addr show dev "$WG_IF" | grep -q "inet ${BLOCK_PAGE_IP}/"; then
  echo "warning: ${BLOCK_PAGE_IP} not on $WG_IF; block-page may still work if port 80 is open on all interfaces"
fi

echo "Starting block-page container..."
docker compose up -d block-page

if command -v ufw &>/dev/null && ufw status 2>/dev/null | grep -q "Status: active"; then
  ufw allow in on "$WG_IF" to any port 80 proto tcp comment "NetGarde block page" || true
fi

if curl -sf --max-time 3 "http://${BLOCK_PAGE_IP}/" >/dev/null; then
  echo "Block page OK at http://${BLOCK_PAGE_IP}/"
else
  echo "warning: could not reach http://${BLOCK_PAGE_IP}/ — check docker compose ports and wg0"
fi

echo "Set BLOCK_IP=${BLOCK_PAGE_IP} in .env and run ./dns-sync/run-sync.sh"
