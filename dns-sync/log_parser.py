#!/usr/bin/env python3
"""
DNS Log Parser for NetGarde
Parses dnsmasq query logs and sends them to the NetGarde API.
Designed to run as a cron job on the host machine.

Dnsmasq log line examples:
  Feb  9 12:34:56 dnsmasq[1234]: query[A] google.com from 10.0.0.1
  Feb  9 12:34:56 dnsmasq[1234]: forwarded google.com to 8.8.8.8
  Feb  9 12:34:56 dnsmasq[1234]: reply google.com is 142.250.80.46
  Feb  9 12:34:56 dnsmasq[1234]: config blocked.com is 0.0.0.0
"""

import os
import sys
import re
import json
import logging
from datetime import datetime
from typing import List, Dict, Any, Optional, Set

# Configure logging
logging.basicConfig(
    level=logging.INFO,
    format='%(asctime)s - %(levelname)s - [log_parser] %(message)s'
)
logger = logging.getLogger(__name__)

# Configuration from environment variables
DNSMASQ_LOG_PATH = os.getenv('DNSMASQ_LOG_PATH', '/var/log/dnsmasq.log')
STATE_FILE_PATH = os.getenv('STATE_FILE_PATH', '/var/lib/netgarde/log_parser_state')
BLOCKED_DOMAINS_PATH = os.getenv('BLOCKED_DOMAINS_PATH', '/etc/dnsmasq.d/blocked-domains.conf')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))

# Regex to parse dnsmasq "query" log lines
# Format: "Feb  9 12:34:56 dnsmasq[1234]: query[A] google.com from 10.0.0.1"
QUERY_PATTERN = re.compile(
    r'^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+'   # timestamp (e.g. "Feb  9 12:34:56")
    r'dnsmasq\[\d+\]:\s+'                         # dnsmasq process info
    r'query\[(\w+)\]\s+'                           # query type (A, AAAA, PTR, etc.)
    r'(\S+)\s+'                                    # domain name
    r'from\s+(\S+)'                                # client IP
)


def load_blocked_domains(config_path: str) -> Set[str]:
    """
    Load blocked domains from the dnsmasq blocked-domains.conf file.
    Each line looks like: address=/example.com/0.0.0.0
    """
    blocked = set()
    try:
        if not os.path.exists(config_path):
            logger.warning(f"Blocked domains file not found: {config_path}")
            return blocked

        with open(config_path, 'r') as f:
            for line in f:
                line = line.strip()
                if line.startswith('address=/'):
                    # Format: address=/domain.com/0.0.0.0
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
    """
    Parse dnsmasq log timestamp (e.g. 'Feb  9 12:34:56') into a datetime object.
    dnsmasq logs don't include the year, so we use the current year.
    """
    try:
        current_year = datetime.now().year
        dt = datetime.strptime(f"{current_year} {timestamp_str}", "%Y %b %d %H:%M:%S")
        return dt
    except ValueError as e:
        logger.debug(f"Could not parse timestamp '{timestamp_str}': {e}")
        return None


def parse_log_lines(lines: List[str], blocked_domains: Set[str]) -> List[Dict[str, Any]]:
    """
    Parse dnsmasq log lines into DNS query records.
    Only 'query[...]' lines are parsed — these contain client IP and domain info.
    Deduplicates by (timestamp, domain, client_ip) to avoid double-counting
    A and AAAA queries for the same lookup.
    """
    queries = []
    seen = set()  # Track (timestamp, domain, client_ip) to deduplicate

    for line in lines:
        match = QUERY_PATTERN.search(line)
        if not match:
            continue

        timestamp_str, query_type, domain, client_ip = match.groups()

        # Parse timestamp
        timestamp = parse_timestamp(timestamp_str)
        if not timestamp:
            continue

        # Skip internal/noise queries (like localhost, arpa, etc.)
        if domain.endswith('.in-addr.arpa') or domain.endswith('.ip6.arpa'):
            continue

        # Deduplicate: keep only one entry per (timestamp, domain, client_ip)
        dedup_key = (timestamp.isoformat(), domain.lower(), client_ip)
        if dedup_key in seen:
            continue
        seen.add(dedup_key)

        # Check if domain is in the blocked list
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
        logger.info("No queries to send")
        return True

    url = f"{api_url.rstrip('/')}/dns-queries/bulk"
    total_sent = 0

    # Send in batches to avoid huge payloads
    for i in range(0, len(queries), BATCH_SIZE):
        batch = queries[i:i + BATCH_SIZE]
        payload = json.dumps({"queries": batch}).encode('utf-8')

        try:
            req = urllib.request.Request(
                url,
                data=payload,
                headers={'Content-Type': 'application/json'},
                method='POST'
            )

            with urllib.request.urlopen(req, timeout=30) as response:
                if response.status in (200, 201):
                    total_sent += len(batch)
                    logger.info(f"Sent batch of {len(batch)} queries (total: {total_sent}/{len(queries)})")
                else:
                    logger.error(f"API returned status {response.status}")
                    return False

        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            logger.error(f"HTTP error sending batch to API: {e.code} - {body}")
            return False
        except urllib.error.URLError as e:
            logger.error(f"URL error sending batch to API: {e.reason}")
            return False
        except Exception as e:
            logger.error(f"Error sending batch to API: {e}")
            return False

    logger.info(f"Successfully sent {total_sent} queries to API")
    return True


def main():
    """Main entry point for the log parser."""
    logger.info("DNS Log Parser started")
    logger.info(f"  Log file:        {DNSMASQ_LOG_PATH}")
    logger.info(f"  State file:      {STATE_FILE_PATH}")
    logger.info(f"  Blocked domains: {BLOCKED_DOMAINS_PATH}")
    logger.info(f"  API URL:         {API_BASE_URL}")
    logger.info(f"  Batch size:      {BATCH_SIZE}")

    # Check if log file exists
    if not os.path.exists(DNSMASQ_LOG_PATH):
        logger.error(f"Log file not found: {DNSMASQ_LOG_PATH}")
        sys.exit(1)

    # Load blocked domains list
    blocked_domains = load_blocked_domains(BLOCKED_DOMAINS_PATH)

    # Get last read position
    last_position = get_last_position(STATE_FILE_PATH)
    file_size = os.path.getsize(DNSMASQ_LOG_PATH)

    # Handle log rotation: if file is smaller than last position, start from beginning
    if file_size < last_position:
        logger.info("Log file appears to have been rotated, starting from beginning")
        last_position = 0

    # Nothing new to read
    if file_size == last_position:
        logger.info("No new log data to process")
        return

    logger.info(f"Reading from byte {last_position} to {file_size} ({file_size - last_position} new bytes)")

    # Read new lines from where we left off
    new_lines = []
    with open(DNSMASQ_LOG_PATH, 'r') as f:
        f.seek(last_position)
        new_lines = f.readlines()
        new_position = f.tell()

    if not new_lines:
        logger.info("No new lines to process")
        save_position(STATE_FILE_PATH, new_position)
        return

    logger.info(f"Read {len(new_lines)} new lines from log")

    # Parse the log lines
    queries = parse_log_lines(new_lines, blocked_domains)
    logger.info(f"Parsed {len(queries)} DNS queries from {len(new_lines)} log lines")

    if queries:
        # Send to API
        if send_to_api(queries, API_BASE_URL):
            # Only update position after successful send
            save_position(STATE_FILE_PATH, new_position)
            logger.info("Log parser completed successfully")
        else:
            logger.error("Failed to send queries to API — position NOT updated (will retry next run)")
            sys.exit(1)
    else:
        # No relevant queries found, still update position so we don't re-read
        save_position(STATE_FILE_PATH, new_position)
        logger.info("No DNS queries found in new log lines, position updated")


if __name__ == '__main__':
    main()
