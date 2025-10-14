from sqlalchemy import Column, Integer, String, DateTime
from datetime import datetime
from app.database import Base

class Rule(Base):
    __tablename__ = "rules"
    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String, unique=True, index=True)
    reason = Column(String)
    created_at = Column(DateTime, default=datetime.now)
    updated_at = Column(DateTime, default=datetime.now)
    deleted_at = Column(DateTime, default=datetime.now)
