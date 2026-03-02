import time

from sqlalchemy.exc import IntegrityError

from app.features.categories.models.category import Category
from app.features.domain_categories.repositories.domain_category_repository import DomainCategoryRepository
from app.features.domain_categories.schemas.domain_category import DomainCategoryCreate
from app.features.domain_classification_jobs.repositories.domain_classification_job_repository import (
    DomainClassificationJobRepository,
)
from app.shared.config import settings
from app.shared.database import SessionLocal
from app.shared.domain_classifier import classify_domain_category_ai
from app.shared.utils.logging import setup_logging, get_logger

setup_logging()
logger = get_logger(__name__)


def get_or_create_category_id(category_name: str, db) -> int:
    category = db.query(Category).filter(Category.name == category_name, Category.is_deleted.is_(False)).first()
    if category:
        return category.id

    try:
        category = Category(name=category_name, created_by=1, updated_by=1)
        db.add(category)
        db.commit()
        db.refresh(category)
        return category.id
    except IntegrityError:
        db.rollback()
        existing = db.query(Category).filter(Category.name == category_name, Category.is_deleted.is_(False)).first()
        if existing:
            return existing.id
        raise


def process_one_job(max_attempts: int = 5) -> bool:
    db = SessionLocal()
    try:
        job_repo = DomainClassificationJobRepository(db)
        mapping_repo = DomainCategoryRepository(db)
        job = job_repo.claim_next_pending(max_attempts=max_attempts)
        if not job:
            return False

        try:
            category_name, confidence, source = classify_domain_category_ai(job.domain)
            category_id = get_or_create_category_id(category_name, db)
            existing = mapping_repo.get_by_domain_and_category_id(job.domain, category_id)
            if not existing:
                mapping_repo.create(
                    DomainCategoryCreate(
                        domain=job.domain,
                        category_id=category_id,
                        confidence=confidence,
                        source=source,
                        created_by=1,
                        updated_by=1,
                    )
                )
            job_repo.mark_completed(job.id)
            logger.info(
                "Domain classified",
                extra={"domain": job.domain, "category": category_name, "confidence": confidence, "source": source},
            )
            return True
        except Exception as exc:
            db.rollback()
            job_repo.mark_failed(job.id, str(exc), can_retry=True, max_attempts=max_attempts)
            logger.warning("Failed to classify domain", extra={"domain": job.domain}, exc_info=True)
            return True
    finally:
        db.close()


def main() -> int:
    if not settings.AI_CLASSIFIER_ENABLED:
        logger.info("AI classifier worker disabled (AI_CLASSIFIER_ENABLED=false)")
        return 0

    logger.info("Starting domain classification worker")
    logger.info("Poll interval seconds: %s", settings.DOMAIN_CLASSIFIER_POLL_INTERVAL_SECONDS)
    while True:
        processed = process_one_job()
        if not processed:
            time.sleep(settings.DOMAIN_CLASSIFIER_POLL_INTERVAL_SECONDS)


if __name__ == "__main__":
    raise SystemExit(main())

