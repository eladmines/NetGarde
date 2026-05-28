from datetime import datetime
from typing import List, Literal, Optional

from pydantic import BaseModel, ConfigDict


class VpnServerRead(BaseModel):
    interface: str = "wg0"
    endpoint: str
    gateway_ip: str
    dns_ip: str
    cidr: str
    server_public_key: str
    allowed_ips: List[str]
    mtu: Optional[int] = None


class VpnPeerNodeRead(BaseModel):
    peer_id: int
    vpn_device_id: str
    device_id: Optional[int] = None
    hostname: Optional[str] = None
    client_ip: str
    public_key: str
    handshake_status: Literal["connected", "idle", "never", "unknown"] = "unknown"
    latest_handshake_at: Optional[datetime] = None
    endpoint: Optional[str] = None
    rx_bytes: Optional[int] = None
    tx_bytes: Optional[int] = None
    on_wireguard: bool = False

    model_config = ConfigDict(from_attributes=True)


class VpnTopologyRead(BaseModel):
    server: VpnServerRead
    peers: List[VpnPeerNodeRead]
