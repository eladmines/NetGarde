#!/usr/bin/env python3
"""
DNS Sync Script for dnsmasq
Fetches policy DNS rules from NetGarde API and updates dnsmasq configuration.
"""

import os
import sys
import subprocess
import time
import logging
import json
from pathlib import Path
from typing import List, Optional, Dict, Any

logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - %(message)s'
)
logger = logging.getLogger(__name__)

API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
POLICY_DNS_SYNC_ENDPOINT = os.getenv('POLICY_DNS_SYNC_ENDPOINT', '/policy/dns-sync')
BLOCK_IP = os.getenv('BLOCK_IP', '0.0.0.0')
DNS_CONFIG_PATH = os.getenv('DNS_CONFIG_PATH', '/etc/dnsmasq.d/blocked-domains.conf')
SYNC_INTERVAL = int(os.getenv('SYNC_INTERVAL', '3600'))
DNSMASQ_RESTART_CMD = os.getenv('DNSMASQ_RESTART_CMD', 'killall -HUP dnsmasq')
DEVICE_SYNC_ENDPOINT = os.getenv('DEVICE_SYNC_ENDPOINT', '/devices/sync-dhcp')
DHCP_LEASES_PATH = os.getenv('DHCP_LEASES_PATH', '/var/lib/misc/dnsmasq.leases')
DEVICE_SYNC_ENABLED = os.getenv('DEVICE_SYNC_ENABLED', '1').lower() not in ('0', 'false', 'no')
DNS_INGEST_TOKEN = os.getenv('DNS_INGEST_TOKEN', '').strip()
ADMIN_API_TOKEN = os.getenv('ADMIN_API_TOKEN', '').strip()
CLIENT_BLOCKS_CONFIG_DIR = os.getenv('CLIENT_BLOCKS_CONFIG_DIR', '/etc/dnsmasq.d/netgarde-devices')


def _api_headers(admin: bool = False, ingest: bool = False) -> Dict[str, str]:
    headers = {'Accept': 'application/json'}
    if admin and ADMIN_API_TOKEN:
        headers['Authorization'] = f'Bearer {ADMIN_API_TOKEN}'
    elif ingest and DNS_INGEST_TOKEN:
        headers['Authorization'] = f'Bearer {DNS_INGEST_TOKEN}'
    return headers


def fetch_policy_dns_sync(api_url: str, endpoint: str) -> Optional[Dict[str, Any]]:
    if not api_url:
        logger.error("API_BASE_URL environment variable is not set")
        return None
    try:
        import urllib.request

        url = f"{api_url.rstrip('/')}{endpoint}"
        logger.info(f"Fetching policy DNS sync from {url}")
        req = urllib.request.Request(url, headers=_api_headers(ingest=True))
        with urllib.request.urlopen(req, timeout=60) as response:
            if response.status != 200:
                logger.error(f"Policy DNS sync API returned status {response.status}")
                return None
            return json.loads(response.read().decode('utf-8'))
    except Exception as e:
        logger.error(f"Error fetching policy DNS sync: {e}", exc_info=True)
        return None


def domains_to_dnsmasq_lines(domains: List[str], block_ip: str) -> List[str]:
    entries = []
    seen = set()
    for site in domains:
        domain = str(site).strip().lower()
        if not domain or domain in seen:
            continue
        seen.add(domain)
        domain = domain.replace('http://', '').replace('https://', '').replace('www.', '')
        domain = domain.split('/')[0].split('?')[0]
        if domain:
            entries.append(f"address=/{domain}/{block_ip}")
    return entries


def convert_device_entry_to_dnsmasq(entry: Dict[str, Any], block_ip: str) -> List[str]:
    mac = (entry.get('mac_address') or '').strip().lower()
    tag = entry.get('tag') or f"ng_device_{entry.get('device_id')}"
    if not mac:
        return []

    lines = [f"# Device {entry.get('device_id')}", f"dhcp-host={mac},set:{tag}"]

    if entry.get('allowlist_only'):
        lines.append(f"tag:{tag}")
        lines.append(f"address=/#/{block_ip}")
        for domain in entry.get('allowlist_domains') or []:
            d = str(domain).strip().lower()
            if not d:
                continue
            lines.append(f"tag:{tag}")
            lines.append(f"address=/{d}/#")
    else:
        for domain in entry.get('block_domains') or []:
            d = str(domain).strip().lower()
            if not d:
                continue
            lines.append(f"tag:{tag}")
            lines.append(f"address=/{d}/{block_ip}")
    return lines


def write_dns_config(entries: List[str], config_path: str) -> bool:
    try:
        config_file = Path(config_path)
        config_file.parent.mkdir(parents=True, exist_ok=True)
        header = [
            "# NetGarde global policy blocks (auto-generated)",
            f"# Generated at: {time.strftime('%Y-%m-%d %H:%M:%S')}",
            "",
        ]
        content = '\n'.join(header + entries) + '\n'
        config_file.write_text(content)
        logger.info(f"Wrote {len(entries)} global DNS entries to {config_path}")
        return True
    except Exception as e:
        logger.error(f"Error writing DNS config: {e}", exc_info=True)
        return False


def write_client_block_configs(files: Dict[str, List[str]], config_dir: str) -> bool:
    try:
        config_path = Path(config_dir)
        config_path.mkdir(parents=True, exist_ok=True)

        active_names = set(files.keys())
        for existing in config_path.glob('ng-device-*.conf'):
            if existing.name not in active_names:
                existing.unlink()
                logger.info(f"Removed stale client block config {existing}")

        for filename, lines in files.items():
            content = '\n'.join(lines) + '\n'
            (config_path / filename).write_text(content)
            logger.info(f"Wrote {len(lines)} lines to {config_path / filename}")

        if not files:
            logger.info("No per-device policy configs to write")
        return True
    except Exception as e:
        logger.error(f"Error writing client block configs: {e}", exc_info=True)
        return False


def reload_dnsmasq(cmd: str) -> bool:
    if not cmd:
        return True
    try:
        subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        logger.info("dnsmasq reloaded successfully")
        return True
    except subprocess.CalledProcessError as e:
        logger.error(f"Failed to reload dnsmasq: {e.stderr}")
        return False


def sync_policy_dns():
    logger.info("Starting policy DNS sync...")
    data = fetch_policy_dns_sync(API_BASE_URL, POLICY_DNS_SYNC_ENDPOINT)
    if data is None:
        return False

    global_lines = domains_to_dnsmasq_lines(data.get('global_domains') or [], BLOCK_IP)
    if not write_dns_config(global_lines, DNS_CONFIG_PATH):
        return False

    files: Dict[str, List[str]] = {}
    for entry in data.get('entries') or []:
        device_id = entry.get('device_id')
        lines = convert_device_entry_to_dnsmasq(entry, BLOCK_IP)
        if device_id and lines:
            files[f"ng-device-{device_id}.conf"] = lines

    if not write_client_block_configs(files, CLIENT_BLOCKS_CONFIG_DIR):
        return False

    if DNSMASQ_RESTART_CMD:
        if not reload_dnsmasq(DNSMASQ_RESTART_CMD):
            logger.warning("Failed to reload dnsmasq, but config was updated")
            return False
    return True


def parse_dhcp_leases(leases_path: str) -> List[Dict[str, Any]]:
    lease_file = Path(leases_path)
    if not lease_file.exists():
        logger.warning(f"DHCP lease file not found: {leases_path}")
        return []

    leases: List[Dict[str, Any]] = []
    try:
        for line in lease_file.read_text(encoding='utf-8', errors='ignore').splitlines():
            line = line.strip()
            if not line or line.startswith('#'):
                continue
            parts = line.split()
            if len(parts) < 4:
                continue
            mac = parts[1].strip().lower()
            client_ip = parts[2].strip()
            hostname = parts[3].strip()
            if hostname == '*':
                hostname = None
            leases.append({
                'client_ip': client_ip,
                'hostname': hostname,
                'mac_address': mac,
            })
    except Exception as e:
        logger.error(f"Error parsing DHCP leases: {e}", exc_info=True)
        return []

    logger.info(f"Parsed {len(leases)} DHCP lease records")
    return leases


def sync_devices_from_dhcp(api_url: str, endpoint: str, leases_path: str) -> bool:
    leases = parse_dhcp_leases(leases_path)
    if not leases:
        logger.info("No DHCP leases available to sync")
        return True
    try:
        import urllib.request

        url = f"{api_url.rstrip('/')}{endpoint}"
        data = json.dumps({'leases': leases}).encode('utf-8')
        logger.info(f"Syncing {len(leases)} DHCP leases to {url}")
        req = urllib.request.Request(url, data=data, method='POST')
        for key, value in _api_headers(ingest=True).items():
            req.add_header(key, value)
        req.add_header('Content-Type', 'application/json')
        with urllib.request.urlopen(req, timeout=30) as response:
            body = response.read().decode('utf-8')
            if response.status not in (200, 201):
                logger.error(f"Device sync failed with status {response.status}: {body}")
                return False
            logger.info(f"Device sync completed: {body}")
            return True
    except Exception as e:
        logger.error(f"Failed to sync DHCP leases: {e}", exc_info=True)
        return False


def sync_cycle() -> bool:
    policy_ok = sync_policy_dns()
    devices_ok = True
    if DEVICE_SYNC_ENABLED:
        devices_ok = sync_devices_from_dhcp(API_BASE_URL, DEVICE_SYNC_ENDPOINT, DHCP_LEASES_PATH)
    if policy_ok and devices_ok:
        logger.info("Sync cycle completed successfully")
        return True
    logger.warning(f"Sync cycle completed with issues (policy_ok={policy_ok}, devices_ok={devices_ok})")
    return False


def main():
    logger.info("DNS Sync Container Started")
    logger.info(f"  API_BASE_URL: {API_BASE_URL}")
    logger.info(f"  POLICY_DNS_SYNC_ENDPOINT: {POLICY_DNS_SYNC_ENDPOINT}")
    first_ok = sync_cycle()
    if SYNC_INTERVAL > 0:
        while True:
            time.sleep(SYNC_INTERVAL)
            sync_cycle()
    else:
        sys.exit(0 if first_ok else 1)


if __name__ == '__main__':
    main()
