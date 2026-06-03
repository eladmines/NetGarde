from __future__ import annotations

import json
import logging
from dataclasses import dataclass
from datetime import datetime, timezone
from typing import Any, Optional

from sqlalchemy.orm import Session

from app.features.devices.models.device import Device
from app.features.vpn.models.ip_lease import IpLease
from app.features.vpn.models.vpn_peer import VpnPeer
from app.features.vpn.schemas.usage import UsageReportRequest
from app.features.vpn.schemas.usage_history import UsageHistoryPoint, UsageHistoryResponse
from app.features.vpn.schemas.usage_live import DeviceUsageLiveItem, DeviceUsageLiveResponse
from app.shared.config import settings
from app.shared.redis_client import get_redis, redis_available

logger = logging.getLogger(__name__)

MIB = 1024 * 1024
DEVICE_KEY_PREFIX = "ng:usage:device:"
SERVER_AGGREGATE_KEY = "ng:usage:server:aggregate"


@dataclass(frozen=True)
class UsageRecordResult:
    aggregate_point: UsageHistoryPoint
    live_items: list[DeviceUsageLiveItem]


def _window_ms() -> int:
    minutes = max(1, min(int(settings.USAGE_HISTORY_MINUTES), 24 * 60))
    return minutes * 60 * 1000


def _ms_now() -> int:
    return int(datetime.now(timezone.utc).timestamp() * 1000)


def _iso_from_ms(ms: int) -> datetime:
    return datetime.fromtimestamp(ms / 1000.0, tz=timezone.utc)


def _rates_from_payload(payload: UsageReportRequest) -> tuple[float, float, float]:
    interval = float(payload.interval_sec) or 1.0
    rx_rate = (payload.delta_rx_bytes / MIB) / interval
    tx_rate = (payload.delta_tx_bytes / MIB) / interval
    return round(rx_rate, 3), round(tx_rate, 3), round(rx_rate + tx_rate, 3)


def record_sample(payload: UsageReportRequest) -> UsageRecordResult:
    if not redis_available():
        raise RuntimeError("Redis is not available")

    r = get_redis()
    now_ms = _ms_now()
    cutoff = now_ms - _window_ms()
    device_id = payload.device_id.strip()
    rx_rate, tx_rate, total_rate = _rates_from_payload(payload)

    device_doc = {
        "vpn_device_id": device_id,
        "recorded_at_ms": now_ms,
        "interval_sec": payload.interval_sec,
        "rx_bytes": payload.rx_bytes,
        "tx_bytes": payload.tx_bytes,
        "delta_rx_bytes": payload.delta_rx_bytes,
        "delta_tx_bytes": payload.delta_tx_bytes,
        "rx_mib_per_sec": rx_rate,
        "tx_mib_per_sec": tx_rate,
        "total_mib_per_sec": total_rate,
    }
    device_key = f"{DEVICE_KEY_PREFIX}{device_id}"
    member = json.dumps(device_doc, separators=(",", ":"))
    pipe = r.pipeline()
    pipe.zadd(device_key, {member: now_ms})
    pipe.zremrangebyscore(device_key, 0, cutoff)
    pipe.execute()

    live_items = _list_live_raw(r, cutoff)
    reporting = len(live_items)
    agg_rx = sum(i.rx_mib_per_sec for i in live_items)
    agg_tx = sum(i.tx_mib_per_sec for i in live_items)
    agg_total = sum(i.total_mib_per_sec for i in live_items)

    agg_doc = {
        "recorded_at_ms": now_ms,
        "rx_mib_per_sec": round(agg_rx, 3),
        "tx_mib_per_sec": round(agg_tx, 3),
        "total_mib_per_sec": round(agg_total, 3),
        "reporting_clients": reporting,
    }
    agg_member = json.dumps(agg_doc, separators=(",", ":"))
    pipe = r.pipeline()
    pipe.zadd(SERVER_AGGREGATE_KEY, {agg_member: now_ms})
    pipe.zremrangebyscore(SERVER_AGGREGATE_KEY, 0, cutoff)
    pipe.execute()

    aggregate_point = UsageHistoryPoint(
        recorded_at=_iso_from_ms(now_ms),
        rx_mib_per_sec=agg_doc["rx_mib_per_sec"],
        tx_mib_per_sec=agg_doc["tx_mib_per_sec"],
        total_mib_per_sec=agg_doc["total_mib_per_sec"],
        reporting_clients=reporting,
    )
    return UsageRecordResult(aggregate_point=aggregate_point, live_items=live_items)


def _parse_device_doc(raw: str, score_ms: int) -> Optional[DeviceUsageLiveItem]:
    try:
        doc = json.loads(raw)
    except json.JSONDecodeError:
        return None
    recorded_at = _iso_from_ms(int(doc.get("recorded_at_ms", score_ms)))
    return DeviceUsageLiveItem(
        device_id=None,
        vpn_device_id=str(doc.get("vpn_device_id", "")),
        client_ip=None,
        recorded_at=recorded_at,
        interval_sec=float(doc.get("interval_sec", 1)),
        rx_bytes=int(doc.get("rx_bytes", 0)),
        tx_bytes=int(doc.get("tx_bytes", 0)),
        delta_rx_bytes=int(doc.get("delta_rx_bytes", 0)),
        delta_tx_bytes=int(doc.get("delta_tx_bytes", 0)),
        rx_mib_per_sec=float(doc.get("rx_mib_per_sec", 0)),
        tx_mib_per_sec=float(doc.get("tx_mib_per_sec", 0)),
        total_mib_per_sec=float(doc.get("total_mib_per_sec", 0)),
    )


def _list_live_raw(r, cutoff_ms: int) -> list[DeviceUsageLiveItem]:
    items: list[DeviceUsageLiveItem] = []
    cursor = 0
    while True:
        cursor, keys = r.scan(cursor=cursor, match=f"{DEVICE_KEY_PREFIX}*", count=100)
        for key in keys:
            rows = r.zrevrange(key, 0, 0, withscores=True)
            if not rows:
                continue
            raw, score = rows[0]
            if score < cutoff_ms:
                continue
            item = _parse_device_doc(raw, int(score))
            if item:
                items.append(item)
        if cursor == 0:
            break
    return items


def enrich_live_items(db: Session, items: list[DeviceUsageLiveItem]) -> list[DeviceUsageLiveItem]:
    if not items:
        return items
    vpn_ids = [i.vpn_device_id for i in items if i.vpn_device_id]
    identity = _identity_map(db, vpn_ids)
    enriched: list[DeviceUsageLiveItem] = []
    for item in items:
        meta = identity.get(item.vpn_device_id, {})
        enriched.append(
            item.model_copy(
                update={
                    "device_id": meta.get("device_id"),
                    "client_ip": meta.get("client_ip"),
                }
            )
        )
    return enriched


def _identity_map(db: Session, vpn_device_ids: list[str]) -> dict[str, dict[str, Any]]:
    if not vpn_device_ids:
        return {}
    rows = (
        db.query(VpnPeer.device_id, Device.id, IpLease.ip)
        .outerjoin(IpLease, IpLease.peer_id == VpnPeer.id)
        .outerjoin(Device, Device.ip_lease_id == IpLease.id)
        .filter(VpnPeer.device_id.in_(vpn_device_ids), IpLease.released_at.is_(None))
        .all()
    )
    out: dict[str, dict[str, Any]] = {}
    for vpn_id, device_id, client_ip in rows:
        out[vpn_id] = {"device_id": device_id, "client_ip": client_ip}
    return out


def list_live(db: Session, *, max_age_sec: Optional[int] = None) -> DeviceUsageLiveResponse:
    age = max_age_sec if max_age_sec is not None else settings.USAGE_LIVE_MAX_AGE_SEC
    age = max(5, min(age, 300))
    cutoff_ms = _ms_now() - age * 1000
    if not redis_available():
        return DeviceUsageLiveResponse(items=[], max_age_sec=age)

    raw = _list_live_raw(get_redis(), cutoff_ms)
    items = enrich_live_items(db, raw)
    return DeviceUsageLiveResponse(items=items, max_age_sec=age)


def list_history(*, minutes: Optional[int] = None) -> UsageHistoryResponse:
    mins = minutes if minutes is not None else settings.USAGE_HISTORY_MINUTES
    mins = max(1, min(mins, 24 * 60))
    window_ms = mins * 60 * 1000
    now_ms = _ms_now()
    cutoff_ms = now_ms - window_ms

    if not redis_available():
        return UsageHistoryResponse(points=[], minutes=mins)

    r = get_redis()
    rows = r.zrangebyscore(SERVER_AGGREGATE_KEY, cutoff_ms, now_ms, withscores=True)
    points: list[UsageHistoryPoint] = []
    for raw, score_ms in rows:
        try:
            doc = json.loads(raw)
        except json.JSONDecodeError:
            continue
        points.append(
            UsageHistoryPoint(
                recorded_at=_iso_from_ms(int(doc.get("recorded_at_ms", score_ms))),
                rx_mib_per_sec=float(doc.get("rx_mib_per_sec", 0)),
                tx_mib_per_sec=float(doc.get("tx_mib_per_sec", 0)),
                total_mib_per_sec=float(doc.get("total_mib_per_sec", 0)),
                reporting_clients=int(doc.get("reporting_clients", 0)),
            )
        )
    return UsageHistoryResponse(points=points, minutes=mins)
