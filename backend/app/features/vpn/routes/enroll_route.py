from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.features.vpn.schemas.enroll import EnrollRequest, EnrollResponse
from app.features.vpn.services.enroll_service import EnrollService
from app.shared.dependencies import get_db


router = APIRouter(prefix="/v1", tags=["VPN"])


@router.post("/enroll", response_model=EnrollResponse)
def enroll_endpoint(payload: EnrollRequest, db: Session = Depends(get_db)):
    service = EnrollService(db)
    return service.enroll(payload.device_id, payload.public_key)

