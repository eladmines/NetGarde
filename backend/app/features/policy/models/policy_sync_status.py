from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String

from app.shared.database import Base


class PolicySyncStatus(Base):
    """Singleton row updated when dns-sync completes policy push."""

    __tablename__ = "policy_sync_status"

    id = Column(Integer, primary_key=True, default=1)
    last_sync_at = Column(DateTime(timezone=True), nullable=True)
    last_success = Column(Boolean, nullable=True)
    last_message = Column(String(512), nullable=True)
