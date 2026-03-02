from datetime import datetime, timezone
from typing import List, Optional, Set

from sqlalchemy.orm import Session

from app.features.domain_categories.models.domain_category import DomainCategory
from app.features.domain_categories.schemas.domain_category import DomainCategoryCreate


class DomainCategoryRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _normalize_domain(domain: str) -> str:
        return domain.strip().lower()

    def create(self, data: DomainCategoryCreate) -> DomainCategory:
        payload = data.model_dump()
        payload["domain"] = self._normalize_domain(payload["domain"])
        if payload.get("created_by") is None:
            payload["created_by"] = 1
        if payload.get("updated_by") is None:
            payload["updated_by"] = payload["created_by"]

        record = DomainCategory(**payload)
        self.db.add(record)
        self.db.commit()
        self.db.refresh(record)
        return record

    def get_by_id(self, mapping_id: int) -> Optional[DomainCategory]:
        return (
            self.db.query(DomainCategory)
            .filter(DomainCategory.id == mapping_id, DomainCategory.is_deleted.is_(False))
            .first()
        )

    def get_by_domain(self, domain: str) -> List[DomainCategory]:
        normalized = self._normalize_domain(domain)
        return (
            self.db.query(DomainCategory)
            .filter(DomainCategory.domain == normalized, DomainCategory.is_deleted.is_(False))
            .all()
        )

    def get_all(self) -> List[DomainCategory]:
        return self.db.query(DomainCategory).filter(DomainCategory.is_deleted.is_(False)).all()

    def get_mapped_domains(self, domains: List[str]) -> Set[str]:
        if not domains:
            return set()

        normalized = [self._normalize_domain(d) for d in domains]
        rows = (
            self.db.query(DomainCategory.domain)
            .filter(
                DomainCategory.domain.in_(normalized),
                DomainCategory.is_deleted.is_(False),
            )
            .distinct()
            .all()
        )
        return {r[0] for r in rows}

    def get_by_domain_and_category_id(self, domain: str, category_id: int) -> Optional[DomainCategory]:
        normalized = self._normalize_domain(domain)
        return (
            self.db.query(DomainCategory)
            .filter(
                DomainCategory.domain == normalized,
                DomainCategory.category_id == category_id,
                DomainCategory.is_deleted.is_(False),
            )
            .first()
        )

    def update(self, mapping_id: int, data: DomainCategoryCreate) -> Optional[DomainCategory]:
        record = self.get_by_id(mapping_id)
        if not record:
            return None

        record.domain = self._normalize_domain(data.domain)
        record.category_id = data.category_id
        record.confidence = data.confidence
        record.source = data.source
        record.updated_by = data.updated_by if data.updated_by is not None else 1
        record.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(record)
        return record

    def delete(self, mapping_id: int) -> bool:
        record = self.get_by_id(mapping_id)
        if not record:
            return False

        record.is_deleted = True
        record.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        return True

