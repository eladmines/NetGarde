import pytest

from app.features.devices.errors.device import DeviceAlreadyExistsError, DeviceNotFoundError
from app.features.devices.schemas.device import DeviceCreate, DeviceUpdate
from app.features.devices.services.device_service import DeviceService
from tests.helpers.factories import create_ip_lease, create_vpn_device


def test_create_device(db_session):
    lease = create_ip_lease(db_session, ip="10.0.0.30")
    svc = DeviceService()
    created = svc.create_device(
        DeviceCreate(ip_lease_id=lease.id, hostname="new-host", source="manual"),
        db_session,
    )
    assert created.client_ip == "10.0.0.30"
    assert created.hostname == "new-host"


def test_create_device_duplicate_lease(db_session):
    _device, lease = create_vpn_device(db_session, ip="10.0.0.31")
    svc = DeviceService()
    with pytest.raises(DeviceAlreadyExistsError):
        svc.create_device(
            DeviceCreate(ip_lease_id=lease.id, hostname="dup"),
            db_session,
        )


def test_get_devices(db_session):
    create_vpn_device(db_session, ip="10.0.0.32", hostname="listed")
    svc = DeviceService()
    devices = svc.get_devices(db_session)
    assert len(devices) == 1
    assert devices[0].hostname == "listed"


def test_update_device(db_session):
    device, _ = create_vpn_device(db_session, ip="10.0.0.33")
    svc = DeviceService()
    updated = svc.update_device(device.id, DeviceUpdate(hostname="renamed"), db_session)
    assert updated.hostname == "renamed"


def test_update_device_not_found(db_session):
    svc = DeviceService()
    with pytest.raises(DeviceNotFoundError):
        svc.update_device(999, DeviceUpdate(hostname="missing"), db_session)


def test_delete_device(db_session):
    device, _ = create_vpn_device(db_session, ip="10.0.0.34")
    svc = DeviceService()
    result = svc.delete_device(device.id, db_session)
    assert result["device_id"] == device.id
    assert svc.get_devices(db_session) == []
