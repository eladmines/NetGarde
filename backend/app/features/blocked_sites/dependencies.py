from app.features.blocked_sites.services.blocked_site_service import BlockedSiteService
from app.features.blocked_sites.services.blocked_site_service_interface import IBlockedSiteService


def get_blocked_site_service() -> IBlockedSiteService:
    """Dependency to get BlockedSiteService instance."""
    return BlockedSiteService()

