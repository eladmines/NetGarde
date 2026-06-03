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

# Get DNSMASQ_RESTART_CMD from environment or use default
DNSMASQ_RESTART_CMD=${DNSMASQ_RESTART_CMD:-killall -HUP dnsmasq}

# Blocked domains: default 0.0.0.0 (DNS sinkhole). Do NOT use EC2 VPC IP (172.31.x.x):
# WireGuard clients (10.0.0.x) cannot reach it. Set BLOCK_PAGE_IP=10.0.0.1 only if you
# serve a block page on wg0.
BLOCK_IP=${BLOCK_IP:-${BLOCK_PAGE_IP:-0.0.0.0}}

# Run the DNS sync container once (SYNC_INTERVAL=0 means run once and exit)
# Note: We disable the internal reload since it can't access host dnsmasq
# Use --no-deps to skip starting dependencies (backend should already be running)
docker compose run --rm --no-deps \
  -e SYNC_INTERVAL=0 \
  -e DNSMASQ_RESTART_CMD="" \
  -e BLOCK_IP="$BLOCK_IP" \
  dns-sync

# Reload dnsmasq on the host after container completes
if [ $? -eq 0 ]; then
    echo "Reloading dnsmasq on host..."
    $DNSMASQ_RESTART_CMD || {
        # Try alternative methods if killall fails
        sudo systemctl reload dnsmasq 2>/dev/null || \
        sudo service dnsmasq reload 2>/dev/null || \
        sudo killall -HUP dnsmasq 2>/dev/null || \
        echo "Warning: Could not reload dnsmasq. You may need to reload manually."
    }
fi

exit $?
