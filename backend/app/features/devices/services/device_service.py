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
from app.shared.logging_context import structured_extra
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class DeviceService:
    """Implementation of IDeviceService."""

    @staticmethod
    def _to_read(device) -> DeviceRead:
        lease = device.ip_lease
        return DeviceRead(
            id=device.id,
            ip_lease_id=device.ip_lease_id,
            client_ip=lease.ip if lease is not None else "",
            hostname=device.hostname,
            mac_address=device.mac_address,
            source=device.source,
            created_at=device.created_at,
            updated_at=device.updated_at,
        )

    def create_device(self, data: DeviceCreate, db: Session) -> DeviceRead:
        repository = DeviceRepository(db)
        try:
            device = repository.create(data)
            return self._to_read(device)
        except IntegrityError as exc:
            logger.warning(
                "Device already exists",
                extra=structured_extra("device_already_exists", ip_lease_id=data.ip_lease_id),
            )
            raise DeviceAlreadyExistsError(str(data.ip_lease_id)) from exc

    def get_devices(self, db: Session) -> List[DeviceRead]:
        repository = DeviceRepository(db)
        devices = repository.get_all()
        return [self._to_read(device) for device in devices]

    def update_device(self, device_id: int, data: DeviceUpdate, db: Session) -> DeviceRead:
        repository = DeviceRepository(db)
        try:
            device = repository.update(device_id, data)
            if not device:
                raise DeviceNotFoundError(str(device_id))
            return self._to_read(device)
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
        skipped = 0

        for lease in payload.leases:
            result = repository.upsert_from_dhcp_lease(lease)
            if result == "created":
                created += 1
            elif result == "updated":
                updated += 1
            else:
                skipped += 1

        logger.info(
            "DHCP device sync completed",
            extra=structured_extra(
                "dhcp_sync_completed",
                processed=len(payload.leases),
                created=created,
                updated=updated,
                skipped=skipped,
            ),
        )
        return DhcpSyncResult(
            processed=len(payload.leases),
            created=created,
            updated=updated,
            skipped=skipped,
        )
