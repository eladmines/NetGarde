from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.features.domain_categories.errors.domain_category import (
    DomainCategoryAlreadyExistsError,
    DomainCategoryNotFoundError,
)
from app.features.domain_categories.schemas.domain_category import DomainCategoryCreate
from app.features.domain_categories.services.domain_category_service import (
    create_domain_category,
    delete_domain_category,
    get_domain_categories,
    get_domain_categories_by_domain,
    get_domain_category_by_id,
    update_domain_category,
)
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


def create_domain_category_controller(data: DomainCategoryCreate, db: Session):
    try:
        return create_domain_category(data, db)
    except DomainCategoryAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.error("POST /domain-categories failed", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))


def get_domain_category_by_id_controller(mapping_id: int, db: Session):
    try:
        return get_domain_category_by_id(mapping_id, db)
    except DomainCategoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception as exc:
        logger.error("GET /domain-categories/{mapping_id} failed", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))


def get_domain_categories_controller(db: Session):
    try:
        return get_domain_categories(db)
    except Exception:
        logger.error("GET /domain-categories failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch domain categories")


def get_domain_categories_by_domain_controller(domain: str, db: Session):
    try:
        return get_domain_categories_by_domain(domain, db)
    except Exception as exc:
        logger.error("GET /domain-categories/by-domain failed", extra={"domain": domain}, exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))


def update_domain_category_controller(mapping_id: int, data: DomainCategoryCreate, db: Session):
    try:
        return update_domain_category(mapping_id, data, db)
    except DomainCategoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except DomainCategoryAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.error("PUT /domain-categories/{mapping_id} failed", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))


def delete_domain_category_controller(mapping_id: int, db: Session):
    try:
        return delete_domain_category(mapping_id, db)
    except DomainCategoryNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception:
        logger.error("DELETE /domain-categories/{mapping_id} failed", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete domain category")

