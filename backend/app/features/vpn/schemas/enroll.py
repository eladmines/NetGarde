from pydantic import BaseModel, Field, field_validator
from typing import List, Optional


class EnrollRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    public_key: str = Field(min_length=1, max_length=255)
    hostname: Optional[str] = Field(None, max_length=255)
    mac_address: Optional[str] = Field(None, max_length=17)
    policy_profile_slug: Optional[str] = Field(
        None,
        max_length=32,
        description="Policy profile: kids, teen, or work",
    )
    client_public_ip: Optional[str] = Field(
        None,
        max_length=45,
        description="Optional public IP reported by the client before VPN tunnel is up",
    )

    @field_validator("hostname")
    @classmethod
    def strip_hostname(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip()
        return s or None

    @field_validator("mac_address")
    @classmethod
    def normalize_mac(cls, v: Optional[str]) -> Optional[str]:
        if v is None:
            return None
        s = v.strip().lower()
        return s or None


class EnrollResponse(BaseModel):
    # client supports either wireguard_conf or structured fields; we return structured
    address: str
    dns: List[str]
    mtu: int
    server_public_key: str
    endpoint: str
    allowed_ips: List[str]
    persistent_keepalive: Optional[int] = None
    device_token: str = Field(
        ...,
        description="Device credential for authenticated API calls (e.g. usage reporting)",
    )

