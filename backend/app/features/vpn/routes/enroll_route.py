import logging

from fastapi import APIRouter, Depends, HTTPException, Request
from sqlalchemy.orm import Session

from app.features.vpn.schemas.enroll import EnrollRequest, EnrollResponse
from app.features.vpn.services.enroll_service import EnrollService
from app.shared.dependencies import get_db
from app.shared.device_auth import verify_enroll_bootstrap
from app.shared.request_client_ip import client_ip_from_request

logger = logging.getLogger(__name__)

router = APIRouter(prefix="/v1", tags=["VPN"])


@router.post("/enroll", response_model=EnrollResponse)
def enroll_endpoint(
    request: Request,
    payload: EnrollRequest,
    db: Session = Depends(get_db),
    _: None = Depends(verify_enroll_bootstrap),
):
    service = EnrollService(db)
    try:
        return service.enroll(
            payload,
            connect_ip=client_ip_from_request(request),
        )
    except ValueError as e:
        logger.warning("Enroll rejected: %s", e)
        raise HTTPException(status_code=409, detail=str(e)) from e
    except RuntimeError as e:
        # Common misconfig: VPN_ENDPOINT / VPN_SERVER_PUBLIC_KEY not set.
        logger.exception("Enroll failed due to server configuration")
        raise HTTPException(status_code=500, detail=str(e)) from e
    except Exception as e:
        logger.exception("Unexpected enroll error")
        raise HTTPException(status_code=500, detail="Enroll failed") from e

