from typing import Protocol, Optional, Tuple, Dict, List
from sqlalchemy.orm import Session
from app.features.blocked_sites.schemas.blocked_site import BlockedSiteCreate
from app.features.blocked_sites.models.blocked_site import BlockedSite


class IBlockedSiteService(Protocol):
    """Protocol defining the blocked site service interface."""
    
    def create_blocked_site(self, blocked_site_data: BlockedSiteCreate, db: Session) -> BlockedSite:
        """Create a new blocked site."""
        ...
    
    def get_blocked_site_by_id(self, blocked_site_id: int, db: Session) -> Optional[BlockedSite]:
        """Get a blocked site by ID."""
        ...
    
    def get_blocked_site_by_domain(self, domain: str, db: Session) -> Optional[BlockedSite]:
        """Get a blocked site by domain."""
        ...
    
    def get_blocked_sites(self, db: Session, page: int = 1, page_size: int = 10, domain_search: Optional[str] = None) -> Tuple[List[BlockedSite], int]:
        """Get paginated list of blocked sites."""
        ...
    
    def update_blocked_site(self, blocked_site_id: int, blocked_site_data: BlockedSiteCreate, db: Session) -> BlockedSite:
        """Update a blocked site."""
        ...
    
    def delete_blocked_site(self, blocked_site_id: int, db: Session) -> Dict[str, any]:
        """Delete a blocked site."""
        ...
    
    def get_blocked_sites_counts_by_category(self, db: Session) -> Dict[str, int]:
        """Get counts of blocked sites by category."""
        ...

