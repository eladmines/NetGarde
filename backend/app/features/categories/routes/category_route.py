from fastapi import APIRouter, Depends
from sqlalchemy.orm import Session
from app.features.categories.schemas.category import CategoryCreate
from app.features.categories.controllers.category_controller import (
    create_category_controller,
    get_category_by_id_controller,
    get_categories_controller,
    update_category_controller,
    delete_category_controller,
)
from app.shared.dependencies import get_db

router = APIRouter(prefix="/categories", tags=["Categories"])


@router.post("")
def create_category_endpoint(category_data: CategoryCreate, db: Session = Depends(get_db)):
    return create_category_controller(category_data, db)


@router.get("")
def get_categories_endpoint(db: Session = Depends(get_db)):
    return get_categories_controller(db)


@router.get("/{category_id}")
def get_category_by_id_endpoint(category_id: int, db: Session = Depends(get_db)):
    return get_category_by_id_controller(category_id, db)


@router.put("/{category_id}")
def update_category_endpoint(category_id: int, category_data: CategoryCreate, db: Session = Depends(get_db)):
    return update_category_controller(category_id, category_data, db)


@router.delete("/{category_id}")
def delete_category_endpoint(category_id: int, db: Session = Depends(get_db)):
    return delete_category_controller(category_id, db)

