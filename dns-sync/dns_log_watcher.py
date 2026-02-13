#!/usr/bin/env python3
"""
NetGarde DNS Log Watcher — Real-time log tail and API push.

Continuously watches /var/log/dnsmasq.log for new DNS queries
and sends them to the NetGarde backend API in near real-time.
Also broadcasts to connected WebSocket clients via the API.

Designed to run as a systemd service on the host machine.
Replaces the cron-based log_parser.py for real-time streaming.
"""

import os
import sys
import re
import json
import time
import logging
from datetime import datetime
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
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '50'))
POLL_INTERVAL = float(os.getenv('POLL_INTERVAL', '2'))  # seconds between checks
FLUSH_INTERVAL = float(os.getenv('FLUSH_INTERVAL', '3'))  # max seconds before sending a batch
BLOCKED_DOMAINS_RELOAD_INTERVAL = int(os.getenv('BLOCKED_DOMAINS_RELOAD_INTERVAL', '300'))  # reload every 5 min

# Regex to parse dnsmasq "query" log lines
QUERY_PATTERN = re.compile(
    r'^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+'   # timestamp
    r'dnsmasq\[\d+\]:\s+'                         # dnsmasq process info
    r'query\[(\w+)\]\s+'                           # query type (A, AAAA, etc.)
    r'(\S+)\s+'                                    # domain name
    r'from\s+(\S+)'                                # client IP
)


def load_blocked_domains(config_path: str) -> Set[str]:
    """Load blocked domains from the dnsmasq blocked-domains.conf file."""
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
    """Get the last read byte-position from the state file."""
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
    """Save the current read byte-position to the state file."""
    try:
        state_dir = os.path.dirname(state_file)
        if state_dir:
            os.makedirs(state_dir, exist_ok=True)
        with open(state_file, 'w') as f:
            f.write(str(position))
    except IOError as e:
        logger.error(f"Error saving state file: {e}")


def parse_timestamp(timestamp_str: str) -> Optional[datetime]:
    """Parse dnsmasq log timestamp into a datetime object."""
    try:
        current_year = datetime.now().year
        dt = datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")
        return dt
    except ValueError:
        return None


def parse_log_lines(lines: List[str], blocked_domains: Set[str]) -> List[Dict[str, Any]]:
    """
    Parse dnsmasq log lines into DNS query records.
    Deduplicates by (timestamp, domain, client_ip).
    """
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

        # Skip internal/noise queries
        if domain.endswith('.in-addr.arpa') or domain.endswith('.ip6.arpa'):
            continue

        # Skip system noise (telemetry, CDN, updates, etc.)
        if is_noise_domain(domain):
            continue

        # Deduplicate: keep only one entry per (timestamp, domain, client_ip)
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
        req = urllib.request.Request(
            url,
            data=payload,
            headers={'Content-Type': 'application/json'},
            method='POST'
        )

        with urllib.request.urlopen(req, timeout=10) as response:
            if response.status in (200, 201):
                return True
            else:
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
    """Wait for the backend API to become available."""
    import urllib.request
    import urllib.error

    health_url = f"{api_url.rstrip('/')}/health"
    for i in range(max_retries):
        try:
            req = urllib.request.Request(health_url, method='GET')
            with urllib.request.urlopen(req, timeout=5) as response:
                if response.status == 200:
                    logger.info("Backend API is available")
                    return True
        except Exception:
            pass

        if i < max_retries - 1:
            logger.info(f"Waiting for backend API at {health_url}... (attempt {i + 1}/{max_retries})")
            time.sleep(retry_interval)

    logger.error(f"Backend API not available after {max_retries} attempts")
    return False


def main():
    """Main entry point — continuously watches the dnsmasq log file."""
    logger.info("=" * 60)
    logger.info("NetGarde DNS Log Watcher started")
    logger.info(f"  Log file:           {DNSMASQ_LOG_PATH}")
    logger.info(f"  State file:         {STATE_FILE_PATH}")
    logger.info(f"  Blocked domains:    {BLOCKED_DOMAINS_PATH}")
    logger.info(f"  API URL:            {API_BASE_URL}")
    logger.info(f"  Batch size:         {BATCH_SIZE}")
    logger.info(f"  Poll interval:      {POLL_INTERVAL}s")
    logger.info(f"  Flush interval:     {FLUSH_INTERVAL}s")
    logger.info("=" * 60)

    # Wait for the backend API to be available
    if not wait_for_api(API_BASE_URL):
        logger.error("Cannot start without backend API. Exiting.")
        sys.exit(1)

    # Check if log file exists
    if not os.path.exists(DNSMASQ_LOG_PATH):
        logger.error(f"Log file not found: {DNSMASQ_LOG_PATH}")
        sys.exit(1)

    # Load blocked domains
    blocked_domains = load_blocked_domains(BLOCKED_DOMAINS_PATH)
    last_blocked_reload = time.time()

    # Get last read position
    last_position = get_last_position(STATE_FILE_PATH)
    logger.info(f"Starting from byte position: {last_position}")

    # Pending queries buffer
    pending_queries: List[Dict[str, Any]] = []
    last_flush_time = time.time()

    logger.info("Watching for new DNS queries...")

    while True:
        try:
            # Periodically reload blocked domains list
            if time.time() - last_blocked_reload > BLOCKED_DOMAINS_RELOAD_INTERVAL:
                blocked_domains = load_blocked_domains(BLOCKED_DOMAINS_PATH)
                last_blocked_reload = time.time()

            # Check file size
            if not os.path.exists(DNSMASQ_LOG_PATH):
                logger.warning(f"Log file disappeared: {DNSMASQ_LOG_PATH}")
                time.sleep(POLL_INTERVAL)
                continue

            file_size = os.path.getsize(DNSMASQ_LOG_PATH)

            # Handle log rotation
            if file_size < last_position:
                logger.info("Log file rotated, starting from beginning")
                last_position = 0

            # Read new data if available
            if file_size > last_position:
                with open(DNSMASQ_LOG_PATH, 'r') as f:
                    f.seek(last_position)
                    new_lines = f.readlines()
                    new_position = f.tell()

                if new_lines:
                    queries = parse_log_lines(new_lines, blocked_domains)
                    if queries:
                        pending_queries.extend(queries)

                    last_position = new_position

            # Flush pending queries when batch is full or flush interval elapsed
            now = time.time()
            should_flush = (
                len(pending_queries) >= BATCH_SIZE or
                (pending_queries and now - last_flush_time >= FLUSH_INTERVAL)
            )

            if should_flush and pending_queries:
                batch = pending_queries[:BATCH_SIZE]
                if send_to_api(batch, API_BASE_URL):
                    pending_queries = pending_queries[BATCH_SIZE:]
                    save_position(STATE_FILE_PATH, last_position)
                    logger.info(f"Sent {len(batch)} queries (remaining: {len(pending_queries)})")
                    last_flush_time = now
                else:
                    logger.warning("Failed to send batch, will retry next cycle")
                    # Exponential backoff on failure
                    time.sleep(min(POLL_INTERVAL * 5, 30))

            # Wait before next poll
            time.sleep(POLL_INTERVAL)

        except KeyboardInterrupt:
            logger.info("Shutting down...")
            # Flush remaining queries
            if pending_queries:
                logger.info(f"Flushing {len(pending_queries)} remaining queries...")
                if send_to_api(pending_queries, API_BASE_URL):
                    save_position(STATE_FILE_PATH, last_position)
                    logger.info("Final flush complete")
                else:
                    logger.error("Failed to flush remaining queries")
            break
        except Exception as e:
            logger.error(f"Unexpected error: {e}", exc_info=True)
            time.sleep(POLL_INTERVAL * 2)


if __name__ == '__main__':
    main()
