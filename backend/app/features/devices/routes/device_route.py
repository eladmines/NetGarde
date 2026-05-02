from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session

from app.features.devices.schemas.device import DeviceCreate, DeviceUpdate, DhcpSyncRequest
from app.features.devices.controllers.device_controller import (
    create_device_controller,
    get_devices_controller,
    update_device_controller,
    delete_device_controller,
    sync_dhcp_leases_controller,
)
from app.features.devices.dependencies import get_device_service
from app.features.devices.services.device_service_interface import IDeviceService
from app.shared.dependencies import get_db

router = APIRouter(prefix="/devices", tags=["Devices"])


@router.post("")
def create_device_endpoint(
    data: DeviceCreate,
    db: Session = Depends(get_db),
    service: IDeviceService = Depends(get_device_service),
):
    return create_device_controller(data, db, service)


@router.get("")
def get_devices_endpoint(
    db: Session = Depends(get_db),
    service: IDeviceService = Depends(get_device_service),
):
    return get_devices_controller(db, service)


@router.put("/{device_id}")
def update_device_endpoint(
    device_id: int,
    data: DeviceUpdate,
    db: Session = Depends(get_db),
    service: IDeviceService = Depends(get_device_service),
):
    return update_device_controller(device_id, data, db, service)


@router.delete("/{device_id}")
def delete_device_endpoint(
    device_id: int,
    db: Session = Depends(get_db),
    service: IDeviceService = Depends(get_device_service),
):
    return delete_device_controller(device_id, db, service)


@router.post("/sync-dhcp")
def sync_dhcp_endpoint(
    payload: DhcpSyncRequest,
    db: Session = Depends(get_db),
    service: IDeviceService = Depends(get_device_service),
):
    """Bulk upsert devices from router DHCP lease records."""
    return sync_dhcp_leases_controller(payload, db, service)
