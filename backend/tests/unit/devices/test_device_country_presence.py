from app.features.devices.models.device import Device
from app.features.devices.repositories.device_country_presence_repository import (
    DeviceCountryPresenceRepository,
)
from app.features.vpn.models.ip_lease import IpLease
from app.features.vpn.models.ip_pool import IpPool
from app.features.vpn.models.vpn_peer import VpnPeer


def _create_device(db_session, *, ip: str = "10.0.0.5") -> Device:
    pool = IpPool(
        name="pool-test",
        cidr="10.0.0.0/24",
        gateway_ip="10.0.0.1",
        dns_ip="10.0.0.1",
        endpoint="vpn:51820",
        server_public_key="key-test",
    )
    db_session.add(pool)
    db_session.flush()
    peer = VpnPeer(device_id="dev-country", public_key="pubkey-country", pool_id=pool.id)
    db_session.add(peer)
    db_session.flush()
    lease = IpLease(pool_id=pool.id, peer_id=peer.id, ip=ip)
    db_session.add(lease)
    db_session.flush()
    device = Device(ip_lease_id=lease.id, source="manual")
    db_session.add(device)
    db_session.commit()
    return device


def test_record_batch_returns_new_countries(db_session):
    device = _create_device(db_session)
    repo = DeviceCountryPresenceRepository(db_session)

    new = repo.record_batch(device.id, {"IL": 5, "GLOBAL": 10})
    db_session.commit()

    assert "IL" in new
    assert "GLOBAL" not in new

    again = repo.record_batch(device.id, {"IL": 1, "DE": 2})
    db_session.commit()

    assert again == ["DE"]
    assert "IL" in repo.known_codes(device.id)
