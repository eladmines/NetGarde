from typing import Protocol, List
from app.features.devices.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceRead,
    DhcpSyncRequest,
    DhcpSyncResult,
)
from sqlalchemy.orm import Session


class IDeviceService(Protocol):
    def create_device(self, data: DeviceCreate, db: Session) -> DeviceRead:
        ...

    def get_devices(self, db: Session, active_only: bool = False) -> List[DeviceRead]:
        ...

    def update_device(self, device_id: int, data: DeviceUpdate, db: Session) -> DeviceRead:
        ...

    def delete_device(self, device_id: int, db: Session) -> dict:
        ...

    def sync_from_dhcp_leases(self, payload: DhcpSyncRequest, db: Session) -> DhcpSyncResult:
        ...
