import logging

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session

from app.features.vpn.schemas.usage import UsageReportRequest, UsageReportResponse
from app.features.vpn.services.usage_service import UsageService
from app.shared.dependencies import get_db
from app.shared.device_auth import AuthenticatedDevice, get_authenticated_device

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["VPN"])


@router.post("/usage", response_model=UsageReportResponse)
def usage_report_endpoint(
    payload: UsageReportRequest,
    db: Session = Depends(get_db),
    device: AuthenticatedDevice = Depends(get_authenticated_device),
):
    if payload.device_id.strip() != device.device_id:
        raise HTTPException(status_code=403, detail="device_id does not match authenticated device")
    service = UsageService(db)
    try:
        return service.report_usage(payload)
    except Exception as e:
        logger.exception("Usage report failed")
        raise HTTPException(status_code=500, detail="Usage report failed") from e
