from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, Text, UniqueConstraint
from app.shared.database import Base


class ClientBehaviorRollup(Base):
    __tablename__ = "client_behavior_rollups"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    window_start = Column(DateTime(timezone=True), nullable=False, index=True)
    query_count = Column(Integer, nullable=False, default=0)
    unique_roots = Column(Integer, nullable=False, default=0)
    new_roots = Column(Integer, nullable=False, default=0)
    hour_utc = Column(Integer, nullable=False)
    country_counts_json = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

    __table_args__ = (
        UniqueConstraint("device_id", "window_start", name="uq_behavior_rollup_device_window"),
    )
