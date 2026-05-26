from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, UniqueConstraint
from app.shared.database import Base


class DeviceSecurityPolicy(Base):
    __tablename__ = "device_security_policies"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, unique=True)
    auto_block_enabled = Column(Boolean, nullable=False, default=False)
    auto_block_threshold = Column(Integer, nullable=False, default=85)
    max_blocks_per_day = Column(Integer, nullable=False, default=10)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (UniqueConstraint("device_id", name="uq_device_security_policy_device"),)
