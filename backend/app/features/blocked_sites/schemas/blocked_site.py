from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional, Dict

class BlockedSiteCreate(BaseModel):
    domain: str
    reason: str
    category: Optional[str] = None
    created_by: Optional[int] = None
    updated_by: Optional[int] = None

class BlockedSiteRead(BaseModel):
    id: int
    domain: str
    reason: str
    category: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    is_deleted: bool = False
    model_config = ConfigDict(from_attributes=True)

class CategoryCountsResponse(BaseModel):
    counts: Dict[str, int]


