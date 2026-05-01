from __future__ import annotations

from sqlalchemy.orm import Session

from app.features.vpn.models.ip_pool import IpPool
from app.features.vpn.models.vpn_peer import VpnPeer
from app.features.vpn.repositories.ip_pool_repository import IpPoolRepository
from app.features.vpn.repositories.vpn_peer_repository import VpnPeerRepository
from app.features.vpn.services.ip_allocation_service import IpAllocationService
from app.features.vpn.services.wireguard_agent_client import apply_peer_on_host
from app.shared.config import settings


class EnrollService:
    def __init__(self, db: Session):
        self.db = db
        self.pools = IpPoolRepository(db)
        self.peers = VpnPeerRepository(db)
        self.alloc = IpAllocationService(db)

    def _get_or_create_default_pool(self) -> IpPool:
        name = settings.VPN_POOL_NAME
        pool = self.pools.get_active_by_name(name)
        if pool:
            return pool

        if not settings.VPN_ENDPOINT or not settings.VPN_SERVER_PUBLIC_KEY:
            raise RuntimeError("VPN_ENDPOINT and VPN_SERVER_PUBLIC_KEY must be set")

        pool = IpPool(
            name=name,
            cidr=settings.VPN_POOL_CIDR,
            gateway_ip=settings.VPN_GATEWAY_IP,
            dns_ip=settings.VPN_DNS_IP,
            mtu=settings.VPN_MTU,
            allowed_ips=settings.VPN_ALLOWED_IPS,
            endpoint=settings.VPN_ENDPOINT,
            server_public_key=settings.VPN_SERVER_PUBLIC_KEY,
            persistent_keepalive=settings.VPN_PERSISTENT_KEEPALIVE,
            is_active=True,
        )
        return self.pools.create(pool)

    def enroll(self, device_id: str, public_key: str) -> dict:
        device_id = device_id.strip()
        public_key = public_key.strip()

        pool = self._get_or_create_default_pool()

        peer = self.peers.get_by_device_id(device_id) or self.peers.get_by_public_key(public_key)
        if not peer:
            peer = self.peers.create(VpnPeer(device_id=device_id, public_key=public_key, pool_id=pool.id))

        lease = self.alloc.ensure_peer_lease(peer, pool)

        # Persist allocation before touching host WireGuard state.
        self.db.commit()

        # Apply (or refresh) the live WireGuard peer on the EC2 host.
        apply_peer_on_host(public_key=peer.public_key, allowed_ip=lease.ip)

        allowed_ips = [s.strip() for s in (pool.allowed_ips or "").split(",") if s.strip()]
        if not allowed_ips:
            allowed_ips = ["0.0.0.0/0", "::/0"]

        return {
            "address": f"{lease.ip}/32",
            "dns": [pool.dns_ip],
            "mtu": pool.mtu or settings.VPN_MTU,
            "server_public_key": pool.server_public_key,
            "endpoint": pool.endpoint,
            "allowed_ips": allowed_ips,
            "persistent_keepalive": pool.persistent_keepalive,
        }

