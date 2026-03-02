from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from sqlalchemy.orm import Session

from app.features.domain_categories.errors.domain_category import (
    DomainCategoryAlreadyExistsError,
    DomainCategoryNotFoundError,
)
from app.features.domain_categories.repositories.domain_category_repository import DomainCategoryRepository
from app.features.domain_categories.schemas.domain_category import DomainCategoryCreate
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


def create_domain_category(data: DomainCategoryCreate, db: Session):
    repository = DomainCategoryRepository(db)
    try:
        logger.info("Creating domain category mapping", extra={"domain": data.domain, "category_id": data.category_id})
        existing = repository.get_by_domain_and_category_id(data.domain, data.category_id)
        if existing:
            raise DomainCategoryAlreadyExistsError(data.domain, data.category_id)
        return repository.create(data)
    except DomainCategoryAlreadyExistsError:
        raise
    except IntegrityError:
        raise DomainCategoryAlreadyExistsError(data.domain, data.category_id)


def get_domain_category_by_id(mapping_id: int, db: Session):
    repository = DomainCategoryRepository(db)
    mapping = repository.get_by_id(mapping_id)
    if mapping is None:
        raise DomainCategoryNotFoundError(mapping_id)
    return mapping


def get_domain_categories(db: Session):
    repository = DomainCategoryRepository(db)
    try:
        return repository.get_all()
    except SQLAlchemyError as exc:
        logger.error("Failed to list domain categories", exc_info=True)
        raise exc


def get_domain_categories_by_domain(domain: str, db: Session):
    repository = DomainCategoryRepository(db)
    try:
        return repository.get_by_domain(domain)
    except SQLAlchemyError as exc:
        logger.error("Failed to list domain categories by domain", extra={"domain": domain}, exc_info=True)
        raise exc


def update_domain_category(mapping_id: int, data: DomainCategoryCreate, db: Session):
    repository = DomainCategoryRepository(db)
    try:
        existing = repository.get_by_domain_and_category_id(data.domain, data.category_id)
        if existing and existing.id != mapping_id:
            raise DomainCategoryAlreadyExistsError(data.domain, data.category_id)
        updated = repository.update(mapping_id, data)
        if updated is None:
            raise DomainCategoryNotFoundError(mapping_id)
        return updated
    except DomainCategoryAlreadyExistsError:
        raise
    except IntegrityError:
        raise DomainCategoryAlreadyExistsError(data.domain, data.category_id)


def delete_domain_category(mapping_id: int, db: Session):
    repository = DomainCategoryRepository(db)
    deleted = repository.delete(mapping_id)
    if not deleted:
        raise DomainCategoryNotFoundError(mapping_id)
    return {"message": "Domain category deleted successfully", "domain_category_id": mapping_id}

