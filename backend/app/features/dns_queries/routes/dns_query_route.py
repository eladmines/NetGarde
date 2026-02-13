from fastapi import APIRouter, Depends, Query, WebSocket, WebSocketDisconnect
from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
import logging
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
from app.shared.websocket_manager import ws_manager

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/dns-queries", tags=["DNS Queries"])


@router.post("")
def create_dns_query_endpoint(
    dns_query_data: DnsQueryCreate,
    db: Session = Depends(get_db)
):
    """Create a single DNS query log entry."""
    return create_dns_query_controller(dns_query_data, db)


@router.post("/bulk")
def bulk_create_dns_queries_endpoint(
    bulk_data: DnsQueryBulkCreate,
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
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
    db: Session = Depends(get_db)
):
    """Get DNS query statistics (total, blocked, top domains, top clients)."""
    return get_dns_stats_controller(db=db, start_date=start_date, end_date=end_date)


@router.get("/clients")
def get_unique_clients_endpoint(db: Session = Depends(get_db)):
    """Get list of unique client IPs that have made DNS queries."""
    return get_unique_clients_controller(db)


@router.delete("/cleanup")
def cleanup_old_records_endpoint(
    days: int = Query(default=30, ge=1, description="Delete records older than this many days"),
    db: Session = Depends(get_db)
):
    """Delete DNS query records older than specified days."""
    return cleanup_old_records_controller(db, days=days)


@router.websocket("/ws")
async def dns_queries_websocket(websocket: WebSocket):
    """
    WebSocket endpoint for real-time DNS query streaming.
    Clients connect here to receive live DNS queries as they are logged.
    """
    await ws_manager.connect(websocket)
    try:
        while True:
            # Keep the connection alive by waiting for any client message
            # (clients can send ping/pong or just keep the connection open)
            await websocket.receive_text()
    except WebSocketDisconnect:
        ws_manager.disconnect(websocket)
        logger.info("WebSocket client disconnected normally")
    except Exception as e:
        ws_manager.disconnect(websocket)
        logger.warning(f"WebSocket connection error: {e}")
