from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, ForeignKey
from sqlalchemy.orm import relationship

from app.shared.database import Base


class VpnPeer(Base):
    __tablename__ = "vpn_peers"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(String(64), nullable=False, unique=True, index=True)
    public_key = Column(String(255), nullable=False, unique=True, index=True)

    pool_id = Column(Integer, ForeignKey("ip_pools.id", ondelete="RESTRICT"), nullable=False, index=True)

    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    pool = relationship("IpPool")
    leases = relationship("IpLease", back_populates="peer")

