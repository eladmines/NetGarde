from datetime import datetime, timezone

from sqlalchemy import Column, DateTime, Integer, String, Text

from app.shared.database import Base


class DomainClassificationJob(Base):
    __tablename__ = "domain_classification_jobs"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, unique=True, index=True)
    status = Column(String(20), nullable=False, default="pending", index=True)  # pending|processing|completed|failed
    attempts = Column(Integer, nullable=False, default=0)
    last_error = Column(Text, nullable=True)
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    updated_at = Column(
        DateTime(timezone=True),
        default=lambda: datetime.now(timezone.utc),
        onupdate=lambda: datetime.now(timezone.utc),
    )

