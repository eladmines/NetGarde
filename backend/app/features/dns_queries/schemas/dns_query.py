from pydantic import BaseModel
from datetime import datetime
from typing import Optional, List


class DnsQueryCreate(BaseModel):
    timestamp: datetime
    client_ip: str
    domain: str
    query_type: Optional[str] = None
    action: Optional[str] = None
    blocked: bool = False


class DnsQueryBulkCreate(BaseModel):
    queries: List[DnsQueryCreate]


class DnsQueryResponse(BaseModel):
    id: int
    timestamp: datetime
    client_ip: str
    domain: str
    query_type: Optional[str] = None
    action: Optional[str] = None
    blocked: bool
    created_at: Optional[datetime] = None

    class Config:
        from_attributes = True
