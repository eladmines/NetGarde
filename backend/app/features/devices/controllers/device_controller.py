from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.features.devices.schemas.device import DeviceCreate, DeviceUpdate, DhcpSyncRequest
from app.features.devices.services.device_service_interface import IDeviceService
from app.features.devices.errors.device import DeviceAlreadyExistsError, DeviceNotFoundError
from app.features.users.errors.user import UserNotFoundError
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


def create_device_controller(data: DeviceCreate, db: Session, service: IDeviceService):
    try:
        return service.create_device(data, db)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DeviceAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error("POST /devices - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


def get_devices_controller(db: Session, service: IDeviceService, active_only: bool = False):
    try:
        return service.get_devices(db, active_only=active_only)
    except Exception:
        logger.error("GET /devices - error", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch devices")


def update_device_controller(device_id: int, data: DeviceUpdate, db: Session, service: IDeviceService):
    try:
        return service.update_device(device_id, data, db)
    except UserNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DeviceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except DeviceAlreadyExistsError as e:
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error("PUT /devices/{device_id} - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


def delete_device_controller(device_id: int, db: Session, service: IDeviceService):
    try:
        return service.delete_device(device_id, db)
    except DeviceNotFoundError as e:
        raise HTTPException(status_code=404, detail=str(e))
    except Exception:
        logger.error("DELETE /devices/{device_id} - error", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete device")


def sync_dhcp_leases_controller(payload: DhcpSyncRequest, db: Session, service: IDeviceService):
    try:
        return service.sync_from_dhcp_leases(payload, db)
    except Exception as e:
        logger.error("POST /devices/sync-dhcp - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))
