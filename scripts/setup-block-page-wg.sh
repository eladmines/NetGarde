#!/usr/bin/env bash
# Ensure TrustEdge block-page is reachable on the WireGuard gateway (10.0.0.1:80 and :443).
# Run on EC2 after docker compose up: sudo bash scripts/setup-block-page-wg.sh
set -euo pipefail

REPO_ROOT="${TRUSTEDGE_REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
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

echo "Generating TLS (CA + SANs for blocked domains)..."
if [[ -f /etc/dnsmasq.d/blocked-domains.conf ]]; then
  sudo bash "$REPO_ROOT/scripts/block-page-tls/generate-certs.sh" /etc/dnsmasq.d/blocked-domains.conf
else
  sudo bash "$REPO_ROOT/scripts/block-page-tls/generate-certs.sh"
fi

echo "Building and starting block-page (HTTP + HTTPS)..."
docker compose build block-page
docker compose up -d block-page

if command -v ufw &>/dev/null && ufw status 2>/dev/null | grep -q "Status: active"; then
  ufw allow in on "$WG_IF" to any port 80 proto tcp comment "TrustEdge block page HTTP" || true
  ufw allow in on "$WG_IF" to any port 443 proto tcp comment "TrustEdge block page HTTPS" || true
fi

if curl -sf --max-time 3 "http://${BLOCK_PAGE_IP}/" >/dev/null; then
  echo "Block page OK at http://${BLOCK_PAGE_IP}/"
else
  echo "warning: could not reach http://${BLOCK_PAGE_IP}/ — check docker compose ports and wg0"
fi

if curl -skf --max-time 3 "https://${BLOCK_PAGE_IP}/" >/dev/null; then
  echo "Block page OK at https://${BLOCK_PAGE_IP}/ (self-signed cert)"
else
  echo "warning: could not reach https://${BLOCK_PAGE_IP}/ — rebuild block-page and open port 443"
fi

echo "Set BLOCK_IP=${BLOCK_PAGE_IP} in .env and run ./dns-sync/run-sync.sh"
echo ""
echo "For HTTPS block page on Mac, trust the CA once:"
echo "  scp ubuntu@SERVER:/etc/trustedge/block-page-tls/ca.crt ."
echo "  sudo security add-trusted-cert -d -r trustRoot -k /Library/Keychains/System.keychain ca.crt"
