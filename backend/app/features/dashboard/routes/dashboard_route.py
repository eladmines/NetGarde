from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.features.dashboard.schemas.network_overview import NetworkOverviewRead
from app.features.dashboard.services.network_overview_service import NetworkOverviewService
from app.shared.admin_auth import verify_admin_api_token
from app.shared.dependencies import get_db

router = APIRouter(prefix="/dashboard", tags=["Dashboard"])


def get_network_overview_service(db: Session = Depends(get_db)) -> NetworkOverviewService:
    return NetworkOverviewService(db)


@router.get("/network-overview", response_model=NetworkOverviewRead)
def get_network_overview(
    _: None = Depends(verify_admin_api_token),
    period_minutes: int = Query(60, ge=5, le=1440),
    refresh: bool = Query(False, description="Bypass Redis cache and regenerate review"),
    service: NetworkOverviewService = Depends(get_network_overview_service),
):
    if refresh:
        from app.features.dashboard.services import network_overview_cache

        network_overview_cache.delete_cached_overview(
            max(5, min(period_minutes, 24 * 60))
        )
    return service.build_overview(period_minutes=period_minutes, refresh=refresh)
