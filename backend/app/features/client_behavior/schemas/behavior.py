from datetime import datetime
from typing import Any, Dict, List, Literal, Optional

from pydantic import BaseModel, ConfigDict, Field

BehaviorReviewSource = Literal["template", "llm"]


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


class BehaviorReviewRead(BaseModel):
    device_id: int
    generated_at: datetime
    summary: str
    source: BehaviorReviewSource = "template"
    review_mode: str = "template"
    llm_model: Optional[str] = None
    llm_error: Optional[str] = None


class BehaviorProfileRead(BaseModel):
    device_id: int
    profile_ready: bool
    last_score: Optional[int] = None
    last_scored_at: Optional[datetime] = None
    baseline: Dict[str, Any] = Field(default_factory=dict)
    updated_at: Optional[datetime] = None


class ClientBlockedDomainCreate(BaseModel):
    domain: str = Field(min_length=1, max_length=253)
    expires_in_hours: Optional[int] = Field(default=None, ge=1, le=24 * 30)


class QuarantineStartRequest(BaseModel):
    hours: int = Field(default=4, ge=1, le=168)
    reason: Optional[str] = Field(default=None, max_length=500)


class QuarantineActionResponse(BaseModel):
    device_id: int
    in_quarantine: bool
    quarantine_expires_at: Optional[datetime] = None
    message: str


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


class BlockedClientSummary(BaseModel):
    """Device with active admin/quarantine enforcement or per-device DNS blocks."""

    device_id: int
    client_ip: Optional[str] = None
    hostname: Optional[str] = None
    mac_address: Optional[str] = None
    last_score: Optional[int] = None
    last_scored_at: Optional[datetime] = None
    in_quarantine: bool = False
    quarantine_expires_at: Optional[datetime] = None
    active_block_count: int = 0
    latest_blocked_domain: Optional[str] = None
    latest_block_at: Optional[datetime] = None
    latest_block_source: Optional[str] = None


class BlockedClientsListResponse(BaseModel):
    items: List[BlockedClientSummary]
    total: int
