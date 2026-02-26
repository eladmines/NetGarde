from pydantic import BaseModel, ConfigDict, field_validator
from datetime import datetime
from typing import Optional, List


class DeviceCreate(BaseModel):
    client_ip: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    source: str = "manual"

    @field_validator("mac_address")
    @classmethod
    def normalize_mac(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.strip().lower()


class DeviceUpdate(BaseModel):
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    is_active: Optional[bool] = None

    @field_validator("mac_address")
    @classmethod
    def normalize_mac(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.strip().lower()


class DeviceRead(BaseModel):
    id: int
    client_ip: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    source: str
    is_active: bool
    created_at: Optional[datetime] = None
    updated_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class DhcpLeaseRecord(BaseModel):
    client_ip: str
    hostname: Optional[str] = None
    mac_address: Optional[str] = None

    @field_validator("mac_address")
    @classmethod
    def normalize_mac(cls, value: Optional[str]) -> Optional[str]:
        if value is None:
            return None
        return value.strip().lower()


class DhcpSyncRequest(BaseModel):
    leases: List[DhcpLeaseRecord]


class DhcpSyncResult(BaseModel):
    processed: int
    created: int
    updated: int
