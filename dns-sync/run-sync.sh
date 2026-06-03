#!/bin/bash
# Script to run DNS sync container as a one-time job
# This script is designed to be called from cron

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
PROJECT_DIR="$(cd "$SCRIPT_DIR/.." && pwd)"

# Change to project directory
cd "$PROJECT_DIR"

# Load environment variables from .env if it exists
if [ -f .env ]; then
    export $(cat .env | grep -v '^#' | xargs)
fi

# Reload host dnsmasq (signals root-owned process on EC2)
DNSMASQ_RESTART_CMD=${DNSMASQ_RESTART_CMD:-sudo systemctl reload dnsmasq}

# Block page on WireGuard gateway (docker block-page :80). Not 172.31.x.x (VPC — unreachable from VPN).
BLOCK_PAGE_IP=${BLOCK_PAGE_IP:-10.0.0.1}
BLOCK_IP=${BLOCK_IP:-${BLOCK_PAGE_IP}}

# Run the DNS sync container once (SYNC_INTERVAL=0 means run once and exit)
# Note: We disable the internal reload since it can't access host dnsmasq
# Use --no-deps to skip starting dependencies (backend should already be running)
BLOCK_IPV6_IP=${BLOCK_IPV6_IP:-::}

docker compose run --rm --no-deps \
  -e SYNC_INTERVAL=0 \
  -e DNSMASQ_RESTART_CMD="" \
  -e BLOCK_IP="$BLOCK_IP" \
  -e BLOCK_IPV6_IP="$BLOCK_IPV6_IP" \
  dns-sync

# Reload dnsmasq on the host after container completes
if [ $? -eq 0 ]; then
    echo "Reloading dnsmasq on host (BLOCK_IP=$BLOCK_IP)..."
    if eval "$DNSMASQ_RESTART_CMD"; then
        echo "dnsmasq reloaded."
    else
        sudo systemctl reload dnsmasq 2>/dev/null || \
        sudo systemctl restart dnsmasq 2>/dev/null || \
        sudo killall -HUP dnsmasq 2>/dev/null || {
            echo "Could not reload dnsmasq. Run: sudo systemctl restart dnsmasq"
            exit 1
        }
    fi
    if [[ -x "$PROJECT_DIR/scripts/refresh-block-page-after-sync.sh" ]]; then
        echo "Refreshing block-page TLS SANs for HTTPS..."
        bash "$PROJECT_DIR/scripts/refresh-block-page-after-sync.sh" || \
            echo "warning: block-page TLS refresh failed (HTTPS may use fallback cert)"
    fi
fi

exit $?
