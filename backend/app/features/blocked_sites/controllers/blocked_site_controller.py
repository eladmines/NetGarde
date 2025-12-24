from fastapi import HTTPException
from sqlalchemy.orm import Session
from app.features.blocked_sites.schemas.blocked_site import BlockedSiteCreate, BlockedSiteRead, CategoryCountsResponse
from app.features.blocked_sites.services.blocked_site_service import create_blocked_site, get_blocked_site_by_id, get_blocked_site_by_domain, get_blocked_sites, update_blocked_site, delete_blocked_site, get_blocked_sites_counts_by_category
from app.features.blocked_sites.errors.blocked_site import BlockedSiteAlreadyExistsError, BlockedSiteNotFoundError
from app.shared.schemas.pagination import PaginatedResponse
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)

def create_blocked_site_controller(blocked_site_data: BlockedSiteCreate, db: Session):
    try:
        logger.info("POST /blocked-sites - create", extra={"domain": blocked_site_data.domain})
        result = create_blocked_site(blocked_site_data, db)
        logger.info("POST /blocked-sites - created", extra={"blocked_site_id": getattr(result, "id", None)})
        return result
    except BlockedSiteAlreadyExistsError as e:
        logger.warning("POST /blocked-sites - conflict", extra={"domain": blocked_site_data.domain})
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error("POST /blocked-sites - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

def get_blocked_site_by_id_controller(blocked_site_id: int, db: Session):
    try:
        logger.info("GET /blocked-sites/{blocked_site_id} - fetch", extra={"blocked_site_id": blocked_site_id})
        blocked_site = get_blocked_site_by_id(blocked_site_id, db)
        if blocked_site is None:
            raise BlockedSiteNotFoundError(blocked_site_id)
        logger.info("GET /blocked-sites/{blocked_site_id} - ok", extra={"blocked_site_id": blocked_site_id})
        return blocked_site
    except BlockedSiteNotFoundError as e:
        logger.warning("GET /blocked-sites/{blocked_site_id} - not found", extra={"blocked_site_id": blocked_site_id})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("GET /blocked-sites/{blocked_site_id} - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

def get_blocked_site_by_domain_controller(blocked_site_domain: str, db: Session):
    try:
        logger.info("GET /blocked-sites/by-domain - fetch", extra={"domain": blocked_site_domain})
        blocked_site = get_blocked_site_by_domain(blocked_site_domain, db)
        if blocked_site is None:
            raise BlockedSiteNotFoundError(blocked_site_domain)
        logger.info("GET /blocked-sites/by-domain - ok", extra={"domain": blocked_site_domain})
        return blocked_site
    except BlockedSiteNotFoundError as e:
        logger.warning("GET /blocked-sites/by-domain - not found", extra={"domain": blocked_site_domain})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("GET /blocked-sites/by-domain - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

def get_blocked_sites_controller(db: Session, page: int = 1, page_size: int = 10, domain_search: str = None):
    try:
        logger.info("GET /blocked-sites - fetch", extra={"page": page, "page_size": page_size, "domain_search": domain_search})
        blocked_sites, total = get_blocked_sites(db, page=page, page_size=page_size, domain_search=domain_search)
        result = PaginatedResponse[BlockedSiteRead].create(
            items=blocked_sites,
            total=total,
            page=page,
            page_size=page_size
        )
        logger.info("GET /blocked-sites - ok", extra={"count": len(blocked_sites), "total": total})
        return result
    except Exception as e:
        logger.error("GET /blocked-sites - error", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch blocked sites")

def update_blocked_site_controller(blocked_site_id: int, blocked_site_data: BlockedSiteCreate, db: Session):
    try:
        logger.info("PUT /blocked-sites/{blocked_site_id} - update", extra={"blocked_site_id": blocked_site_id, "domain": blocked_site_data.domain})
        result = update_blocked_site(blocked_site_id, blocked_site_data, db)
        logger.info("PUT /blocked-sites/{blocked_site_id} - updated", extra={"blocked_site_id": blocked_site_id})
        return result
    except BlockedSiteNotFoundError as e:
        logger.warning("PUT /blocked-sites/{blocked_site_id} - not found", extra={"blocked_site_id": blocked_site_id})
        raise HTTPException(status_code=404, detail=str(e))
    except BlockedSiteAlreadyExistsError as e:
        logger.warning("PUT /blocked-sites/{blocked_site_id} - conflict", extra={"domain": blocked_site_data.domain})
        raise HTTPException(status_code=409, detail=str(e))
    except Exception as e:
        logger.error("PUT /blocked-sites/{blocked_site_id} - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(e))

def delete_blocked_site_controller(blocked_site_id: int, db: Session):
    try:
        logger.info("DELETE /blocked-sites/{blocked_site_id} - delete", extra={"blocked_site_id": blocked_site_id})
        result = delete_blocked_site(blocked_site_id, db)
        logger.info("DELETE /blocked-sites/{blocked_site_id} - deleted", extra={"blocked_site_id": blocked_site_id})
        return result
    except BlockedSiteNotFoundError as e:
        logger.warning("DELETE /blocked-sites/{blocked_site_id} - not found", extra={"blocked_site_id": blocked_site_id})
        raise HTTPException(status_code=404, detail=str(e))
    except Exception as e:
        logger.error("DELETE /blocked-sites/{blocked_site_id} - error", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete blocked site")

def get_blocked_sites_counts_by_category_controller(db: Session):
    try:
        logger.info("GET /blocked-sites/counts-by-category - fetch")
        counts = get_blocked_sites_counts_by_category(db)
        result = CategoryCountsResponse(counts=counts)
        logger.info("GET /blocked-sites/counts-by-category - ok", extra={"categories_count": len(counts)})
        return result
    except Exception as e:
        logger.error("GET /blocked-sites/counts-by-category - error", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch blocked sites counts by category")


