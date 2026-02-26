from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime, timezone
from app.shared.database import Base


class Device(Base):
    __tablename__ = "devices"

    id = Column(Integer, primary_key=True, index=True)
    client_ip = Column(String(45), unique=True, nullable=False, index=True)  # IPv4/IPv6
    hostname = Column(String(255), nullable=True, index=True)
    mac_address = Column(String(17), nullable=True, unique=True, index=True)  # AA:BB:CC:DD:EE:FF
    vendor = Column(String(100), nullable=True, index=True)  # Inferred from MAC OUI prefix
    source = Column(String(20), nullable=False, default="manual")  # manual, dhcp_lease
    is_active = Column(Boolean, default=True, nullable=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc)
    )
