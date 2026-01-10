from sqlalchemy import Column, Integer, String, DateTime, Boolean
from datetime import datetime
from app.shared.database import Base


class Category(Base):
    __tablename__ = "categories"
    id = Column(Integer, primary_key=True, index=True)
    name = Column(String, unique=True, index=True, nullable=False)
    created_at = Column(DateTime, default=datetime.now)
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime, default=datetime.now, onupdate=datetime.now)
    updated_by = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

