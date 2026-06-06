from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.features.vpn.schemas.topology import VpnTopologyRead
from app.features.vpn.services.vpn_topology_service import VpnTopologyService
from app.shared.admin_auth import verify_admin_api_token
from app.shared.dependencies import get_db
from app.shared.logging_context import structured_extra
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)

router = APIRouter(prefix="/vpn", tags=["VPN"])


@router.get("/topology", response_model=VpnTopologyRead)
def get_vpn_topology_endpoint(
    db: Session = Depends(get_db),
    _: None = Depends(verify_admin_api_token),
):
    """WireGuard VPN layout: server, pool, enrolled peers, and live handshake state."""
    try:
        return VpnTopologyService(db).get_topology()
    except RuntimeError as e:
        logger.exception(
            "VPN topology unavailable",
            extra=structured_extra("vpn_topology_unavailable"),
        )
        raise HTTPException(status_code=503, detail=str(e)) from e
