#!/usr/bin/env python3
"""
DNS Log Parser for NetGarde
Parses dnsmasq query logs and sends them to the NetGarde API.
Designed to run as a cron job on the host machine.
"""

import os
import sys
import re
import json
from datetime import datetime, timezone
from typing import List, Dict, Any, Optional, Set

from log_config import setup_logging, structured_extra
from noise_filter import is_noise_domain

logger = setup_logging(service="log-parser", logger_name=__name__)

DNSMASQ_LOG_PATH = os.getenv('DNSMASQ_LOG_PATH', '/var/log/dnsmasq.log')
STATE_FILE_PATH = os.getenv('STATE_FILE_PATH', '/var/lib/netgarde/log_parser_state')
BLOCKED_DOMAINS_PATH = os.getenv('BLOCKED_DOMAINS_PATH', '/etc/dnsmasq.d/blocked-domains.conf')
API_BASE_URL = os.getenv('API_BASE_URL', 'http://localhost:8000')
BATCH_SIZE = int(os.getenv('BATCH_SIZE', '100'))

QUERY_PATTERN = re.compile(
    r'^(\w{3}\s+\d+\s+\d{2}:\d{2}:\d{2})\s+'
    r'dnsmasq\[\d+\]:\s+'
    r'query\[(\w+)\]\s+'
    r'(\S+)\s+'
    r'from\s+(\S+)'
)


def load_blocked_domains(config_path: str) -> Set[str]:
    blocked = set()
    try:
        if not os.path.exists(config_path):
            logger.warning(
                "Blocked domains file not found",
                extra=structured_extra("blocked_domains_missing", path=config_path),
            )
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
    except Exception as e:
        logger.error(
            "Failed to load blocked domains",
            extra=structured_extra("blocked_domains_load_failed", error=str(e)),
        )

    return blocked


def get_last_position(state_file: str) -> int:
    try:
        if os.path.exists(state_file):
            with open(state_file, 'r') as f:
                content = f.read().strip()
                if content:
                    return int(content)
    except (ValueError, IOError) as e:
        logger.warning(
            "Failed to read log parser state file",
            extra=structured_extra("log_parser_state_read_failed", error=str(e)),
        )
    return 0


def save_position(state_file: str, position: int):
    try:
        state_dir = os.path.dirname(state_file)
        if state_dir:
            os.makedirs(state_dir, exist_ok=True)
        with open(state_file, 'w') as f:
            f.write(str(position))
    except IOError as e:
        logger.error(
            "Failed to save log parser state file",
            extra=structured_extra("log_parser_state_write_failed", error=str(e)),
        )


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
    import urllib.request
    import urllib.error

    if not queries:
        return True

    url = f"{api_url.rstrip('/')}/dns-queries/bulk"
    total_sent = 0

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
                else:
                    logger.error(
                        "DNS ingest API error",
                        extra=structured_extra("dns_ingest_failed", status_code=response.status),
                    )
                    return False

        except urllib.error.HTTPError as e:
            body = e.read().decode('utf-8', errors='replace')
            logger.error(
                "DNS ingest HTTP error",
                extra=structured_extra(
                    "dns_ingest_failed",
                    status_code=e.code,
                    body=body[:500],
                ),
            )
            return False
        except urllib.error.URLError as e:
            logger.error(
                "DNS ingest connection error",
                extra=structured_extra("dns_ingest_failed", error=str(e.reason)),
            )
            return False
        except Exception as e:
            logger.error(
                "DNS ingest failed",
                extra=structured_extra("dns_ingest_failed", error=str(e)),
            )
            return False

    blocked_count = sum(1 for q in queries if q.get("blocked"))
    logger.info(
        "DNS log parser ingest completed",
        extra=structured_extra(
            "dns_parser_ingest_ok",
            query_count=total_sent,
            blocked_count=blocked_count,
        ),
    )
    return True


def main():
    if not os.path.exists(DNSMASQ_LOG_PATH):
        logger.error(
            "dnsmasq log not found",
            extra=structured_extra("dnsmasq_log_missing", path=DNSMASQ_LOG_PATH),
        )
        sys.exit(1)

    blocked_domains = load_blocked_domains(BLOCKED_DOMAINS_PATH)
    last_position = get_last_position(STATE_FILE_PATH)
    file_size = os.path.getsize(DNSMASQ_LOG_PATH)

    if file_size < last_position:
        last_position = 0

    if file_size == last_position:
        return

    new_lines = []
    with open(DNSMASQ_LOG_PATH, 'r') as f:
        f.seek(last_position)
        new_lines = f.readlines()
        new_position = f.tell()

    if not new_lines:
        save_position(STATE_FILE_PATH, new_position)
        return

    queries = parse_log_lines(new_lines, blocked_domains)

    if queries:
        if send_to_api(queries, API_BASE_URL):
            save_position(STATE_FILE_PATH, new_position)
        else:
            logger.error(
                "Log parser ingest failed; position not updated",
                extra=structured_extra("dns_parser_ingest_failed", query_count=len(queries)),
            )
            sys.exit(1)
    else:
        save_position(STATE_FILE_PATH, new_position)


if __name__ == '__main__':
    main()
