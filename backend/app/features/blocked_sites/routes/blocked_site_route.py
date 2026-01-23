from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from app.features.blocked_sites.schemas.blocked_site import BlockedSiteCreate
from app.features.blocked_sites.controllers.blocked_site_controller import (
    create_blocked_site_controller,
    get_blocked_site_by_id_controller,
    get_blocked_sites_controller,
    update_blocked_site_controller,
    delete_blocked_site_controller,
    get_blocked_sites_counts_by_category_controller,
)
from app.features.blocked_sites.dependencies import get_blocked_site_service
from app.features.blocked_sites.services.blocked_site_service_interface import IBlockedSiteService
from app.shared.dependencies import get_db

router = APIRouter(prefix="/blocked-sites", tags=["Blocked Sites"])

@router.post("/")
def create_blocked_site_endpoint(
    blocked_site_data: BlockedSiteCreate, 
    db: Session = Depends(get_db),
    service: IBlockedSiteService = Depends(get_blocked_site_service)
):
    return create_blocked_site_controller(blocked_site_data, db, service)

@router.get("")
def get_blocked_sites_endpoint(
    page: int = Query(default=1, ge=1, description="Page number (1-based)"),
    page_size: int = Query(default=10, ge=1, le=100, description="Number of items per page"),
    domain_search: str = Query(default=None, description="Domain search query (case-insensitive partial match)"),
    db: Session = Depends(get_db),
    service: IBlockedSiteService = Depends(get_blocked_site_service)
):
    return get_blocked_sites_controller(db, service, page=page, page_size=page_size, domain_search=domain_search)

@router.get("/counts-by-category")
def get_blocked_sites_counts_by_category_endpoint(
    db: Session = Depends(get_db),
    service: IBlockedSiteService = Depends(get_blocked_site_service)
):
    return get_blocked_sites_counts_by_category_controller(db, service)

@router.get("/{blocked_site_id}")
def get_blocked_site_by_id_endpoint(
    blocked_site_id: int, 
    db: Session = Depends(get_db),
    service: IBlockedSiteService = Depends(get_blocked_site_service)
):
    return get_blocked_site_by_id_controller(blocked_site_id, db, service)

@router.put("/{blocked_site_id}")
def update_blocked_site_endpoint(
    blocked_site_id: int, 
    blocked_site_data: BlockedSiteCreate, 
    db: Session = Depends(get_db),
    service: IBlockedSiteService = Depends(get_blocked_site_service)
):
    return update_blocked_site_controller(blocked_site_id, blocked_site_data, db, service)

@router.delete("/{blocked_site_id}")
def delete_blocked_site_endpoint(
    blocked_site_id: int, 
    db: Session = Depends(get_db),
    service: IBlockedSiteService = Depends(get_blocked_site_service)
):
    return delete_blocked_site_controller(blocked_site_id, db, service)
