from sqlalchemy import Column, Integer, String, DateTime, Float, BigInteger
from datetime import datetime, timezone
from app.shared.database import Base


class DeviceUsageSample(Base):
    __tablename__ = "device_usage_samples"

    id = Column(Integer, primary_key=True, index=True)
    device_external_id = Column(String(64), nullable=False, index=True)
    recorded_at = Column(DateTime(timezone=True), nullable=False, index=True)
    interval_sec = Column(Float, nullable=False)
    rx_bytes = Column(BigInteger, nullable=False)
    tx_bytes = Column(BigInteger, nullable=False)
    delta_rx_bytes = Column(BigInteger, nullable=False)
    delta_tx_bytes = Column(BigInteger, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
