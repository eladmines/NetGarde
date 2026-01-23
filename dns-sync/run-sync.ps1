# PowerShell script to run DNS sync container as a one-time job
# This script is designed to be called from Task Scheduler (Windows cron equivalent)

$ErrorActionPreference = "Stop"

# Get the directory where this script is located
$ScriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$ProjectDir = Split-Path -Parent $ScriptDir

# Change to project directory
Set-Location $ProjectDir

# Load environment variables from .env if it exists
if (Test-Path .env) {
    Get-Content .env | ForEach-Object {
        if ($_ -match '^([^#][^=]+)=(.*)$') {
            [System.Environment]::SetEnvironmentVariable($matches[1], $matches[2], 'Process')
        }
    }
}

# Run the DNS sync container once (SYNC_INTERVAL=0 means run once and exit)
docker compose run --rm -e SYNC_INTERVAL=0 dns-sync

exit $LASTEXITCODE
