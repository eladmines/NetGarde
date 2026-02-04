from typing import List, Optional
from datetime import datetime
from app.features.dns_queries.repositories.dns_query_repository import DnsQueryRepository
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate, DnsQueryResponse


class DnsQueryService:
    def __init__(self, repository: DnsQueryRepository):
        self.repository = repository

    def create_query(self, dns_query_data: DnsQueryCreate) -> DnsQueryResponse:
        dns_query = self.repository.create(dns_query_data)
        return DnsQueryResponse.model_validate(dns_query)

    def bulk_create_queries(self, queries: List[DnsQueryCreate]) -> dict:
        count = self.repository.bulk_create(queries)
        return {"inserted": count}

    def get_queries(
        self,
        page: int = 1,
        page_size: int = 50,
        domain_search: Optional[str] = None,
        client_ip: Optional[str] = None,
        blocked_only: bool = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        items, total = self.repository.get_all(
            page=page,
            page_size=page_size,
            domain_search=domain_search,
            client_ip=client_ip,
            blocked_only=blocked_only,
            start_date=start_date,
            end_date=end_date
        )
        return {
            "items": [DnsQueryResponse.model_validate(item) for item in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }

    def get_stats(
        self,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        return self.repository.get_stats(start_date=start_date, end_date=end_date)

    def get_unique_clients(self) -> List[str]:
        return self.repository.get_unique_clients()

    def cleanup_old_records(self, days: int = 30) -> dict:
        count = self.repository.delete_old_records(days=days)
        return {"deleted": count}
