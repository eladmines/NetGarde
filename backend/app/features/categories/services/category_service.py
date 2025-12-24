from sqlalchemy.orm import Session
from app.features.categories.schemas.category import CategoryCreate
from app.features.categories.repositories.category_repository import CategoryRepository
from app.features.categories.errors.category import CategoryAlreadyExistsError, CategoryNotFoundError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


def create_category(category_data: CategoryCreate, db: Session):
    repository = CategoryRepository(db)
    try:
        logger.info("Creating category", extra={"category_name": category_data.name})
        category = repository.create(category_data)
        logger.info("Category created", extra={"category_id": getattr(category, "id", None), "category_name": category.name})
        return category
    except IntegrityError:
        logger.warning("Category already exists", extra={"category_name": category_data.name})
        raise CategoryAlreadyExistsError(category_data.name)


def get_category_by_id(category_id: int, db: Session):
    repository = CategoryRepository(db)
    try:
        category = repository.get_by_id(category_id)
        if category is None:
            logger.warning("Category not found by id", extra={"category_id": category_id})
        else:
            logger.info("Fetched category by id", extra={"category_id": category_id})
        return category
    except IntegrityError:
        logger.error("Integrity error while fetching category by id", extra={"category_id": category_id}, exc_info=True)
        raise CategoryNotFoundError(category_id)


def get_category_by_name(category_name: str, db: Session):
    repository = CategoryRepository(db)
    try:
        category = repository.get_by_name(category_name)
        if category is None:
            logger.warning("Category not found by name", extra={"category_name": category_name})
        else:
            logger.info("Fetched category by name", extra={"category_name": category_name})
        return category
    except IntegrityError:
        logger.error("Integrity error while fetching category by name", extra={"category_name": category_name}, exc_info=True)
        raise CategoryNotFoundError(category_name)


def get_categories(db: Session):
    repository = CategoryRepository(db)
    try:
        categories = repository.get_categories()
        logger.info("Fetched categories", extra={"count": len(categories)})
        return categories
    except SQLAlchemyError as e:
        logger.error("Database error while listing categories", exc_info=True)
        raise e


def update_category(category_id: int, category_data: CategoryCreate, db: Session):
    repository = CategoryRepository(db)
    try:
        logger.info("Updating category", extra={"category_id": category_id, "category_name": category_data.name})
        category = repository.update(category_id, category_data)
        if category is None:
            logger.warning("Category not found for update", extra={"category_id": category_id})
            raise CategoryNotFoundError(category_id)
        logger.info("Category updated successfully", extra={"category_id": category_id, "category_name": category.name})
        return category
    except CategoryNotFoundError:
        raise
    except IntegrityError:
        logger.warning("Category with name already exists", extra={"category_name": category_data.name})
        raise CategoryAlreadyExistsError(category_data.name)
    except SQLAlchemyError as e:
        logger.error("Database error while updating category", extra={"category_id": category_id}, exc_info=True)
        raise e


def delete_category(category_id: int, db: Session):
    repository = CategoryRepository(db)
    try:
        logger.info("Deleting category", extra={"category_id": category_id})
        deleted = repository.delete(category_id)
        if not deleted:
            logger.warning("Category not found for deletion", extra={"category_id": category_id})
            raise CategoryNotFoundError(category_id)
        logger.info("Category deleted successfully", extra={"category_id": category_id})
        return {"message": "Category deleted successfully", "category_id": category_id}
    except CategoryNotFoundError:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error while deleting category", extra={"category_id": category_id}, exc_info=True)
        raise e

