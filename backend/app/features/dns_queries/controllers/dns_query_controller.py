from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.features.dns_queries.services.dns_query_service import DnsQueryService
from app.features.dns_queries.repositories.dns_query_repository import DnsQueryRepository
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate, DnsQueryBulkCreate


def get_service(db: Session) -> DnsQueryService:
    repository = DnsQueryRepository(db)
    return DnsQueryService(repository)


def create_dns_query_controller(dns_query_data: DnsQueryCreate, db: Session):
    service = get_service(db)
    return service.create_query(dns_query_data)


def bulk_create_dns_queries_controller(bulk_data: DnsQueryBulkCreate, db: Session):
    service = get_service(db)
    return service.bulk_create_queries(bulk_data.queries)


def get_dns_queries_controller(
    db: Session,
    page: int = 1,
    page_size: int = 50,
    domain_search: Optional[str] = None,
    client_ip: Optional[str] = None,
    blocked_only: bool = False,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    service = get_service(db)
    return service.get_queries(
        page=page,
        page_size=page_size,
        domain_search=domain_search,
        client_ip=client_ip,
        blocked_only=blocked_only,
        start_date=start_date,
        end_date=end_date
    )


def get_dns_stats_controller(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None
):
    service = get_service(db)
    return service.get_stats(start_date=start_date, end_date=end_date)


def get_unique_clients_controller(db: Session):
    service = get_service(db)
    return service.get_unique_clients()


def cleanup_old_records_controller(db: Session, days: int = 30):
    service = get_service(db)
    return service.cleanup_old_records(days=days)
