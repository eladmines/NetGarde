from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class DeviceLoginGeoObservationRead(BaseModel):
    device_id: int
    public_ip: str
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    region_name: Optional[str] = None
    city: Optional[str] = None
    observed_at: datetime
    source: str = "enroll"


class DeviceLoginGeoRead(BaseModel):
    device_id: int
    latest: Optional[DeviceLoginGeoObservationRead] = None
    history: List[DeviceLoginGeoObservationRead] = Field(default_factory=list)


class DeviceLoginGeoSummaryItem(BaseModel):
    device_id: int
    country_code: Optional[str] = None
    country_name: Optional[str] = None
    public_ip: Optional[str] = None
    observed_at: Optional[datetime] = None


class DeviceLoginGeoSummaryList(BaseModel):
    items: List[DeviceLoginGeoSummaryItem]
