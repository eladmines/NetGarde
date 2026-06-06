from datetime import datetime
from typing import Optional

from pydantic import BaseModel, Field


class DeviceUsageLiveItem(BaseModel):
    """Latest VPN tunnel throughput sample for dashboard Live Clients."""

    device_id: Optional[int] = None
    vpn_device_id: str
    client_ip: Optional[str] = None
    recorded_at: datetime
    interval_sec: float = Field(gt=0)
    rx_bytes: int = Field(ge=0)
    tx_bytes: int = Field(ge=0)
    delta_rx_bytes: int = Field(ge=0)
    delta_tx_bytes: int = Field(ge=0)
    rx_mib_per_sec: float = Field(ge=0)
    tx_mib_per_sec: float = Field(ge=0)
    total_mib_per_sec: float = Field(ge=0)


class DeviceUsageLiveResponse(BaseModel):
    items: list[DeviceUsageLiveItem]
    max_age_sec: int
