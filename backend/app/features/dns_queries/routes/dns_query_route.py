from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate, DnsQueryBulkCreate
from app.features.dns_queries.controllers.dns_query_controller import (
    create_dns_query_controller,
    bulk_create_dns_queries_controller,
    get_dns_queries_controller,
    get_dns_stats_controller,
    get_unique_clients_controller,
    cleanup_old_records_controller
)
from app.shared.dependencies import get_db
from app.shared.service_auth import verify_dns_ingest_service
from app.shared.admin_auth import verify_admin_api_token

router = APIRouter(prefix="/dns-queries", tags=["DNS Queries"])


@router.post("")
def create_dns_query_endpoint(
    dns_query_data: DnsQueryCreate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_dns_ingest_service),
):
    """Create a single DNS query log entry."""
    return create_dns_query_controller(dns_query_data, db)


@router.post("/bulk")
def bulk_create_dns_queries_endpoint(
    bulk_data: DnsQueryBulkCreate,
    db: Session = Depends(get_db),
    _: None = Depends(verify_dns_ingest_service),
):
    """Create multiple DNS query log entries at once."""
    return bulk_create_dns_queries_controller(bulk_data, db)


@router.get("")
def get_dns_queries_endpoint(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=50, ge=1, le=100, description="Number of items per page"),
    domain_search: Optional[str] = Query(default=None, description="Search by domain (partial match)"),
    client_ip: Optional[str] = Query(default=None, description="Filter by client IP"),
    blocked_only: bool = Query(default=False, description="Show only blocked queries"),
    start_date: Optional[datetime] = Query(default=None, description="Filter from date (ISO format)"),
    end_date: Optional[datetime] = Query(default=None, description="Filter to date (ISO format)"),
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
):
    """Get paginated DNS query logs with optional filters."""
    return get_dns_queries_controller(
        db=db,
        page=page,
        page_size=page_size,
        domain_search=domain_search,
        client_ip=client_ip,
        blocked_only=blocked_only,
        start_date=start_date,
        end_date=end_date
    )


@router.get("/stats")
def get_dns_stats_endpoint(
    start_date: Optional[datetime] = Query(default=None, description="Stats from date (ISO format)"),
    end_date: Optional[datetime] = Query(default=None, description="Stats to date (ISO format)"),
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
):
    """Get DNS query statistics (total, blocked, top domains, top clients)."""
    return get_dns_stats_controller(db=db, start_date=start_date, end_date=end_date)


@router.get("/clients")
def get_unique_clients_endpoint(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
):
    """Get list of unique client IPs that have made DNS queries."""
    return get_unique_clients_controller(db)


@router.delete("/cleanup")
def cleanup_old_records_endpoint(
    days: int = Query(default=30, ge=1, description="Delete records older than this many days"),
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
):
    """Delete DNS query records older than specified days."""
    return cleanup_old_records_controller(db, days=days)
