"""In-memory DNS ingest counters (since process start)."""

from __future__ import annotations

import threading
from collections import Counter, defaultdict
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Set

from app.features.dns_queries.schemas.dns_query import DnsQueryCreate
from app.shared.domain_utils import extract_root_domain, is_noise_domain


@dataclass
class _SiteAggregate:
    root_domain: str
    total_queries: int = 0
    subdomains: Set[str] = field(default_factory=set)
    last_seen: Optional[datetime] = None
    first_seen: Optional[datetime] = None
    blocked: bool = False


class DnsIngestStats:
    """Thread-safe counters updated on every DNS ingest batch."""

    def __init__(self) -> None:
        self._lock = threading.Lock()
        self._started_at = datetime.now(timezone.utc)
        self._total = 0
        self._blocked = 0
        self._blocked_domains: Counter[str] = Counter()
        self._clients: Counter[str] = Counter()
        self._sites: Dict[str, _SiteAggregate] = {}
        self._noise_filtered = 0

    def record(self, queries: List[DnsQueryCreate]) -> None:
        with self._lock:
            for query in queries:
                self._total += 1
                self._clients[query.client_ip] += 1

                if query.blocked:
                    self._blocked += 1
                    self._blocked_domains[query.domain.lower()] += 1

                if is_noise_domain(query.domain):
                    self._noise_filtered += 1
                    continue

                root = extract_root_domain(query.domain)
                site = self._sites.get(root)
                if site is None:
                    site = _SiteAggregate(root_domain=root)
                    self._sites[root] = site

                site.total_queries += 1
                site.subdomains.add(query.domain.lower())
                site.blocked = site.blocked or query.blocked
                ts = query.timestamp
                if site.last_seen is None or ts > site.last_seen:
                    site.last_seen = ts
                if site.first_seen is None or ts < site.first_seen:
                    site.first_seen = ts

    def get_stats(self) -> dict:
        with self._lock:
            total = self._total
            blocked = self._blocked
            now = datetime.now(timezone.utc)
            top_blocked = [
                {"domain": domain, "count": count}
                for domain, count in self._blocked_domains.most_common(10)
            ]
            top_clients = [
                {"client_ip": ip, "count": count}
                for ip, count in self._clients.most_common(10)
            ]
            return {
                "total_queries": total,
                "blocked_queries": blocked,
                "allowed_queries": total - blocked,
                "block_rate": round((blocked / total * 100), 2) if total > 0 else 0,
                "top_blocked_domains": top_blocked,
                "top_clients": top_clients,
                "period": {
                    "start": self._started_at.isoformat(),
                    "end": now.isoformat(),
                },
                "source": "live",
            }

    def get_unique_clients(self) -> List[str]:
        with self._lock:
            return sorted(self._clients.keys())

    def get_grouped_sites(
        self,
        *,
        client_ip: Optional[str] = None,
        blocked_only: bool = False,
        filter_noise: bool = True,
        limit: int = 50,
    ) -> Dict[str, Any]:
        with self._lock:
            sites: List[dict] = []
            for site in self._sites.values():
                if blocked_only and not site.blocked:
                    continue
                sites.append(
                    {
                        "root_domain": site.root_domain,
                        "total_queries": site.total_queries,
                        "subdomains": sorted(site.subdomains),
                        "last_seen": site.last_seen.isoformat() if site.last_seen else None,
                        "first_seen": site.first_seen.isoformat() if site.first_seen else None,
                        "blocked": site.blocked,
                    }
                )

            sites.sort(
                key=lambda x: x["last_seen"] or "",
                reverse=True,
            )
            now = datetime.now(timezone.utc)
            return {
                "sites": sites[:limit],
                "total_sites": len(sites),
                "noise_filtered": self._noise_filtered,
                "period": {
                    "start": self._started_at.isoformat(),
                    "end": now.isoformat(),
                },
                "source": "live",
            }


ingest_stats = DnsIngestStats()
