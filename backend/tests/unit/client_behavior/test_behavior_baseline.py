from datetime import datetime, timedelta, timezone

from app.features.client_behavior.models.client_behavior_rollup import ClientBehaviorRollup
from app.features.client_behavior.services.behavior_baseline_service import BehaviorBaselineService
from app.features.devices.models.device import Device
from app.features.vpn.models.ip_lease import IpLease
from app.features.vpn.models.ip_pool import IpPool
from app.features.vpn.models.vpn_peer import VpnPeer


def _seed_rollups(db_session, device_id: int, hours: int, queries_per_hour: int = 10):
    now = datetime.now(timezone.utc)
    for i in range(hours):
        window = (now - timedelta(hours=hours - i)).replace(minute=0, second=0, microsecond=0)
        db_session.add(
            ClientBehaviorRollup(
                device_id=device_id,
                window_start=window,
                query_count=queries_per_hour,
                unique_roots=5,
                new_roots=1,
                hour_utc=window.hour,
            )
        )
    db_session.commit()


def _create_device(db_session, *, pool_name: str, ip: str, mac: str) -> Device:
    pool = IpPool(
        name=pool_name,
        cidr="10.0.0.0/24",
        gateway_ip="10.0.0.1",
        dns_ip="10.0.0.1",
        endpoint="vpn.example:51820",
        server_public_key=f"key-{pool_name}",
    )
    db_session.add(pool)
    db_session.flush()
    peer = VpnPeer(
        device_id=f"dev-{pool_name}",
        public_key=f"pubkey-{pool_name}",
        pool_id=pool.id,
    )
    db_session.add(peer)
    db_session.flush()
    lease = IpLease(pool_id=pool.id, peer_id=peer.id, ip=ip)
    db_session.add(lease)
    db_session.flush()
    device = Device(ip_lease_id=lease.id, mac_address=mac, source="manual")
    db_session.add(device)
    db_session.commit()
    return device


def test_baseline_not_ready_with_few_rollups(db_session):
    device = _create_device(
        db_session,
        pool_name="default",
        ip="10.0.0.5",
        mac="aa:bb:cc:dd:ee:01",
    )

    _seed_rollups(db_session, device.id, hours=10, queries_per_hour=5)
    ready = BehaviorBaselineService(db_session).recompute_device(device.id)
    assert ready is False


def test_baseline_ready_with_enough_data(db_session):
    device = _create_device(
        db_session,
        pool_name="default2",
        ip="10.0.1.5",
        mac="aa:bb:cc:dd:ee:02",
    )

    _seed_rollups(db_session, device.id, hours=80, queries_per_hour=10)
    ready = BehaviorBaselineService(db_session).recompute_device(device.id)
    assert ready is True
