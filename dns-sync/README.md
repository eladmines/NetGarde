# DNS Sync Container

A containerized utility for syncing blocked sites from the NetGarde API to dnsmasq configuration.

## Overview

This container periodically fetches blocked sites from the NetGarde backend API and updates the dnsmasq configuration file to block those domains at the DNS level.

## Usage

### Environment Variables

- `API_BASE_URL` (default: `http://localhost:8000`): Base URL of the NetGarde API
- `API_ENDPOINT` (default: `/blocked-sites`): API endpoint for blocked sites
- `BLOCK_IP` (default: `0.0.0.0`): IP address to redirect blocked domains to
- `DNS_CONFIG_PATH` (default: `/etc/dnsmasq.d/custom.conf`): Path to dnsmasq configuration file
- `SYNC_INTERVAL` (default: `3600`): Sync interval in seconds (0 = run once and exit)
- `PAGE_SIZE` (default: `100`): Number of items per page when fetching from API
- `DNSMASQ_RESTART_CMD` (default: `killall -HUP dnsmasq`): Command to reload dnsmasq

### Docker Run

```bash
docker run -d \
  --name dns-sync \
  --restart unless-stopped \
  -v /etc/dnsmasq.d:/etc/dnsmasq.d:rw \
  -e API_BASE_URL="https://daemixzdg8jfd.cloudfront.net" \
  -e API_ENDPOINT="/blocked-sites" \
  -e BLOCK_IP="0.0.0.0" \
  -e DNS_CONFIG_PATH="/etc/dnsmasq.d/custom.conf" \
  -e SYNC_INTERVAL=3600 \
  dns-sync:latest
```

### Docker Compose

The service is already configured in `docker-compose.yml`. Set environment variables:

```bash
# In your .env file or environment
API_BASE_URL=https://daemixzdg8jfd.cloudfront.net
API_ENDPOINT=/blocked-sites
BLOCK_IP=0.0.0.0
SYNC_INTERVAL=3600
```

Then run:
```bash
docker compose up -d dns-sync
```

## How It Works

1. **Fetches Blocked Sites**: Calls the NetGarde API endpoint `/blocked-sites` with pagination
2. **Converts to dnsmasq Format**: Transforms each domain to `address=/domain.com/0.0.0.0` format
3. **Writes Config**: Updates the dnsmasq configuration file
4. **Reloads dnsmasq**: Sends SIGHUP to dnsmasq to apply changes

## Generated DNS Format

The script automatically converts blocked sites to dnsmasq format:

```
# Auto-generated DNS configuration
# Last updated: 2026-01-21 21:30:45

address=/example.com/0.0.0.0
address=/malicious-site.com/0.0.0.0
address=/ads.example.com/0.0.0.0
```

## Running as a Cron Job

For cron job mode (recommended for production), see [CRON_SETUP.md](CRON_SETUP.md) for detailed instructions.

Quick setup:
```bash
# Make script executable
chmod +x dns-sync/run-sync.sh

# Add to crontab (runs every hour)
crontab -e
# Add: 0 * * * * /path/to/NetGarde/dns-sync/run-sync.sh >> /var/log/dns-sync.log 2>&1
```

## Notes

- The container needs write access to the dnsmasq configuration directory
- Ensure dnsmasq is running on the host and can be reloaded with the specified command
- **Continuous mode**: Set `SYNC_INTERVAL > 0` and use `docker compose up -d dns-sync`
- **Cron mode**: Set `SYNC_INTERVAL=0` and use `docker compose run --rm dns-sync` (recommended)
- The script handles pagination automatically to fetch all blocked sites
- Domains are normalized (removes http://, https://, www., paths, query strings)
- Deleted sites (`is_deleted=true`) are automatically excluded
- The configuration file is written to `/etc/dnsmasq.d/blocked-domains.conf` by default