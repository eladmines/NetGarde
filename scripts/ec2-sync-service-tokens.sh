#!/usr/bin/env bash
# Push ADMIN_API_TOKEN / DNS_INGEST_TOKEN from backend.env into host services + compose .env
set -euo pipefail

ENV_FILE="${NETGARDE_ENV_FILE:-/etc/netgarde/backend.env}"
REPO_ROOT="${NETGARDE_REPO_ROOT:-$(cd "$(dirname "$0")/.." && pwd)}"
COMPOSE_ENV="${REPO_ROOT}/.env"

read_env() {
  local key="$1"
  sudo grep -E "^${key}=" "$ENV_FILE" 2>/dev/null | tail -1 | cut -d= -f2- || true
}

if ! sudo test -f "$ENV_FILE"; then
  echo "Missing $ENV_FILE — run ec2-sync-backend-env.sh first" >&2
  exit 1
fi

DNS_INGEST_TOKEN="$(read_env DNS_INGEST_TOKEN)"
ADMIN_API_TOKEN="$(read_env ADMIN_API_TOKEN)"
BLOCK_IP="$(read_env BLOCK_IP)"
if [ -z "$BLOCK_IP" ]; then
  BLOCK_IP="0.0.0.0"
fi

# --- netgarde-log-watcher (DNS → POST /dns-queries/bulk) ---
if systemctl list-unit-files netgarde-log-watcher.service >/dev/null 2>&1; then
  sudo mkdir -p /etc/systemd/system/netgarde-log-watcher.service.d
  if [ -n "$DNS_INGEST_TOKEN" ]; then
    printf '%s\n' "[Service]" "Environment=DNS_INGEST_TOKEN=${DNS_INGEST_TOKEN}" | \
      sudo tee /etc/systemd/system/netgarde-log-watcher.service.d/tokens.conf >/dev/null
    echo "Updated netgarde-log-watcher DNS_INGEST_TOKEN"
  else
    sudo rm -f /etc/systemd/system/netgarde-log-watcher.service.d/tokens.conf
    echo "WARNING: DNS_INGEST_TOKEN empty — log watcher may get 401 on ingest"
  fi
  sudo systemctl daemon-reload
  sudo systemctl restart netgarde-log-watcher || true
fi

# --- repo-root .env for docker compose (dns-sync needs both tokens) ---
touch "$COMPOSE_ENV"
for key in WG_AGENT_URL WG_AGENT_TOKEN DNS_INGEST_TOKEN ADMIN_API_TOKEN; do
  val="$(read_env "$key")"
  [ -n "$val" ] || continue
  if grep -q "^${key}=" "$COMPOSE_ENV" 2>/dev/null; then
    sed -i.bak "s|^${key}=.*|${key}=${val}|" "$COMPOSE_ENV" && rm -f "${COMPOSE_ENV}.bak"
  else
    echo "${key}=${val}" >>"$COMPOSE_ENV"
  fi
done
if grep -q "^BLOCK_IP=" "$COMPOSE_ENV" 2>/dev/null; then
  sed -i.bak "s|^BLOCK_IP=.*|BLOCK_IP=${BLOCK_IP}|" "$COMPOSE_ENV" && rm -f "${COMPOSE_ENV}.bak"
else
  echo "BLOCK_IP=${BLOCK_IP}" >>"$COMPOSE_ENV"
fi
chmod 600 "$COMPOSE_ENV" 2>/dev/null || true
echo "Updated ${COMPOSE_ENV} for docker compose (BLOCK_IP=${BLOCK_IP})"
