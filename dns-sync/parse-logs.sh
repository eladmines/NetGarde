#!/bin/bash
# =============================================================================
# NetGarde DNS Log Parser - Cron Wrapper
# =============================================================================
# Parses dnsmasq query logs and sends them to the NetGarde backend API.
# Designed to be called from cron every minute.
#
# Setup:
#   sudo chmod +x /home/ubuntu/netgarde/dns-sync/parse-logs.sh
#   sudo mkdir -p /var/lib/netgarde
#   sudo crontab -e
#   # Add: * * * * * /home/ubuntu/netgarde/dns-sync/parse-logs.sh >> /var/log/netgarde-log-parser.log 2>&1
# =============================================================================

set -e

# Get the directory where this script is located
SCRIPT_DIR="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"

# Configuration (override via environment variables)
export DNSMASQ_LOG_PATH=${DNSMASQ_LOG_PATH:-/var/log/dnsmasq.log}
export STATE_FILE_PATH=${STATE_FILE_PATH:-/var/lib/netgarde/log_parser_state}
export BLOCKED_DOMAINS_PATH=${BLOCKED_DOMAINS_PATH:-/etc/dnsmasq.d/blocked-domains.conf}
export API_BASE_URL=${API_BASE_URL:-http://localhost:8000}
export BATCH_SIZE=${BATCH_SIZE:-100}

# Create state directory if it doesn't exist
mkdir -p "$(dirname "$STATE_FILE_PATH")"

# Run the log parser
python3 "$SCRIPT_DIR/log_parser.py"
