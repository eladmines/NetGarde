from typing import List, Optional
from datetime import datetime
from sqlalchemy.orm import Session
from app.features.dns_queries.repositories.dns_query_repository import DnsQueryRepository
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate, DnsQueryResponse
from app.features.dns_queries.services.dns_query_service_interface import IDnsQueryService
from app.features.devices.repositories.device_repository import DeviceRepository
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class DnsQueryService:
    """Implementation of IDnsQueryService."""

    def create_query(self, dns_query_data: DnsQueryCreate, db: Session) -> DnsQueryResponse:
        repository = DnsQueryRepository(db)
        logger.info("Creating DNS query", extra={"domain": dns_query_data.domain})
        dns_query = repository.create(dns_query_data)
        logger.info("DNS query created", extra={"id": getattr(dns_query, "id", None)})
        return DnsQueryResponse.model_validate(dns_query)

    def bulk_create_queries(self, queries: List[DnsQueryCreate], db: Session) -> dict:
        repository = DnsQueryRepository(db)
        logger.info("Bulk creating DNS queries", extra={"count": len(queries)})
        count = repository.bulk_create(queries)
        logger.info("Bulk DNS queries created", extra={"inserted": count})
        return {"inserted": count}

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
        repository = DnsQueryRepository(db)
        items, total = repository.get_all(
            page=page,
            page_size=page_size,
            domain_search=domain_search,
            client_ip=client_ip,
            blocked_only=blocked_only,
            start_date=start_date,
            end_date=end_date
        )
        client_ips = list({item.client_ip for item in items})
        device_map = DeviceRepository(db).get_hostname_map_by_client_ips(client_ips)
        logger.info("Fetched DNS queries", extra={"count": len(items), "total": total, "page": page})
        return {
            "items": [
                DnsQueryResponse.model_validate(item).model_copy(
                    update={"device_name": device_map.get(item.client_ip)}
                )
                for item in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }

    def get_stats(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        repository = DnsQueryRepository(db)
        logger.info("Fetching DNS stats")
        return repository.get_stats(start_date=start_date, end_date=end_date)

    def get_unique_clients(self, db: Session) -> List[str]:
        repository = DnsQueryRepository(db)
        logger.info("Fetching unique clients")
        return repository.get_unique_clients()

    def cleanup_old_records(self, db: Session, days: int = 30) -> dict:
        repository = DnsQueryRepository(db)
        logger.info("Cleaning up old DNS records", extra={"days": days})
        count = repository.delete_old_records(days=days)
        logger.info("Old DNS records deleted", extra={"deleted": count})
        return {"deleted": count}

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
        repository = DnsQueryRepository(db)
        logger.info("Fetching grouped sites")
        return repository.get_grouped_by_site(
            start_date=start_date,
            end_date=end_date,
            client_ip=client_ip,
            blocked_only=blocked_only,
            filter_noise=filter_noise,
            limit=limit
        )
