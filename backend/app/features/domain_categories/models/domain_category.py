from datetime import datetime, timezone

from sqlalchemy import Boolean, Column, DateTime, ForeignKey, Integer, String, UniqueConstraint
from sqlalchemy.orm import relationship

from app.shared.database import Base


class DomainCategory(Base):
    __tablename__ = "domain_categories"

    id = Column(Integer, primary_key=True, index=True)
    domain = Column(String(255), nullable=False, index=True)
    category_id = Column(Integer, ForeignKey("categories.id"), nullable=False, index=True)
    confidence = Column(Integer, nullable=True)  # Optional confidence score as 0-100
    source = Column(String(50), nullable=True)  # manual, ai, feed
    created_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc))
    created_by = Column(Integer, nullable=True)
    updated_at = Column(DateTime(timezone=True), default=lambda: datetime.now(timezone.utc), onupdate=lambda: datetime.now(timezone.utc))
    updated_by = Column(Integer, nullable=True)
    is_deleted = Column(Boolean, default=False, nullable=False)

    category = relationship("Category")

    __table_args__ = (
        UniqueConstraint("domain", "category_id", name="uq_domain_categories_domain_category_id"),
    )

