"""Decide which DNS queries are written to RDS."""

from app.features.dns_queries.schemas.dns_query import DnsQueryCreate
from app.shared.config import settings


def should_persist_query(query: DnsQueryCreate) -> bool:
    """Return True if this query should be stored in RDS."""
    if settings.PERSIST_ALL_DNS:
        return True
    return query.blocked


def filter_queries_to_persist(queries: list[DnsQueryCreate]) -> list[DnsQueryCreate]:
    return [q for q in queries if should_persist_query(q)]
