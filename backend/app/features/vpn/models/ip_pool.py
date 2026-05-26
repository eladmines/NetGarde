from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.shared.database import Base


class IpPool(Base):
    __tablename__ = "ip_pools"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(100), nullable=False, unique=True, index=True)
    cidr = Column(String(43), nullable=False)  # enough for IPv6 CIDR if needed later

    gateway_ip = Column(String(45), nullable=False)
    dns_ip = Column(String(45), nullable=False)

    mtu = Column(Integer, nullable=True)
    allowed_ips = Column(String(400), nullable=True)  # csv, e.g. "0.0.0.0/0,::/0"
    endpoint = Column(String(255), nullable=False)  # host:port
    server_public_key = Column(String(255), nullable=False)
    persistent_keepalive = Column(Integer, nullable=True)

    is_active = Column(Boolean, nullable=False, default=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

