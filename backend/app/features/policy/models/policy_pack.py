from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text

from app.shared.database import Base


class PolicyPack(Base):
    """Toggleable category block list (domains live in policy/data/{slug}.txt)."""

    __tablename__ = "policy_packs"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    enabled_globally = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
