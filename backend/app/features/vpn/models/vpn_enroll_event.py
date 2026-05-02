from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, Index
from sqlalchemy.orm import relationship

from app.shared.database import Base


class VpnEnrollEvent(Base):
    __tablename__ = "vpn_enroll_events"

    id = Column(Integer, primary_key=True, index=True)
    peer_id = Column(Integer, ForeignKey("vpn_peers.id", ondelete="CASCADE"), nullable=False, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="SET NULL"), nullable=True, index=True)

    event_type = Column(String(32), nullable=False, default="enroll")

    # Snapshots at the moment of enroll (useful even if devices table later changes)
    lease_ip = Column(String(45), nullable=False)
    hostname = Column(String(255), nullable=True)
    mac_address = Column(String(17), nullable=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), nullable=False, index=True)

    peer = relationship("VpnPeer")
    device = relationship("Device")

    __table_args__ = (
        Index("ix_vpn_enroll_events_peer_created_at", "peer_id", "created_at"),
        Index("ix_vpn_enroll_events_device_created_at", "device_id", "created_at"),
    )

