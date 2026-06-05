"""Payload builders and helpers for integration tests."""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Any, Optional


def dns_query_payload(
    *,
    client_ip: str = "10.0.0.10",
    domain: str = "blocked.test",
    blocked: bool = True,
    timestamp: Optional[datetime] = None,
    **extra: Any,
) -> dict[str, Any]:
    payload: dict[str, Any] = {
        "timestamp": (timestamp or datetime.now(timezone.utc)).isoformat(),
        "client_ip": client_ip,
        "domain": domain,
        "blocked": blocked,
    }
    payload.update(extra)
    return payload


def enroll_payload(
    *,
    device_id: str,
    public_key: str,
    hostname: Optional[str] = None,
) -> dict[str, str]:
    payload = {"device_id": device_id, "public_key": public_key}
    if hostname:
        payload["hostname"] = hostname
    return payload


def usage_report_payload(
    *,
    device_id: str,
    interval_sec: float = 5.0,
    rx_bytes: int = 1000,
    tx_bytes: int = 500,
    delta_rx_bytes: int = 1000,
    delta_tx_bytes: int = 500,
) -> dict[str, Any]:
    return {
        "device_id": device_id,
        "interval_sec": interval_sec,
        "rx_bytes": rx_bytes,
        "tx_bytes": tx_bytes,
        "delta_rx_bytes": delta_rx_bytes,
        "delta_tx_bytes": delta_tx_bytes,
    }
