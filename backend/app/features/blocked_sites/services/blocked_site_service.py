from sqlalchemy.orm import Session
from app.features.blocked_sites.schemas.blocked_site import BlockedSiteCreate
from app.features.blocked_sites.repositories.blocked_site_repository import BlockedSiteRepository
from app.features.blocked_sites.errors.blocked_site import BlockedSiteAlreadyExistsError, BlockedSiteNotFoundError
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


def create_blocked_site(blocked_site_data: BlockedSiteCreate, db: Session):
    repository = BlockedSiteRepository(db)
    try:
        logger.info("Creating blocked site", extra={"domain": blocked_site_data.domain})
        blocked_site = repository.create(blocked_site_data)
        logger.info("Blocked site created", extra={"blocked_site_id": getattr(blocked_site, "id", None), "domain": blocked_site.domain})
        return blocked_site
    except IntegrityError:
        logger.warning("Blocked site already exists", extra={"domain": blocked_site_data.domain})
        raise BlockedSiteAlreadyExistsError(blocked_site_data.domain)

def get_blocked_site_by_id(blocked_site_id: int, db: Session):
    repository = BlockedSiteRepository(db)
    try:
        blocked_site = repository.get_by_id(blocked_site_id)
        if blocked_site is None:
            logger.warning("Blocked site not found by id", extra={"blocked_site_id": blocked_site_id})
        else:
            logger.info("Fetched blocked site by id", extra={"blocked_site_id": blocked_site_id})
        return blocked_site
    except IntegrityError:
        logger.error("Integrity error while fetching blocked site by id", extra={"blocked_site_id": blocked_site_id}, exc_info=True)
        raise BlockedSiteNotFoundError(blocked_site_id)

def get_blocked_site_by_domain(blocked_site_domain: str, db: Session):
    repository = BlockedSiteRepository(db)
    try:
        blocked_site = repository.get_by_domain(blocked_site_domain)
        if blocked_site is None:
            logger.warning("Blocked site not found by domain", extra={"domain": blocked_site_domain})
        else:
            logger.info("Fetched blocked site by domain", extra={"domain": blocked_site_domain})
        return blocked_site
    except IntegrityError:
        logger.error("Integrity error while fetching blocked site by domain", extra={"domain": blocked_site_domain}, exc_info=True)
        raise BlockedSiteNotFoundError(blocked_site_domain)

def get_blocked_sites(db: Session, page: int = 1, page_size: int = 10, domain_search: str = None):
    repository = BlockedSiteRepository(db)
    try:
        skip = (page - 1) * page_size
        blocked_sites, total = repository.get_blocked_sites(skip=skip, limit=page_size, domain_search=domain_search)
        logger.info("Fetched blocked sites", extra={"count": len(blocked_sites), "total": total, "page": page, "page_size": page_size, "domain_search": domain_search})
        return blocked_sites, total
    except SQLAlchemyError as e:
        logger.error("Database error while listing blocked sites", exc_info=True)
        raise e 

def update_blocked_site(blocked_site_id: int, blocked_site_data: BlockedSiteCreate, db: Session):
    repository = BlockedSiteRepository(db)
    try:
        logger.info("Updating blocked site", extra={"blocked_site_id": blocked_site_id, "domain": blocked_site_data.domain})
        blocked_site = repository.update(blocked_site_id, blocked_site_data)
        if blocked_site is None:
            logger.warning("Blocked site not found for update", extra={"blocked_site_id": blocked_site_id})
            raise BlockedSiteNotFoundError(blocked_site_id)
        logger.info("Blocked site updated successfully", extra={"blocked_site_id": blocked_site_id, "domain": blocked_site.domain})
        return blocked_site
    except BlockedSiteNotFoundError:
        raise
    except IntegrityError:
        logger.warning("Blocked site with domain already exists", extra={"domain": blocked_site_data.domain})
        raise BlockedSiteAlreadyExistsError(blocked_site_data.domain)
    except SQLAlchemyError as e:
        logger.error("Database error while updating blocked site", extra={"blocked_site_id": blocked_site_id}, exc_info=True)
        raise e

def delete_blocked_site(blocked_site_id: int, db: Session):
    repository = BlockedSiteRepository(db)
    try:
        logger.info("Deleting blocked site", extra={"blocked_site_id": blocked_site_id})
        deleted = repository.delete(blocked_site_id)
        if not deleted:
            logger.warning("Blocked site not found for deletion", extra={"blocked_site_id": blocked_site_id})
            raise BlockedSiteNotFoundError(blocked_site_id)
        logger.info("Blocked site deleted successfully", extra={"blocked_site_id": blocked_site_id})
        return {"message": "Blocked site deleted successfully", "blocked_site_id": blocked_site_id}
    except BlockedSiteNotFoundError:
        raise
    except SQLAlchemyError as e:
        logger.error("Database error while deleting blocked site", extra={"blocked_site_id": blocked_site_id}, exc_info=True)
        raise e

def get_blocked_sites_counts_by_category(db: Session):
    repository = BlockedSiteRepository(db)
    try:
        counts = repository.get_counts_by_category()
        logger.info("Fetched blocked sites counts by category", extra={"categories_count": len(counts)})
        return counts
    except SQLAlchemyError as e:
        logger.error("Database error while fetching blocked sites counts by category", exc_info=True)
        raise e


