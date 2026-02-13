import asyncio
import logging
from sqlalchemy.orm import Session
from typing import Optional, List
from datetime import datetime
from app.features.dns_queries.services.dns_query_service import DnsQueryService
from app.features.dns_queries.repositories.dns_query_repository import DnsQueryRepository
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate, DnsQueryBulkCreate
from app.shared.websocket_manager import ws_manager

logger = logging.getLogger(__name__)


def get_service(db: Session) -> DnsQueryService:
    repository = DnsQueryRepository(db)
    return DnsQueryService(repository)


def create_dns_query_controller(dns_query_data: DnsQueryCreate, db: Session):
    service = get_service(db)
    result = service.create_query(dns_query_data)
    # Broadcast to WebSocket clients
    _broadcast_queries([dns_query_data])
    return result


def bulk_create_dns_queries_controller(bulk_data: DnsQueryBulkCreate, db: Session):
    service = get_service(db)
    result = service.bulk_create_queries(bulk_data.queries)
    # Broadcast to WebSocket clients
    _broadcast_queries(bulk_data.queries)
    return result


def _broadcast_queries(queries: List[DnsQueryCreate]):
    """Broadcast new DNS queries to all connected WebSocket clients."""
    if ws_manager.connection_count == 0:
        return  # No clients connected, skip

    data = {
        "type": "dns_queries",
        "queries": [
            {
                "timestamp": q.timestamp.isoformat(),
                "client_ip": q.client_ip,
                "domain": q.domain,
                "query_type": q.query_type,
                "action": q.action,
                "blocked": q.blocked,
            }
            for q in queries
        ]
    }

    try:
        loop = asyncio.get_event_loop()
        if loop.is_running():
            asyncio.ensure_future(ws_manager.broadcast(data))
        else:
            loop.run_until_complete(ws_manager.broadcast(data))
    except RuntimeError:
        # If no event loop exists, create one
        asyncio.run(ws_manager.broadcast(data))
    except Exception as e:
        logger.warning(f"Failed to broadcast DNS queries via WebSocket: {e}")


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


def get_grouped_sites_controller(
    db: Session,
    start_date: Optional[datetime] = None,
    end_date: Optional[datetime] = None,
    client_ip: Optional[str] = None,
    blocked_only: bool = False,
    filter_noise: bool = True,
    limit: int = 50
):
    service = get_service(db)
    return service.get_grouped_by_site(
        start_date=start_date,
        end_date=end_date,
        client_ip=client_ip,
        blocked_only=blocked_only,
        filter_noise=filter_noise,
        limit=limit
    )
