from collections import defaultdict
from datetime import datetime, timedelta, timezone
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy import func
from sqlalchemy.orm import Session

from app.features.client_behavior.models.client_behavior_rollup import ClientBehaviorRollup
from app.shared.domain_utils import extract_root_domain


def _hour_bucket(ts: datetime) -> datetime:
    if ts.tzinfo is None:
        ts = ts.replace(tzinfo=timezone.utc)
    return ts.replace(minute=0, second=0, microsecond=0)


class BehaviorRollupRepository:
    def __init__(self, db: Session):
        self.db = db

    def upsert_batch(
        self,
        device_id: int,
        queries: List[Tuple[datetime, str]],
        known_roots: Set[Tuple[int, str]],
    ) -> None:
        """queries: list of (timestamp, domain). known_roots: (device_id, root) already seen."""
        if not queries:
            return

        buckets: Dict[datetime, Dict[str, int]] = defaultdict(lambda: {"count": 0, "roots": set(), "new": 0})
        device_known = {r for did, r in known_roots if did == device_id}

        for ts, domain in queries:
            window = _hour_bucket(ts)
            root = extract_root_domain(domain)
            buckets[window]["count"] += 1
            buckets[window]["roots"].add(root)
            if root and (device_id, root) not in known_roots:
                buckets[window]["new"] += 1
                device_known.add(root)
                known_roots.add((device_id, root))

        now = datetime.now(timezone.utc)
        for window_start, data in buckets.items():
            existing = (
                self.db.query(ClientBehaviorRollup)
                .filter(
                    ClientBehaviorRollup.device_id == device_id,
                    ClientBehaviorRollup.window_start == window_start,
                )
                .first()
            )
            unique_count = len(data["roots"])
            if existing:
                existing.query_count += data["count"]
                existing.unique_roots = max(existing.unique_roots, unique_count)
                existing.new_roots += data["new"]
                existing.updated_at = now
            else:
                self.db.add(
                    ClientBehaviorRollup(
                        device_id=device_id,
                        window_start=window_start,
                        query_count=data["count"],
                        unique_roots=unique_count,
                        new_roots=data["new"],
                        hour_utc=window_start.hour,
                        created_at=now,
                        updated_at=now,
                    )
                )

    def get_rollups_for_device(
        self,
        device_id: int,
        since: datetime,
    ) -> List[ClientBehaviorRollup]:
        return (
            self.db.query(ClientBehaviorRollup)
            .filter(
                ClientBehaviorRollup.device_id == device_id,
                ClientBehaviorRollup.window_start >= since,
            )
            .order_by(ClientBehaviorRollup.window_start.asc())
            .all()
        )

    def sum_recent_window(
        self,
        device_id: int,
        since: datetime,
    ) -> Tuple[int, int, int]:
        row = (
            self.db.query(
                func.coalesce(func.sum(ClientBehaviorRollup.query_count), 0),
                func.coalesce(func.sum(ClientBehaviorRollup.unique_roots), 0),
                func.coalesce(func.sum(ClientBehaviorRollup.new_roots), 0),
            )
            .filter(
                ClientBehaviorRollup.device_id == device_id,
                ClientBehaviorRollup.window_start >= since,
            )
            .one()
        )
        return int(row[0]), int(row[1]), int(row[2])
