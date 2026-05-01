from __future__ import annotations

import ipaddress
from dataclasses import dataclass

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.features.vpn.models.ip_pool import IpPool
from app.features.vpn.models.ip_lease import IpLease
from app.features.vpn.models.vpn_peer import VpnPeer
from app.features.vpn.repositories.ip_lease_repository import IpLeaseRepository


@dataclass(frozen=True)
class AllocatedLease:
    ip: str


class IpAllocationService:
    """
    Allocate a single IPv4 address from a pool, transactionally.

    Concurrency strategy:
    - compute a candidate list
    - try INSERT with unique constraint (pool_id, ip) and (peer_id)
    - on IntegrityError, retry next candidate
    """

    def __init__(self, db: Session):
        self.db = db
        self.leases = IpLeaseRepository(db)

    def _iter_pool_hosts(self, pool: IpPool):
        net = ipaddress.ip_network(pool.cidr, strict=False)
        if not isinstance(net, ipaddress.IPv4Network):
            raise ValueError("Only IPv4 pools are supported right now")

        # Reserve:
        # - network address (.0) and broadcast (.255) are excluded by hosts()
        # - gateway_ip, dns_ip should not be leased
        reserved = {pool.gateway_ip.strip(), pool.dns_ip.strip()}
        for ip in net.hosts():
            s = str(ip)
            if s in reserved:
                continue
            yield s

    def ensure_peer_lease(self, peer: VpnPeer, pool: IpPool) -> AllocatedLease:
        existing = self.leases.get_active_by_peer_id(peer.id)
        if existing:
            return AllocatedLease(ip=existing.ip)

        # Best effort: start with current used set to skip obvious conflicts.
        used = self.leases.list_active_ips_by_pool_id(pool.id)

        for candidate in self._iter_pool_hosts(pool):
            if candidate in used:
                continue
            try:
                # Use a savepoint so a failed insert doesn't roll back unrelated ORM work
                # (e.g., newly created IpPool / VpnPeer rows in the same transaction).
                with self.db.begin_nested():
                    lease = IpLease(pool_id=pool.id, peer_id=peer.id, ip=candidate)
                    self.leases.create(lease)
                return AllocatedLease(ip=candidate)
            except IntegrityError:
                continue

        raise RuntimeError("No available IPs in pool")

