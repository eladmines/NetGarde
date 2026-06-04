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
    """Unique domains in the pack list (snapshot or seed file)."""
    blocked_sites_count: int = 0
    """Domains actively blocked network-wide when enabled_globally (equals domain_count if on)."""
    domain_list_source: str = "seed"
    """snapshot = downloaded upstream list; seed = bundled fallback until Refresh."""
    model_config = ConfigDict(from_attributes=True)


class PolicyPackUpdate(BaseModel):
    enabled_globally: bool


class PolicyPackRefreshResponse(BaseModel):
    slug: str
    domain_count: int
    message: str


class PolicyPackDomainsPage(BaseModel):
    slug: str
    domains: List[str]
    total: int
    skip: int
    limit: int
    domain_list_source: str
    query: str = ""


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


class ForbiddenCountryRuleRead(BaseModel):
    user_country: str
    user_country_name: str
    blocked_countries: List[str]
    blocked_country_names: List[str] = Field(default_factory=list)


class ForbiddenCountryPolicyRead(BaseModel):
    enabled: bool
    user_country_source: str = "vpn_login_geo"
    rules: List[ForbiddenCountryRuleRead] = Field(default_factory=list)
    vpn_login_block_enabled: bool = False
    blocked_vpn_login_countries: List[str] = Field(default_factory=list)
    blocked_vpn_login_country_names: List[str] = Field(default_factory=list)


class PolicyDeviceDnsEntry(BaseModel):
    device_id: int
    mac_address: str
    tag: str
    block_domains: List[str]
    allowlist_only: bool = False
    allowlist_domains: List[str] = Field(default_factory=list)
    block_country_tlds: List[str] = Field(
        default_factory=list,
        description="dnsmasq suffix patterns (e.g. .ir) for forbidden-country ccTLD blocking",
    )


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
