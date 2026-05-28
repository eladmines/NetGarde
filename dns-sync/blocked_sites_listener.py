#!/usr/bin/env python3
"""
Listen to PostgreSQL NOTIFY events for blocked_sites changes and trigger dns-sync.

This service subscribes to channel: blocked_sites_changed
When an event arrives, it runs SYNC_COMMAND (defaults to run-sync.sh).
"""

import json
import logging
import os
import select
import subprocess
import time
from typing import Optional

import psycopg2
from psycopg2.extensions import ISOLATION_LEVEL_AUTOCOMMIT


logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(levelname)s - [blocked-sites-listener] %(message)s",
)
logger = logging.getLogger(__name__)

CHANNEL_NAME = os.getenv("DB_NOTIFY_CHANNEL", "blocked_sites_changed")
SYNC_COMMAND = os.getenv("SYNC_COMMAND", "/home/ubuntu/netgarde/dns-sync/run-sync.sh")
RECONNECT_DELAY = int(os.getenv("RECONNECT_DELAY", "5"))
LISTEN_TIMEOUT_SECONDS = int(os.getenv("LISTEN_TIMEOUT_SECONDS", "60"))


def normalize_db_url(raw_url: str) -> str:
    """Convert SQLAlchemy URL to a psycopg2-compatible URL when needed."""
    if raw_url.startswith("postgresql+psycopg2://"):
        return "postgresql://" + raw_url[len("postgresql+psycopg2://") :]
    return raw_url


def run_sync_command() -> bool:
    """Run the configured sync command."""
    try:
        logger.info("Running sync command: %s", SYNC_COMMAND)
        result = subprocess.run(
            ["bash", "-lc", SYNC_COMMAND],
            capture_output=True,
            text=True,
            timeout=180,
        )
        if result.returncode != 0:
            logger.error("Sync command failed (code=%s): %s", result.returncode, result.stderr.strip())
            return False
        if result.stdout.strip():
            logger.info("Sync output: %s", result.stdout.strip())
        logger.info("Sync command completed successfully")
        return True
    except Exception as e:
        logger.error("Error running sync command: %s", e, exc_info=True)
        return False


def connect(db_url: str):
    conn = psycopg2.connect(db_url)
    conn.set_isolation_level(ISOLATION_LEVEL_AUTOCOMMIT)
    return conn


def parse_payload(payload: Optional[str]) -> str:
    if not payload:
        return "{}"
    try:
        obj = json.loads(payload)
        return json.dumps(obj)
    except Exception:
        return payload


def listen_forever(db_url: str) -> None:
    while True:
        conn = None
        try:
            conn = connect(db_url)
            cursor = conn.cursor()
            cursor.execute(f"LISTEN {CHANNEL_NAME};")
            logger.info("Listening on PostgreSQL channel '%s'", CHANNEL_NAME)

            while True:
                ready = select.select([conn], [], [], LISTEN_TIMEOUT_SECONDS)
                if ready == ([], [], []):
                    continue

                conn.poll()
                while conn.notifies:
                    notify = conn.notifies.pop(0)
                    logger.info("Received notify: channel=%s payload=%s", notify.channel, parse_payload(notify.payload))
                    run_sync_command()
        except Exception as e:
            logger.error("Listener error: %s", e, exc_info=True)
            logger.info("Reconnecting in %s seconds...", RECONNECT_DELAY)
            time.sleep(RECONNECT_DELAY)
        finally:
            if conn:
                try:
                    conn.close()
                except Exception:
                    pass


def main() -> int:
    raw_db_url = os.getenv("DB_URL", "").strip()
    if not raw_db_url:
        logger.error("DB_URL is not set")
        return 1

    db_url = normalize_db_url(raw_db_url)
    logger.info("Starting blocked sites DB listener")
    logger.info("Channel: %s", CHANNEL_NAME)
    logger.info("Sync command: %s", SYNC_COMMAND)
    listen_forever(db_url)
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
