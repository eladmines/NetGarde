from datetime import datetime

from pydantic import BaseModel, Field


class NetworkOverviewStats(BaseModel):
    reporting_clients: int = Field(ge=0)
    live_total_mib_per_sec: float = Field(ge=0)
    peak_mib_per_sec: float = Field(ge=0)
    alerts_total: int = Field(ge=0)
    blocked_queries: int = Field(ge=0)
    enabled_policy_packs: int = Field(ge=0)
    elevated_behavior_clients: int = Field(ge=0)


class NetworkOverviewRead(BaseModel):
    generated_at: datetime
    period_minutes: int = Field(ge=1, le=24 * 60)
    bullets: list[str]
    stats: NetworkOverviewStats
