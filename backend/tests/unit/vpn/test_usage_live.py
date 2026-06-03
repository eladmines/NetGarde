from datetime import datetime, timedelta, timezone

from app.features.devices.models.device import Device
from app.features.vpn.models.device_usage_sample import DeviceUsageSample
from app.features.vpn.models.ip_lease import IpLease
from app.features.vpn.models.ip_pool import IpPool
from app.features.vpn.models.vpn_peer import VpnPeer
from app.features.vpn.services.usage_service import UsageService


def _seed_pool_peer_lease_device(db_session):
    pool = IpPool(
        name="test",
        cidr="10.0.0.0/24",
        gateway_ip="10.0.0.1",
        dns_ip="10.0.0.1",
        endpoint="127.0.0.1:51820",
        server_public_key="server-pk",
    )
    db_session.add(pool)
    db_session.flush()
    peer = VpnPeer(device_id="dev-abc", public_key="pk", pool_id=pool.id)
    db_session.add(peer)
    db_session.flush()
    lease = IpLease(pool_id=pool.id, peer_id=peer.id, ip="10.0.0.2")
    db_session.add(lease)
    db_session.flush()
    device = Device(ip_lease_id=lease.id, source="vpn_enroll")
    db_session.add(device)
    db_session.commit()
    return device, peer


def test_list_live_bandwidth_returns_latest_rates(db_session):
    device, peer = _seed_pool_peer_lease_device(db_session)
    now = datetime.now(timezone.utc)
    db_session.add(
        DeviceUsageSample(
            device_external_id=peer.device_id,
            recorded_at=now - timedelta(seconds=30),
            interval_sec=5.0,
            rx_bytes=0,
            tx_bytes=0,
            delta_rx_bytes=5 * 1024 * 1024,
            delta_tx_bytes=1 * 1024 * 1024,
        )
    )
    db_session.add(
        DeviceUsageSample(
            device_external_id=peer.device_id,
            recorded_at=now,
            interval_sec=5.0,
            rx_bytes=10 * 1024 * 1024,
            tx_bytes=2 * 1024 * 1024,
            delta_rx_bytes=10 * 1024 * 1024,
            delta_tx_bytes=2 * 1024 * 1024,
        )
    )
    db_session.commit()

    resp = UsageService(db_session).list_live_bandwidth(max_age_sec=60)
    assert len(resp.items) == 1
    item = resp.items[0]
    assert item.device_id == device.id
    assert item.vpn_device_id == "dev-abc"
    assert item.client_ip == "10.0.0.2"
    assert item.rx_mib_per_sec == 2.0
    assert item.tx_mib_per_sec == 0.4
    assert item.total_mib_per_sec == 2.4
