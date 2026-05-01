from pydantic import BaseModel, Field
from typing import List, Optional


class EnrollRequest(BaseModel):
    device_id: str = Field(min_length=1, max_length=64)
    public_key: str = Field(min_length=1, max_length=255)


class EnrollResponse(BaseModel):
    # client supports either wireguard_conf or structured fields; we return structured
    address: str
    dns: List[str]
    mtu: int
    server_public_key: str
    endpoint: str
    allowed_ips: List[str]
    persistent_keepalive: Optional[int] = None

