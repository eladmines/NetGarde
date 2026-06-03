from datetime import datetime

from pydantic import BaseModel, Field

from app.features.vpn.schemas.usage_live import DeviceUsageLiveItem, DeviceUsageLiveResponse


class UsageHistoryPoint(BaseModel):
    recorded_at: datetime
    rx_mib_per_sec: float = Field(ge=0)
    tx_mib_per_sec: float = Field(ge=0)
    total_mib_per_sec: float = Field(ge=0)
    reporting_clients: int = Field(ge=0)


class UsageHistoryResponse(BaseModel):
    points: list[UsageHistoryPoint]
    minutes: int


class UsageWsSnapshot(BaseModel):
    type: str = "usage_snapshot"
    history: UsageHistoryResponse
    live: DeviceUsageLiveResponse


class UsageWsUpdate(BaseModel):
    type: str = "usage_update"
    aggregate_point: UsageHistoryPoint
    live: DeviceUsageLiveResponse
