from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from sqlalchemy.orm import Session

from app.features.devices.models.device import Device
from app.features.vpn.models.ip_lease import IpLease
from app.features.vpn.models.ip_pool import IpPool
from app.features.vpn.models.vpn_peer import VpnPeer
from app.features.vpn.repositories.ip_pool_repository import IpPoolRepository
from app.features.vpn.schemas.topology import VpnPeerNodeRead, VpnServerRead, VpnTopologyRead
from app.features.vpn.services.wireguard_agent_client import list_peers_on_host
from app.shared.config import settings
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)

HANDSHAKE_CONNECTED_SEC = 180


def _handshake_status(latest_handshake: int) -> str:
    if latest_handshake <= 0:
        return "never"
    age = datetime.now(timezone.utc).timestamp() - latest_handshake
    if age <= HANDSHAKE_CONNECTED_SEC:
        return "connected"
    return "idle"


def _wg_peer_map() -> Dict[str, dict]:
    try:
        rows = list_peers_on_host()
    except Exception as exc:
        logger.warning("WireGuard agent peer list unavailable: %s", exc)
        return {}
    return {row["public_key"]: row for row in rows}


class VpnTopologyService:
    def __init__(self, db: Session):
        self.db = db
        self.pools = IpPoolRepository(db)

    def _resolve_pool(self) -> Optional[IpPool]:
        pool = self.pools.get_active_by_name(settings.VPN_POOL_NAME)
        if pool:
            return pool
        if not settings.VPN_ENDPOINT or not settings.VPN_SERVER_PUBLIC_KEY:
            return None
        return IpPool(
            name=settings.VPN_POOL_NAME,
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

    def get_topology(self) -> VpnTopologyRead:
        pool = self._resolve_pool()
        if pool is None:
            raise RuntimeError("VPN pool is not configured")

        allowed = [s.strip() for s in (pool.allowed_ips or "").split(",") if s.strip()]
        if not allowed:
            allowed = ["0.0.0.0/0", "::/0"]

        server = VpnServerRead(
            endpoint=pool.endpoint,
            gateway_ip=pool.gateway_ip,
            dns_ip=pool.dns_ip,
            cidr=pool.cidr,
            server_public_key=pool.server_public_key,
            allowed_ips=allowed,
            mtu=pool.mtu,
        )

        wg_by_key = _wg_peer_map()
        q = (
            self.db.query(VpnPeer, IpLease, Device)
            .join(
                IpLease,
                (IpLease.peer_id == VpnPeer.id) & (IpLease.released_at.is_(None)),
            )
            .outerjoin(Device, Device.ip_lease_id == IpLease.id)
        )
        if pool.id is not None:
            q = q.filter(VpnPeer.pool_id == pool.id)
        rows = q.order_by(IpLease.ip.asc()).all()

        peers: List[VpnPeerNodeRead] = []
        for peer, lease, device in rows:
            wg = wg_by_key.get(peer.public_key, {})
            latest = int(wg.get("latest_handshake") or 0)
            hs_at = (
                datetime.fromtimestamp(latest, tz=timezone.utc)
                if latest > 0
                else None
            )
            status = _handshake_status(latest) if wg else "unknown"
            if wg and latest <= 0:
                status = "never"

            peers.append(
                VpnPeerNodeRead(
                    peer_id=peer.id,
                    vpn_device_id=peer.device_id,
                    device_id=device.id if device else None,
                    hostname=device.hostname if device else None,
                    client_ip=lease.ip,
                    public_key=peer.public_key,
                    handshake_status=status,
                    latest_handshake_at=hs_at,
                    endpoint=wg.get("endpoint"),
                    rx_bytes=wg.get("rx_bytes"),
                    tx_bytes=wg.get("tx_bytes"),
                    on_wireguard=bool(wg),
                )
            )

        return VpnTopologyRead(server=server, peers=peers)
