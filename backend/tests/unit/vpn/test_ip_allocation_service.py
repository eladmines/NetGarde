import pytest

from app.features.vpn.models.ip_lease import IpLease
from app.features.vpn.models.ip_pool import IpPool
from app.features.vpn.models.vpn_peer import VpnPeer
from app.features.vpn.services.ip_allocation_service import IpAllocationService


def _create_pool_and_peer(db_session):
    pool = IpPool(
        name="alloc-pool",
        cidr="10.0.0.0/29",
        gateway_ip="10.0.0.1",
        dns_ip="10.0.0.2",
        endpoint="vpn:51820",
        server_public_key="key",
        is_active=True,
    )
    db_session.add(pool)
    db_session.flush()

    peer = VpnPeer(device_id="peer-alloc", public_key="pubkey-alloc", pool_id=pool.id)
    db_session.add(peer)
    db_session.commit()
    db_session.refresh(pool)
    db_session.refresh(peer)
    return pool, peer


def test_ensure_peer_lease_allocates_ip(db_session):
    pool, peer = _create_pool_and_peer(db_session)
    svc = IpAllocationService(db_session)
    lease = svc.ensure_peer_lease(peer, pool)
    assert lease.ip.startswith("10.0.0.")
    assert lease.ip not in {pool.gateway_ip, pool.dns_ip}

    row = db_session.query(IpLease).filter(IpLease.peer_id == peer.id).one()
    assert row.ip == lease.ip


def test_ensure_peer_lease_idempotent(db_session):
    pool, peer = _create_pool_and_peer(db_session)
    svc = IpAllocationService(db_session)
    first = svc.ensure_peer_lease(peer, pool)
    second = svc.ensure_peer_lease(peer, pool)
    assert second.ip == first.ip


def test_iter_pool_hosts_skips_gateway_and_dns(db_session):
    pool, peer = _create_pool_and_peer(db_session)
    svc = IpAllocationService(db_session)
    hosts = list(svc._iter_pool_hosts(pool))
    assert pool.gateway_ip not in hosts
    assert pool.dns_ip not in hosts
    assert "10.0.0.3" in hosts
