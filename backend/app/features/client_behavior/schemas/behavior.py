from datetime import datetime
from typing import Any, Dict, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class DeviceSecurityPolicyRead(BaseModel):
    device_id: int
    auto_block_enabled: bool
    auto_block_threshold: int
    max_blocks_per_day: int
    model_config = ConfigDict(from_attributes=True)


class DeviceSecurityPolicyUpdate(BaseModel):
    auto_block_enabled: Optional[bool] = None
    auto_block_threshold: Optional[int] = Field(default=None, ge=50, le=100)
    max_blocks_per_day: Optional[int] = Field(default=None, ge=1, le=100)


class BehaviorProfileRead(BaseModel):
    device_id: int
    profile_ready: bool
    last_score: Optional[int] = None
    last_scored_at: Optional[datetime] = None
    baseline: Dict[str, Any] = Field(default_factory=dict)
    updated_at: Optional[datetime] = None


class ClientBlockedDomainRead(BaseModel):
    id: int
    device_id: int
    domain: str
    root_domain: Optional[str] = None
    source: str
    score: Optional[int] = None
    expires_at: Optional[datetime] = None
    revoked_at: Optional[datetime] = None
    created_at: Optional[datetime] = None
    model_config = ConfigDict(from_attributes=True)


class ClientBlockSyncEntry(BaseModel):
    device_id: int
    mac_address: str
    tag: str
    domains: List[str]


class ClientBlockSyncResponse(BaseModel):
    entries: List[ClientBlockSyncEntry]


class BehaviorRecomputeResult(BaseModel):
    devices_updated: int
