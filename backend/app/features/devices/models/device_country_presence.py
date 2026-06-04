from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from app.shared.database import Base


class DeviceCountryPresence(Base):
    """Countries inferred from DNS domains for a device (first/last seen, query volume)."""

    __tablename__ = "device_country_presences"

    id = Column(Integer, primary_key=True, index=True)
    device_id = Column(Integer, ForeignKey("devices.id", ondelete="CASCADE"), nullable=False, index=True)
    country_code = Column(String(8), nullable=False, index=True)
    first_seen_at = Column(DateTime(timezone=True), nullable=False)
    last_seen_at = Column(DateTime(timezone=True), nullable=False)
    query_count = Column(Integer, nullable=False, default=0)

    __table_args__ = (
        UniqueConstraint("device_id", "country_code", name="uq_device_country_presence"),
    )
