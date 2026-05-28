from pydantic import BaseModel, Field


class UsageReportRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    rx_bytes: int = Field(ge=0)
    tx_bytes: int = Field(ge=0)
    delta_rx_bytes: int = Field(ge=0)
    delta_tx_bytes: int = Field(ge=0)
    interval_sec: float = Field(gt=0)


class UsageReportResponse(BaseModel):
    stored: bool = True
    alert_created: bool = False
    rate_mib_per_sec: float = 0.0
