from datetime import datetime
from typing import List, Optional

from pydantic import BaseModel, Field


class CountryCountItem(BaseModel):
    country_code: str
    country_name: str
    query_count: int = Field(ge=0)
    share_percent: float = Field(ge=0, le=100)
    first_seen_at: Optional[datetime] = None
    last_seen_at: Optional[datetime] = None
    is_new: bool = False


class DeviceCountryBreakdownRead(BaseModel):
    device_id: int
    period_hours: int = Field(ge=1, le=24 * 30)
    total_queries: int = Field(ge=0)
    primary_country_code: Optional[str] = None
    primary_country_name: Optional[str] = None
    countries: List[CountryCountItem] = Field(default_factory=list)
    note: Optional[str] = None
    known_regions_count: int = Field(default=0, ge=0)


class DeviceCountrySummaryItem(BaseModel):
    device_id: int
    primary_country_code: Optional[str] = None
    primary_country_name: Optional[str] = None


class DeviceCountrySummaryList(BaseModel):
    items: List[DeviceCountrySummaryItem]
    period_hours: int
