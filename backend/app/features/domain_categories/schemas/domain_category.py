from datetime import datetime
from typing import Optional

from pydantic import BaseModel, ConfigDict, Field


class DomainCategoryCreate(BaseModel):
    domain: str = Field(min_length=1, max_length=255)
    category_id: int
    confidence: Optional[int] = Field(default=None, ge=0, le=100)
    source: Optional[str] = Field(default="manual", max_length=50)
    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class DomainCategoryRead(BaseModel):
    id: int
    domain: str
    category_id: int
    confidence: Optional[int] = None
    source: Optional[str] = None
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    is_deleted: bool = False

    model_config = ConfigDict(from_attributes=True)

