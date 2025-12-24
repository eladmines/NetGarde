from typing import Optional, List, Dict
from sqlalchemy.orm import Session
from sqlalchemy import func
from datetime import datetime
from app.features.blocked_sites.models.blocked_site import BlockedSite
from app.features.blocked_sites.schemas.blocked_site import BlockedSiteCreate


class BlockedSiteRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: BlockedSiteCreate) -> BlockedSite:
        blocked_site_data = data.model_dump()
        # Set mock user_id values if not provided
        if blocked_site_data.get('created_by') is None:
            blocked_site_data['created_by'] = 1  # Mock user_id
        if blocked_site_data.get('updated_by') is None:
            blocked_site_data['updated_by'] = blocked_site_data.get('created_by', 1)  # Mock user_id
        new_blocked_site = BlockedSite(**blocked_site_data)
        self.db.add(new_blocked_site)
        self.db.commit()
        self.db.refresh(new_blocked_site)
        return new_blocked_site

    def get_by_id(self, blocked_site_id: int) -> Optional[BlockedSite]:
        return (
            self.db.query(BlockedSite)
            .filter(BlockedSite.id == blocked_site_id, BlockedSite.is_deleted == False)
            .first()
        )

    def get_by_domain(self, domain: str) -> Optional[BlockedSite]:
        return (
            self.db.query(BlockedSite)
            .filter(BlockedSite.domain == domain, BlockedSite.is_deleted == False)
            .first()
        )

    def get_blocked_sites(self, skip: int = 0, limit: int = None, domain_search: Optional[str] = None) -> tuple[List[BlockedSite], int]:
        """
        Get blocked sites with pagination support.
        
        Args:
            skip: Number of records to skip
            limit: Maximum number of records to return
            domain_search: Optional domain search query (case-insensitive partial match)
            
        Returns:
            Tuple of (list of blocked sites, total count)
        """
        query = self.db.query(BlockedSite).filter(BlockedSite.is_deleted == False)
        
        # Apply domain search filter if provided
        if domain_search and domain_search.strip():
            domain_search_lower = domain_search.strip().lower()
            query = query.filter(BlockedSite.domain.ilike(f"%{domain_search_lower}%"))
        
        # Get total count before pagination
        total = query.count()
        
        # Apply pagination
        if limit is not None:
            query = query.offset(skip).limit(limit)
        
        return query.all(), total

    def update(self, blocked_site_id: int, data: BlockedSiteCreate) -> Optional[BlockedSite]:
        blocked_site = self.db.query(BlockedSite).filter(BlockedSite.id == blocked_site_id, BlockedSite.is_deleted == False).first()
        if not blocked_site:
            return None
        
        blocked_site.domain = data.domain
        blocked_site.reason = data.reason
        blocked_site.category = data.category
        # Set mock user_id if not provided
        blocked_site.updated_by = data.updated_by if data.updated_by is not None else 1  # Mock user_id
        blocked_site.updated_at = datetime.now()
        self.db.commit()
        self.db.refresh(blocked_site)
        return blocked_site

    def delete(self, blocked_site_id: int) -> bool:
        blocked_site = self.db.query(BlockedSite).filter(BlockedSite.id == blocked_site_id, BlockedSite.is_deleted == False).first()
        if not blocked_site:
            return False
        blocked_site.is_deleted = True
        blocked_site.updated_at = datetime.now()
        self.db.commit()
        return True

    def get_counts_by_category(self) -> Dict[str, int]:
        """
        Get count of blocked sites grouped by category.
        
        Returns:
            Dictionary mapping category names to counts
        """
        results = (
            self.db.query(
                BlockedSite.category,
                func.count(BlockedSite.id).label('count')
            )
            .filter(BlockedSite.is_deleted == False, BlockedSite.category.isnot(None))
            .group_by(BlockedSite.category)
            .all()
        )
        
        # Convert results to dictionary: {category_name: count}
        counts = {category: count for category, count in results}
        return counts

    

    

