from datetime import datetime
from typing import Any, List, Optional

from pydantic import BaseModel, ConfigDict, Field


class PolicyPackRead(BaseModel):
    id: int
    slug: str
    name: str
    description: Optional[str] = None
    enabled_globally: bool
    domain_count: int = 0
    model_config = ConfigDict(from_attributes=True)


class PolicyPackUpdate(BaseModel):
    enabled_globally: bool


class PolicyProfileRead(BaseModel):
    id: int
    slug: str
    name: str
    description: Optional[str] = None
    enabled_pack_slugs: List[str] = Field(default_factory=list)
    extra_block_domains: List[str] = Field(default_factory=list)
    allowlist_domains: List[str] = Field(default_factory=list)
    schedule_rules: List[dict[str, Any]] = Field(default_factory=list)
    behavior_sensitivity: str
    quarantine_on_abnormal: bool
    quarantine_hours: int
    is_builtin: bool
    model_config = ConfigDict(from_attributes=True)


class PolicyProfileUpdate(BaseModel):
    enabled_pack_slugs: Optional[List[str]] = None
    extra_block_domains: Optional[List[str]] = None
    allowlist_domains: Optional[List[str]] = None
    schedule_rules: Optional[List[dict[str, Any]]] = None
    behavior_sensitivity: Optional[str] = None
    quarantine_on_abnormal: Optional[bool] = None
    quarantine_hours: Optional[int] = Field(default=None, ge=1, le=168)


class DevicePolicyAssignmentRead(BaseModel):
    device_id: int
    policy_profile_id: Optional[int] = None
    policy_profile_slug: Optional[str] = None
    policy_profile_name: Optional[str] = None
    in_quarantine: bool = False
    quarantine_expires_at: Optional[datetime] = None


class AssignPolicyProfileRequest(BaseModel):
    policy_profile_slug: str


class PolicyDeviceDnsEntry(BaseModel):
    device_id: int
    mac_address: str
    tag: str
    block_domains: List[str]
    allowlist_only: bool = False
    allowlist_domains: List[str] = Field(default_factory=list)


class PolicyDnsSyncResponse(BaseModel):
    global_domains: List[str] = Field(default_factory=list)
    entries: List[PolicyDeviceDnsEntry] = Field(default_factory=list)


class PolicySyncStatusRead(BaseModel):
    last_sync_at: Optional[datetime] = None
    last_success: Optional[bool] = None
    last_message: Optional[str] = None


class PolicySyncReport(BaseModel):
    success: bool
    message: Optional[str] = None


class PolicyApplyResponse(BaseModel):
    queued: bool = True
    message: str = "Policy enforcement sync queued"
