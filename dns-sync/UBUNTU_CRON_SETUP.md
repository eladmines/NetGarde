# Ubuntu Server Cron Job Setup

Quick guide to set up DNS sync as a cron job on your Ubuntu server.

## Prerequisites

- SSH access to your Ubuntu server
- Docker and Docker Compose installed
- NetGarde project deployed on the server
- dnsmasq installed and running

## Step-by-Step Setup

### 1. SSH into your Ubuntu server

```bash
ssh ubuntu@your-server-ip
```

### 2. Navigate to your NetGarde directory

```bash
cd ~/netgarde
# Or wherever you deployed the project
```

### 3. Make the script executable

```bash
chmod +x dns-sync/run-sync.sh
```

### 4. Test the script manually first

```bash
# Test that it works
./dns-sync/run-sync.sh
```

If it works, you should see output like:
```
DNS Sync Container Started
Configuration:
  API_BASE_URL: https://daemixzdg8jfd.cloudfront.net
  ...
Starting DNS sync...
```

### 5. Create a .env file (if not exists)

```bash
# Create or edit .env file in the project root
nano .env
```

Add these variables:
```bash
API_BASE_URL=https://daemixzdg8jfd.cloudfront.net
API_ENDPOINT=/blocked-sites
BLOCK_IP=0.0.0.0
DNS_CONFIG_PATH=/etc/dnsmasq.d/blocked-domains.conf
SYNC_INTERVAL=0
PAGE_SIZE=100
DNSMASQ_RESTART_CMD=killall -HUP dnsmasq
```

### 6. Get the full path to the script

```bash
# Get absolute path
realpath dns-sync/run-sync.sh
```

Example output: `/home/ubuntu/netgarde/dns-sync/run-sync.sh`

### 7. Add to crontab

```bash
crontab -e
```

Choose your editor (nano is easiest), then add one of these lines:

**Every hour (recommended):**
```bash
0 * * * * /home/ubuntu/netgarde/dns-sync/run-sync.sh >> /var/log/dns-sync.log 2>&1
```

**Every 30 minutes:**
```bash
*/30 * * * * /home/ubuntu/netgarde/dns-sync/run-sync.sh >> /var/log/dns-sync.log 2>&1
```

**Every 15 minutes:**
```bash
*/15 * * * * /home/ubuntu/netgarde/dns-sync/run-sync.sh >> /var/log/dns-sync.log 2>&1
```

**Daily at 2 AM:**
```bash
0 2 * * * /home/ubuntu/netgarde/dns-sync/run-sync.sh >> /var/log/dns-sync.log 2>&1
```

Save and exit (Ctrl+X, then Y, then Enter in nano).

### 8. Verify cron job is added

```bash
crontab -l
```

You should see your cron job listed.

### 9. Create log directory (if needed)

```bash
sudo touch /var/log/dns-sync.log
sudo chmod 666 /var/log/dns-sync.log
```

Or use a user-writable location:
```bash
# Use home directory instead
mkdir -p ~/logs
# Then update crontab to use: >> ~/logs/dns-sync.log 2>&1
```

## Verify It's Working

### Check logs

```bash
tail -f /var/log/dns-sync.log
# Or if using home directory:
tail -f ~/logs/dns-sync.log
```

### Check dnsmasq config

```bash
cat /etc/dnsmasq.d/blocked-domains.conf
```

### Test manually

```bash
./dns-sync/run-sync.sh
```

## Troubleshooting

### Cron job not running

1. Check cron service:
   ```bash
   sudo systemctl status cron
   ```

2. Check cron logs:
   ```bash
   grep CRON /var/log/syslog | tail -20
   ```

3. Check your cron job syntax:
   ```bash
   crontab -l
   ```

### Permission denied

```bash
# Make sure script is executable
chmod +x dns-sync/run-sync.sh

# Check Docker permissions
docker ps  # Should work without sudo
```

### Docker not found in cron

Cron runs with minimal environment. The script should handle this, but if issues occur:

```bash
# Add full paths in crontab
0 * * * * /usr/bin/docker compose -f /home/ubuntu/netgarde/docker-compose.yml run --rm -e SYNC_INTERVAL=0 dns-sync >> /var/log/dns-sync.log 2>&1
```

### Check if dnsmasq is accessible

```bash
# Test dnsmasq reload command
killall -HUP dnsmasq

# Check dnsmasq status
sudo systemctl status dnsmasq
```

## Quick Reference

**Edit crontab:**
```bash
crontab -e
```

**View crontab:**
```bash
crontab -l
```

**View cron logs:**
```bash
tail -f /var/log/dns-sync.log
```

**Test manually:**
```bash
./dns-sync/run-sync.sh
```
