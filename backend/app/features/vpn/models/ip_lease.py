from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey, UniqueConstraint, Index
from sqlalchemy.orm import relationship

from app.shared.database import Base


class IpLease(Base):
    __tablename__ = "ip_leases"

    id = Column(Integer, primary_key=True, index=True)
    pool_id = Column(Integer, ForeignKey("ip_pools.id", ondelete="CASCADE"), nullable=False, index=True)
    peer_id = Column(Integer, ForeignKey("vpn_peers.id", ondelete="CASCADE"), nullable=False, index=True)

    ip = Column(String(45), nullable=False)
    leased_at = Column(DateTime(timezone=True), nullable=False, default=lambda: datetime.now(timezone.utc))
    released_at = Column(DateTime(timezone=True), nullable=True)

    pool = relationship("IpPool")
    peer = relationship("VpnPeer", back_populates="leases")

    __table_args__ = (
        UniqueConstraint("pool_id", "ip", name="uq_ip_leases_pool_ip"),
        UniqueConstraint("peer_id", name="uq_ip_leases_peer_id"),
        Index("ix_ip_leases_pool_active", "pool_id", "released_at"),
    )

