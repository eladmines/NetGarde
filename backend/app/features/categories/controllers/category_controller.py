from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.features.categories.schemas.category import CategoryCreate
from app.features.categories.services.category_service import (
    create_category,
    get_category_by_id,
    get_category_by_name,
    get_categories,
    update_category,
    delete_category,
)
from app.features.categories.errors.category import CategoryAlreadyExistsError, CategoryNotFoundError
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


def create_category_controller(category_data: CategoryCreate, db: Session):
    try:
        logger.info("POST /categories - create", extra={"category_name": category_data.name})
        result = create_category(category_data, db)
        logger.info("POST /categories - created", extra={"category_id": getattr(result, "id", None)})
        return result
    except CategoryAlreadyExistsError as e:
        logger.warning("POST /categories - conflict", extra={"category_name": category_data.name})
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error("POST /categories - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


def get_category_by_id_controller(category_id: int, db: Session):
    try:
        logger.info("GET /categories/{category_id} - fetch", extra={"category_id": category_id})
        category = get_category_by_id(category_id, db)
        if category is None:
            raise CategoryNotFoundError(category_id)
        logger.info("GET /categories/{category_id} - ok", extra={"category_id": category_id})
        return category
    except CategoryNotFoundError as e:
        logger.warning("GET /categories/{category_id} - not found", extra={"category_id": category_id})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("GET /categories/{category_id} - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


def get_category_by_name_controller(category_name: str, db: Session):
    try:
        logger.info("GET /categories/by-name - fetch", extra={"category_name": category_name})
        category = get_category_by_name(category_name, db)
        if category is None:
            raise CategoryNotFoundError(category_name)
        logger.info("GET /categories/by-name - ok", extra={"category_name": category_name})
        return category
    except CategoryNotFoundError as e:
        logger.warning("GET /categories/by-name - not found", extra={"category_name": category_name})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("GET /categories/by-name - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


def get_categories_controller(db: Session):
    try:
        logger.info("GET /categories - fetch all")
        categories = get_categories(db)
        logger.info("GET /categories - ok", extra={"count": len(categories)})
        return categories
    except Exception as e:
        logger.error("GET /categories - error", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch categories")


def update_category_controller(category_id: int, category_data: CategoryCreate, db: Session):
    try:
        logger.info("PUT /categories/{category_id} - update", extra={"category_id": category_id, "category_name": category_data.name})
        updated_category = update_category(category_id, category_data, db)
        logger.info("PUT /categories/{category_id} - updated", extra={"category_id": category_id, "category_name": updated_category.name})
        return updated_category
    except CategoryNotFoundError as e:
        logger.warning("PUT /categories/{category_id} - not found", extra={"category_id": category_id})
        raise HTTPException(status_code=404, detail=str(e))
    except CategoryAlreadyExistsError as e:
        logger.warning("PUT /categories/{category_id} - conflict", extra={"category_id": category_id, "category_name": category_data.name})
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error("PUT /categories/{category_id} - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))


def delete_category_controller(category_id: int, db: Session):
    try:
        logger.info("DELETE /categories/{category_id} - delete", extra={"category_id": category_id})
        result = delete_category(category_id, db)
        logger.info("DELETE /categories/{category_id} - deleted", extra={"category_id": category_id})
        return result
    except CategoryNotFoundError as e:
        logger.warning("DELETE /categories/{category_id} - not found", extra={"category_id": category_id})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("DELETE /categories/{category_id} - error", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete category")

