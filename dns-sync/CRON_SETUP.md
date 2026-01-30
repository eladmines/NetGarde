# DNS Sync Cron Job Setup

This guide explains how to set up the DNS sync container to run as a cron job instead of running continuously.

## Overview

When running as a cron job, the container:
- Runs once per cron schedule
- Exits after completing the sync
- Does not consume resources when idle
- Is more efficient for periodic updates

## Setup Instructions

### Option 1: Using the Helper Script (Recommended)

#### Linux/Unix

1. Make the script executable:
   ```bash
   chmod +x dns-sync/run-sync.sh
   ```

2. Add to crontab:
   ```bash
   crontab -e
   ```

3. Add one of these lines (choose your schedule):
   ```bash
   # Run every hour
   0 * * * * /path/to/NetGarde/dns-sync/run-sync.sh >> /var/log/dns-sync.log 2>&1
   
   # Run every 30 minutes
   */30 * * * * /path/to/NetGarde/dns-sync/run-sync.sh >> /var/log/dns-sync.log 2>&1
   
   # Run every 15 minutes
   */15 * * * * /path/to/NetGarde/dns-sync/run-sync.sh >> /var/log/dns-sync.log 2>&1
   
   # Run daily at 2 AM
   0 2 * * * /path/to/NetGarde/dns-sync/run-sync.sh >> /var/log/dns-sync.log 2>&1
   ```

#### Windows (Task Scheduler)

1. Open Task Scheduler
2. Create Basic Task
3. Set trigger (e.g., "Daily" or "When I log on")
4. Set action: "Start a program"
5. Program: `powershell.exe`
6. Arguments: `-File "C:\path\to\NetGarde\dns-sync\run-sync.ps1"`

### Option 2: Direct Docker Compose Command

Add to crontab:
```bash
# Run every hour
0 * * * * cd /path/to/NetGarde && docker compose run --rm -e SYNC_INTERVAL=0 dns-sync >> /var/log/dns-sync.log 2>&1
```

### Option 3: Direct Docker Command

If you've built the image:
```bash
# Run every hour
0 * * * * docker run --rm -v /etc/dnsmasq.d:/etc/dnsmasq.d:rw -e API_BASE_URL=https://daemixzdg8jfd.cloudfront.net -e SYNC_INTERVAL=0 dns-sync:latest >> /var/log/dns-sync.log 2>&1
```

## Environment Variables

Make sure to set these in your environment or `.env` file:

```bash
API_BASE_URL=https://daemixzdg8jfd.cloudfront.net
API_ENDPOINT=/blocked-sites
BLOCK_IP=0.0.0.0
DNS_CONFIG_PATH=/etc/dnsmasq.d/blocked-domains.conf
SYNC_INTERVAL=0  # Important: Set to 0 for cron mode
PAGE_SIZE=100
DNSMASQ_RESTART_CMD=killall -HUP dnsmasq
```

## Recommended Schedule

- **Every 15-30 minutes**: For frequently updated block lists
- **Every hour**: For most use cases (default)
- **Every 6 hours**: For stable block lists
- **Daily**: For rarely changing lists

## Testing

Test the cron job manually:

```bash
# Linux/Unix
./dns-sync/run-sync.sh

# Or directly
cd /path/to/NetGarde
docker compose run --rm -e SYNC_INTERVAL=0 dns-sync
```

## Logging

Logs are written to:
- Container stdout/stderr (captured by cron)
- dnsmasq configuration file header (timestamp)

To view recent cron logs:
```bash
tail -f /var/log/dns-sync.log
```

## Troubleshooting

### Container doesn't run
- Check Docker is running: `docker ps`
- Check cron service: `systemctl status cron` (Linux)
- Check cron logs: `grep CRON /var/log/syslog` (Linux)

### Permission errors
- Ensure the script is executable: `chmod +x dns-sync/run-sync.sh`
- Ensure Docker socket is accessible
- Check volume mount permissions: `/etc/dnsmasq.d` must be writable

### DNS not updating
- Check container logs: `docker compose logs dns-sync`
- Verify API is accessible: `curl https://daemixzdg8jfd.cloudfront.net/blocked-sites`
- Check dnsmasq config file: `cat /etc/dnsmasq.d/blocked-domains.conf`
- Verify dnsmasq reloaded: `systemctl status dnsmasq`
