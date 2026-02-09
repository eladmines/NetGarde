from sqlalchemy.orm import Session
from sqlalchemy import func, desc
from typing import List, Optional
from datetime import datetime, timedelta
from app.features.dns_queries.models.dns_query import DnsQuery
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate


class DnsQueryRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, dns_query_data: DnsQueryCreate) -> DnsQuery:
        dns_query = DnsQuery(
            timestamp=dns_query_data.timestamp,
            client_ip=dns_query_data.client_ip,
            domain=dns_query_data.domain,
            query_type=dns_query_data.query_type,
            action=dns_query_data.action,
            blocked=dns_query_data.blocked
        )
        self.db.add(dns_query)
        self.db.commit()
        self.db.refresh(dns_query)
        return dns_query

    def bulk_create(self, queries: List[DnsQueryCreate]) -> int:
        """Create multiple DNS queries at once. Returns the count of inserted records."""
        dns_queries = [
            DnsQuery(
                timestamp=q.timestamp,
                client_ip=q.client_ip,
                domain=q.domain,
                query_type=q.query_type,
                action=q.action,
                blocked=q.blocked
            )
            for q in queries
        ]
        self.db.bulk_save_objects(dns_queries)
        self.db.commit()
        return len(dns_queries)

    def get_all(
        self,
        page: int = 1,
        page_size: int = 50,
        domain_search: Optional[str] = None,
        client_ip: Optional[str] = None,
        blocked_only: bool = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> tuple[List[DnsQuery], int]:
        """Get paginated DNS queries with optional filters."""
        query = self.db.query(DnsQuery)

        # Apply filters
        if domain_search:
            query = query.filter(DnsQuery.domain.ilike(f"%{domain_search}%"))
        if client_ip:
            query = query.filter(DnsQuery.client_ip == client_ip)
        if blocked_only:
            query = query.filter(DnsQuery.blocked == True)
        if start_date:
            query = query.filter(DnsQuery.timestamp >= start_date)
        if end_date:
            query = query.filter(DnsQuery.timestamp <= end_date)

        # Get total count
        total = query.count()

        # Apply pagination and ordering
        offset = (page - 1) * page_size
        items = query.order_by(desc(DnsQuery.timestamp)).offset(offset).limit(page_size).all()

        return items, total

    def get_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        """Get statistics about DNS queries."""
        if not start_date:
            start_date = datetime.now() - timedelta(days=1)
        if not end_date:
            end_date = datetime.now()

        query = self.db.query(DnsQuery).filter(
            DnsQuery.timestamp >= start_date,
            DnsQuery.timestamp <= end_date
        )

        total_queries = query.count()
        blocked_queries = query.filter(DnsQuery.blocked == True).count()
        
        # Top blocked domains
        top_blocked = self.db.query(
            DnsQuery.domain,
            func.count(DnsQuery.id).label('count')
        ).filter(
            DnsQuery.timestamp >= start_date,
            DnsQuery.timestamp <= end_date,
            DnsQuery.blocked == True
        ).group_by(DnsQuery.domain).order_by(desc('count')).limit(10).all()

        # Top clients
        top_clients = self.db.query(
            DnsQuery.client_ip,
            func.count(DnsQuery.id).label('count')
        ).filter(
            DnsQuery.timestamp >= start_date,
            DnsQuery.timestamp <= end_date
        ).group_by(DnsQuery.client_ip).order_by(desc('count')).limit(10).all()

        return {
            "total_queries": total_queries,
            "blocked_queries": blocked_queries,
            "allowed_queries": total_queries - blocked_queries,
            "block_rate": round((blocked_queries / total_queries * 100), 2) if total_queries > 0 else 0,
            "top_blocked_domains": [{"domain": d, "count": c} for d, c in top_blocked],
            "top_clients": [{"client_ip": ip, "count": c} for ip, c in top_clients],
            "period": {
                "start": start_date.isoformat(),
                "end": end_date.isoformat()
            }
        }

    def get_unique_clients(self) -> List[str]:
        """Get list of unique client IPs."""
        result = self.db.query(DnsQuery.client_ip).distinct().all()
        return [r[0] for r in result]

    def delete_old_records(self, days: int = 30) -> int:
        """Delete records older than specified days. Returns count of deleted records."""
        cutoff_date = datetime.now() - timedelta(days=days)
        count = self.db.query(DnsQuery).filter(DnsQuery.timestamp < cutoff_date).delete()
        self.db.commit()
        return count
