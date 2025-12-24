from pydantic import BaseModel, ConfigDict
from datetime import datetime
from typing import Optional


class CategoryCreate(BaseModel):
    name: str
    created_by: Optional[int] = None
    updated_by: Optional[int] = None


class CategoryRead(BaseModel):
    id: int
    name: str
    created_at: Optional[datetime] = None
    created_by: Optional[int] = None
    updated_at: Optional[datetime] = None
    updated_by: Optional[int] = None
    is_deleted: bool = False
    model_config = ConfigDict(from_attributes=True)

