# DNS Sync Container

A containerized utility for syncing **policy DNS rules** (packs, profiles, schedules, behavior blocks, quarantine) from the NetGarde API to dnsmasq.

## Overview

This container periodically calls `GET /policy/dns-sync` and writes global + per-device tagged dnsmasq configuration.

## Usage

### Environment Variables

- `API_BASE_URL` (default: `http://localhost:8000`): Base URL of the NetGarde API
- `POLICY_DNS_SYNC_ENDPOINT` (default: `/policy/dns-sync`): Merged policy DNS sync API
- `BLOCK_IP` (default: `10.0.0.1`): IPv4 returned for blocked domains (A records). Points VPN clients at the **block-page** nginx on the WireGuard gateway. Use **`0.0.0.0`** for sinkhole-only (“site can’t be reached”). Do **not** use EC2 VPC `172.31.x.x` — unreachable from `10.0.0.x` clients.
- `BLOCK_PAGE_IP` (default: `10.0.0.1`): Same as gateway IP; used when `BLOCK_IP` is unset.
- `BLOCK_IPV6_IP` (default: `::`): IPv6 sinkhole for blocked domains (AAAA records). Without this, browsers may still reach sites via IPv6 while A records return `0.0.0.0`.
- `DNS_CONFIG_PATH` (default: `/etc/dnsmasq.d/custom.conf`): Path to dnsmasq configuration file
- `SYNC_INTERVAL` (default: `3600`): Sync interval in seconds (0 = run once and exit)
- `PAGE_SIZE` (default: `100`): Number of items per page when fetching from API
- `DNSMASQ_RESTART_CMD` (default: `killall -HUP dnsmasq`): Command to reload dnsmasq
- `DNS_INGEST_TOKEN`: Bearer token for DHCP sync and per-device block sync (`/devices/client-blocks/sync`)
- `ADMIN_API_TOKEN`: Bearer token for fetching global blocked sites when admin auth is enabled
- `CLIENT_BLOCKS_SYNC_ENDPOINT` (default: `/devices/client-blocks/sync`): Per-device behavioral blocks API
- `CLIENT_BLOCKS_CONFIG_DIR` (default: `/etc/dnsmasq.d/netgarde-devices`): Per-device tagged dnsmasq snippets (`ng-device-{id}.conf`)

Per-device blocks use dnsmasq DHCP tags (`dhcp-host=MAC,set:ng_device_{id}` + `tag:ng_device_{id}` + `address=/domain/0.0.0.0`).

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

## Event-Driven Sync (PostgreSQL LISTEN/NOTIFY)

Policy and legacy blocked-site changes trigger immediate dns-sync on the EC2 host:

1. DB triggers send `NOTIFY policy_changed` when packs, profiles, or device assignments change.
2. Legacy `blocked_sites` changes still send `NOTIFY blocked_sites_changed`.
3. `blocked_sites_listener.py` listens on both channels (configurable via `DB_NOTIFY_CHANNELS`) and runs `run-sync.sh`.
4. `run-sync.sh` writes dnsmasq config, reloads dnsmasq, and reports status to `POST /policy/sync-report`.

The listener runs on the EC2 host as a systemd service (`EnvironmentFile=/etc/netgarde/backend.env`):

```bash
sudo cp dns-sync/netgarde-blocked-sites-listener.service /etc/systemd/system/
sudo systemctl daemon-reload
sudo systemctl enable --now netgarde-blocked-sites-listener
```