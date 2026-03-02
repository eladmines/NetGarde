from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.features.domain_classification_jobs.models.domain_classification_job import DomainClassificationJob


class DomainClassificationJobRepository:
    def __init__(self, db: Session):
        self.db = db

    @staticmethod
    def _normalize_domain(domain: str) -> str:
        return domain.strip().lower()

    def enqueue(self, domain: str) -> None:
        d = self._normalize_domain(domain)
        if not d:
            return

        job = self.db.query(DomainClassificationJob).filter(DomainClassificationJob.domain == d).first()
        if not job:
            self.db.add(DomainClassificationJob(domain=d, status="pending", attempts=0))
            self.db.commit()
            return

        if job.status in {"completed", "processing"}:
            return

        job.status = "pending"
        job.last_error = None
        job.updated_at = datetime.now(timezone.utc)
        self.db.commit()

    def claim_next_pending(self, max_attempts: int = 5) -> Optional[DomainClassificationJob]:
        job = (
            self.db.query(DomainClassificationJob)
            .filter(
                DomainClassificationJob.status == "pending",
                DomainClassificationJob.attempts < max_attempts,
            )
            .order_by(DomainClassificationJob.created_at.asc())
            .with_for_update(skip_locked=True)
            .first()
        )
        if not job:
            return None

        job.status = "processing"
        job.attempts = (job.attempts or 0) + 1
        job.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(job)
        return job

    def mark_completed(self, job_id: int) -> None:
        job = self.db.query(DomainClassificationJob).filter(DomainClassificationJob.id == job_id).first()
        if not job:
            return
        job.status = "completed"
        job.last_error = None
        job.updated_at = datetime.now(timezone.utc)
        self.db.commit()

    def mark_failed(self, job_id: int, error: str, can_retry: bool = True, max_attempts: int = 5) -> None:
        job = self.db.query(DomainClassificationJob).filter(DomainClassificationJob.id == job_id).first()
        if not job:
            return
        retry_allowed = can_retry and (job.attempts or 0) < max_attempts
        job.status = "pending" if retry_allowed else "failed"
        job.last_error = (error or "")[:4000]
        job.updated_at = datetime.now(timezone.utc)
        self.db.commit()

