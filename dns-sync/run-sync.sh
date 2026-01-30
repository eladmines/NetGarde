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

# Run the DNS sync container once (SYNC_INTERVAL=0 means run once and exit)
# Note: We disable the internal reload since it can't access host dnsmasq
docker compose run --rm -e SYNC_INTERVAL=0 -e DNSMASQ_RESTART_CMD="" dns-sync

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
