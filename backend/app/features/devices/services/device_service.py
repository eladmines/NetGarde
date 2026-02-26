from typing import List
from sqlalchemy.orm import Session
from sqlalchemy.exc import IntegrityError, SQLAlchemyError

from app.features.devices.repositories.device_repository import DeviceRepository
from app.features.devices.schemas.device import (
    DeviceCreate,
    DeviceUpdate,
    DeviceRead,
    DhcpSyncRequest,
    DhcpSyncResult,
)
from app.features.devices.errors.device import DeviceAlreadyExistsError, DeviceNotFoundError
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class DeviceService:
    """Implementation of IDeviceService."""

    def create_device(self, data: DeviceCreate, db: Session) -> DeviceRead:
        repository = DeviceRepository(db)
        try:
            logger.info("Creating device", extra={"client_ip": data.client_ip})
            device = repository.create(data)
            return DeviceRead.model_validate(device)
        except IntegrityError as exc:
            logger.warning("Device already exists", extra={"client_ip": data.client_ip})
            raise DeviceAlreadyExistsError(data.client_ip) from exc

    def get_devices(self, db: Session, active_only: bool = False) -> List[DeviceRead]:
        repository = DeviceRepository(db)
        devices = repository.get_all(active_only=active_only)
        return [DeviceRead.model_validate(device) for device in devices]

    def update_device(self, device_id: int, data: DeviceUpdate, db: Session) -> DeviceRead:
        repository = DeviceRepository(db)
        try:
            device = repository.update(device_id, data)
            if not device:
                raise DeviceNotFoundError(str(device_id))
            return DeviceRead.model_validate(device)
        except IntegrityError as exc:
            raise DeviceAlreadyExistsError(str(device_id)) from exc

    def delete_device(self, device_id: int, db: Session) -> dict:
        repository = DeviceRepository(db)
        deleted = repository.delete(device_id)
        if not deleted:
            raise DeviceNotFoundError(str(device_id))
        return {"message": "Device deleted successfully", "device_id": device_id}

    def sync_from_dhcp_leases(self, payload: DhcpSyncRequest, db: Session) -> DhcpSyncResult:
        repository = DeviceRepository(db)
        created = 0
        updated = 0

        for lease in payload.leases:
            result = repository.upsert_from_dhcp_lease(lease)
            if result == "created":
                created += 1
            else:
                updated += 1

        logger.info(
            "DHCP device sync completed",
            extra={"processed": len(payload.leases), "created": created, "updated": updated},
        )
        return DhcpSyncResult(processed=len(payload.leases), created=created, updated=updated)
