#!/usr/bin/env python3
"""
NetGarde DNS Log Watcher — Real-time log tail and API push.

Continuously watches /var/log/dnsmasq.log for new DNS queries
and sends them to the NetGarde backend API in near real-time.
Designed to run as a systemd service on the host machine.
"""

import os
import sys
import re
import json
import time
import logging
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set

from noise_filter import is_noise_domain

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [dns_watcher] %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
DNSMASQ_LOG_PATH = os.getenv('DNSMASQ_LOG_PATH', '/var/log/dnsmasq.log')
STATE_FILE_PATH = os.getenv('STATE_FILE_PATH', '/var/lib/netgarde/log_parser_state')
BLOCKED_DOMAINS_PATH = os.getenv('BLOCKED_DOMAINS_PATH', '/etc/dnsmasq.d/blocked-domains.conf')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
DNS_INGEST_TOKEN = os.getenv('DNS_INGEST_TOKEN', '').strip()
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '50'))
POLL_INTERVAL = float(os.getenv('POLL_INTERVAL', '2'))  # seconds between checks
FLUSH_INTERVAL = float(os.getenv('FLUSH_INTERVAL', '3'))  # max seconds before sending a batch
BLOCKED_DOMAINS_RELOAD_INTERVAL = int(os.getenv('BLOCKED_DOMAINS_RELOAD_INTERVAL', '300'))  # reload every 5 min

# Regex to parse dnsmasq "query" log lines
QUERY_PATTERN = re.compile(
    r'^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+'   # timestamp
    r'dnsmasq\[\d+\]:\s+'                      # dnsmasq process info
    r'query\[(\w+)\]\s+'                       # query type (A, AAAA, etc.)
    r'(\S+)\s+'                                # domain name
    r'from\s+(\S+)'                            # client IP
)


def load_blocked_domains(config_path: str) -> Set[str]:
    blocked = set()
    try:
        if not os.path.exists(config_path):
            logger.warning(f"Blocked domains file not found: {config_path}")
            return blocked

        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('address=/'):
                    parts = line.split('/')
                    if len(parts) >= 3:
                        domain = parts[1]
                        if domain:
                            blocked.add(domain.lower())

        logger.info(f"Loaded {len(blocked)} blocked domains from {config_path}")
    except Exception as e:
        logger.error(f"Error loading blocked domains: {e}")

    return blocked


def get_last_position(state_file: str) -> int:
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                content = f.read().strip()
                if content:
                    return int(content)
    except (ValueError, IOError) as e:
        logger.warning(f"Error reading state file: {e}")
    return 0


def save_position(state_file: str, position: int):
    try:
        state_dir = os.path.dirname(state_file)
        if state_dir:
            os.makedirs(state_dir, exist_ok=True)
        with open(state_file, 'w') as f:
            f.write(str(position))
    except IOError as e:
        logger.error(f"Error saving state file: {e}")


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    try:
        current_year = datetime.now(timezone.utc).year
        dt = datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")
        return dt.replace(tzinfo=timezone.utc)
    except ValueError:
        return None


def parse_log_lines(lines: List[str], blocked_domains: Set[str]) -> List[Dict[str, Any]]:
    queries = []
    seen = set()

    for line in lines:
        match = QUERY_PATTERN.search(line)
        if not match:
            continue

        timestamp_str, query_type, domain, client_ip = match.groups()
        timestamp = parse_timestamp(timestamp_str)
        if not timestamp:
            continue

        if domain.endswith('.in-addr.arpa') or domain.endswith('.ip6.arpa'):
            continue
        if is_noise_domain(domain):
            continue

        dedup_key = (timestamp.isoformat(), domain.lower(), client_ip)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        is_blocked = domain.lower() in blocked_domains
        action = "blocked" if is_blocked else "forwarded"

        queries.append({
            "timestamp": timestamp.isoformat(),
            "client_ip": client_ip,
            "domain": domain,
            "query_type": query_type,
            "action": action,
            "blocked": is_blocked
        })

    return queries


def send_to_api(queries: List[Dict[str, Any]], api_url: str) -> bool:
    """Send parsed queries to the NetGarde API via POST /dns-queries/bulk."""
    import urllib.request
    import urllib.error

    if not queries:
        return True

    url = f"{api_url.rstrip('/')}/dns-queries/bulk"
    payload = json.dumps({"queries": queries}).encode('utf-8')

    try:
        headers = {'Content-Type': 'application/json'}
        if DNS_INGEST_TOKEN:
            headers['Authorization'] = f"Bearer {DNS_INGEST_TOKEN}"

        req = urllib.request.Request(
            url,
            data=payload,
            headers=headers,
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in (200, 201):
                return True
            logger.error(f"API returned status {response.status}")
            return False

    except urllib.error.HTTPError as e:
        body = e.read().decode('utf-8', errors='replace')
        logger.error(f"HTTP error: {e.code} - {body}")
        return False
    except urllib.error.URLError as e:
        logger.error(f"URL error: {e.reason}")
        return False
    except Exception as e:
        logger.error(f"Error sending to API: {e}")
        return False


def wait_for_api(api_url: str, max_retries: int = 30, retry_interval: int = 10):
    import urllib.request
    import urllib.error

    health_url = f"{api_url.rstrip('/')}/health"
    for _ in range(max_retries):
        try:
            with urllib.request.urlopen(health_url, timeout=5) as response:
                if response.status == 200:
                    logger.info("Backend API is available")
                    return
        except Exception:
            logger.info("Waiting for backend API...")
        time.sleep(retry_interval)
    raise RuntimeError("Backend API not available")


def main():
    wait_for_api(API_BASE_URL)
    position = get_last_position(STATE_FILE_PATH)
    blocked_domains = load_blocked_domains(BLOCKED_DOMAINS_PATH)
    last_reload = time.time()

    last_flush = time.time()
    pending: List[Dict[str, Any]] = []

    while True:
        try:
            now = time.time()
            if now - last_reload >= BLOCKED_DOMAINS_RELOAD_INTERVAL:
                blocked_domains = load_blocked_domains(BLOCKED_DOMAINS_PATH)
                last_reload = now

            if not os.path.exists(DNSMASQ_LOG_PATH):
                logger.warning(f"dnsmasq log not found: {DNSMASQ_LOG_PATH}")
                time.sleep(POLL_INTERVAL)
                continue

            with open(DNSMASQ_LOG_PATH, 'r') as f:
                f.seek(position)
                new_data = f.read()
                position = f.tell()

            if new_data:
                lines = [l for l in new_data.splitlines() if l.strip()]
                parsed = parse_log_lines(lines, blocked_domains)
                if parsed:
                    pending.extend(parsed)

            should_flush = len(pending) >= BATCH_SIZE or (pending and (now - last_flush) >= FLUSH_INTERVAL)
            if should_flush:
                batch = pending[:BATCH_SIZE]
                ok = send_to_api(batch, API_BASE_URL)
                if ok:
                    pending = pending[len(batch):]
                    save_position(STATE_FILE_PATH, position)
                last_flush = now

            time.sleep(POLL_INTERVAL)
        except KeyboardInterrupt:
            logger.info("Shutting down…")
            return 0
        except Exception as e:
            logger.error(f"Watcher error: {e}")
            time.sleep(POLL_INTERVAL)


if __name__ == "__main__":
    sys.exit(main())

