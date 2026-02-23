from typing import Protocol, Optional, List, Dict, Any
from datetime import datetime
from sqlalchemy.orm import Session
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate, DnsQueryResponse


class IDnsQueryService(Protocol):
    """Protocol defining the DNS query service interface."""

    def create_query(self, dns_query_data: DnsQueryCreate, db: Session) -> DnsQueryResponse:
        """Create a single DNS query log entry."""
        ...

    def bulk_create_queries(self, queries: List[DnsQueryCreate], db: Session) -> dict:
        """Create multiple DNS queries at once. Returns count of inserted records."""
        ...

    def get_queries(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 50,
        domain_search: Optional[str] = None,
        client_ip: Optional[str] = None,
        blocked_only: bool = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get paginated DNS queries with optional filters."""
        ...

    def get_stats(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get DNS query statistics."""
        ...

    def get_unique_clients(self, db: Session) -> List[str]:
        """Get list of unique client IPs."""
        ...

    def cleanup_old_records(self, db: Session, days: int = 30) -> dict:
        """Delete records older than specified days."""
        ...

    def get_grouped_by_site(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        client_ip: Optional[str] = None,
        blocked_only: bool = False,
        filter_noise: bool = True,
        limit: int = 50
    ) -> dict:
        """Get DNS queries grouped by root domain."""
        ...
