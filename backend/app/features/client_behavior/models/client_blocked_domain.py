from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship
from app.shared.database import Base


class ClientBlockedDomain(Base):
    __tablename__ = "client_blocked_domains"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    domain = Column(String(255), nullable=False)
    root_domain = Column(String(255), nullable=True)
    source = Column(String(32), nullable=False, default="behavior_auto")
    score = Column(Integer, nullable=True)
    expires_at = Column(DateTime(timezone=True), nullable=True, index=True)
    revoked_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))

    device = relationship("Device", backref="client_blocked_domains")

    __table_args__ = (
        UniqueConstraint("device_id", "domain", name="uq_client_blocked_device_domain"),
    )
