from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from app.shared.database import Base


class ClientBehaviorProfile(Base):
    __tablename__ = "client_behavior_profiles"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, unique=True, index=True)
    baseline_json = Column(Text, nullable=True)
    profile_ready = Column(Boolean, nullable=False, default=False)
    last_score = Column(Integer, nullable=True)
    last_scored_at = Column(DateTime(timezone=True), nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (UniqueConstraint("device_id", name="uq_client_behavior_profile_device"),)
