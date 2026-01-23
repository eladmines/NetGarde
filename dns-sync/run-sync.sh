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

# Run the DNS sync container once (SYNC_INTERVAL=0 means run once and exit)
docker compose run --rm -e SYNC_INTERVAL=0 dns-sync

exit $?
