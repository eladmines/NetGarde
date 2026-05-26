from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Set, Tuple

from sqlalchemy.orm import Session

from app.features.client_behavior.repositories.behavior_rollup_repository import BehaviorRollupRepository
from app.features.devices.repositories.device_repository import DeviceRepository
from app.features.dns_queries.models.domain_first_seen import DomainFirstSeen
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate
from app.shared.domain_utils import extract_root_domain, is_noise_domain
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class ClientBehaviorAggregator:
    """Update hourly behavior rollups from DNS ingest batches."""

    def __init__(self, db: Session):
        self.db = db
        self.rollup_repo = BehaviorRollupRepository(db)
        self.device_repo = DeviceRepository(db)

    def process_queries(self, queries: List[DnsQueryCreate]) -> None:
        if not queries:
            return

        by_ip: Dict[str, List[DnsQueryCreate]] = defaultdict(list)
        for q in queries:
            if is_noise_domain(q.domain):
                continue
            by_ip[q.client_ip].append(q)

        known_roots = self._load_known_roots()

        for client_ip, batch in by_ip.items():
            device = self.device_repo.get_by_client_ip(client_ip)
            if not device:
                continue
            tuples: List[Tuple[datetime, str]] = []
            for q in batch:
                ts = q.timestamp
                if ts.tzinfo is None:
                    ts = ts.replace(tzinfo=timezone.utc)
                tuples.append((ts, q.domain))
            self.rollup_repo.upsert_batch(device.id, tuples, known_roots)

    def _load_known_roots(self) -> Set[Tuple[int, str]]:
        rows = self.db.query(DomainFirstSeen.client_ip, DomainFirstSeen.root_domain).all()
        known: Set[Tuple[int, str]] = set()
        for client_ip, root in rows:
            device = self.device_repo.get_by_client_ip(client_ip)
            if device:
                known.add((device.id, root.lower()))
        return known
