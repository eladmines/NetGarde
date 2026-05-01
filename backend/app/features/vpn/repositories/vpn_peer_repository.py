from __future__ import annotations

from sqlalchemy.orm import Session

from app.features.vpn.models.vpn_peer import VpnPeer


class VpnPeerRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_by_device_id(self, device_id: str) -> VpnPeer | None:
        return self.db.query(VpnPeer).filter(VpnPeer.device_id == device_id).first()

    def get_by_public_key(self, public_key: str) -> VpnPeer | None:
        return self.db.query(VpnPeer).filter(VpnPeer.public_key == public_key).first()

    def create(self, peer: VpnPeer) -> VpnPeer:
        self.db.add(peer)
        self.db.flush()
        self.db.refresh(peer)
        return peer

