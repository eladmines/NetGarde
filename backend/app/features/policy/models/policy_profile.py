from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, Integer, String, Text
from sqlalchemy.types import JSON

from app.shared.database import Base


class PolicyProfile(Base):
    """Per-device template: packs, lists, schedule, behavior sensitivity, quarantine."""

    __tablename__ = "policy_profiles"

    id = Column(Integer, primary_key=True, index=True)
    slug = Column(String(32), unique=True, nullable=False, index=True)
    name = Column(String(128), nullable=False)
    description = Column(Text, nullable=True)
    enabled_pack_slugs = Column(JSON, nullable=False, default=list)
    extra_block_domains = Column(JSON, nullable=False, default=list)
    allowlist_domains = Column(JSON, nullable=False, default=list)
    schedule_rules = Column(JSON, nullable=False, default=list)
    behavior_sensitivity = Column(String(16), nullable=False, default="medium")
    quarantine_on_abnormal = Column(Boolean, nullable=False, default=True)
    quarantine_hours = Column(Integer, nullable=False, default=4)
    is_builtin = Column(Boolean, nullable=False, default=False)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )
