from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.features.domain_categories.controllers.domain_category_controller import (
    create_domain_category_controller,
    delete_domain_category_controller,
    get_domain_categories_by_domain_controller,
    get_domain_categories_controller,
    get_domain_category_by_id_controller,
    update_domain_category_controller,
)
from app.features.domain_categories.schemas.domain_category import DomainCategoryCreate
from app.shared.dependencies import get_db

router = APIRouter(prefix="/domain-categories", tags=["Domain Categories"])


@router.post("")
def create_domain_category_endpoint(data: DomainCategoryCreate, db: Session = Depends(get_db)):
    return create_domain_category_controller(data, db)


@router.get("")
def get_domain_categories_endpoint(db: Session = Depends(get_db)):
    return get_domain_categories_controller(db)


@router.get("/by-domain")
def get_domain_categories_by_domain_endpoint(
    domain: str = Query(..., min_length=1),
    db: Session = Depends(get_db),
):
    return get_domain_categories_by_domain_controller(domain, db)


@router.get("/{mapping_id}")
def get_domain_category_by_id_endpoint(mapping_id: int, db: Session = Depends(get_db)):
    return get_domain_category_by_id_controller(mapping_id, db)


@router.put("/{mapping_id}")
def update_domain_category_endpoint(
    mapping_id: int,
    data: DomainCategoryCreate,
    db: Session = Depends(get_db),
):
    return update_domain_category_controller(mapping_id, data, db)


@router.delete("/{mapping_id}")
def delete_domain_category_endpoint(mapping_id: int, db: Session = Depends(get_db)):
    return delete_domain_category_controller(mapping_id, db)

