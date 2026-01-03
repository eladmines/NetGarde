import pytest
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
from unittest.mock import Mock, patch
from app.features.blocked_sites.services.blocked_site_service import (
    create_blocked_site,
    get_blocked_site_by_id,
    get_blocked_site_by_domain,
    get_blocked_sites,
    update_blocked_site,
    delete_blocked_site,
    get_blocked_sites_counts_by_category,
)
from app.features.blocked_sites.schemas.blocked_site import BlockedSiteCreate
from app.features.blocked_sites.errors.blocked_site import (
    BlockedSiteAlreadyExistsError,
    BlockedSiteNotFoundError,
)
from app.features.blocked_sites.repositories.blocked_site_repository import BlockedSiteRepository


class TestBlockedSiteService:
    def test_create_blocked_site_success(self, db_session, sample_blocked_site_data):
        create_data = BlockedSiteCreate(**sample_blocked_site_data)
        
        result = create_blocked_site(create_data, db_session)
        
        assert result.id is not None
        assert result.domain == "example.com"
        assert result.reason == "Test reason"

    def test_create_blocked_site_duplicate_domain(self, db_session, sample_blocked_site):
        create_data = BlockedSiteCreate(
            domain="example.com",
            reason="Another reason",
            category=None,
        )
        
        with pytest.raises(BlockedSiteAlreadyExistsError) as exc_info:
            create_blocked_site(create_data, db_session)
        
        assert "example.com" in str(exc_info.value)

    def test_get_blocked_site_by_id_success(self, db_session, sample_blocked_site):
        result = get_blocked_site_by_id(sample_blocked_site.id, db_session)
        
        assert result is not None
        assert result.id == sample_blocked_site.id
        assert result.domain == sample_blocked_site.domain

    def test_get_blocked_site_by_id_not_found(self, db_session):
        result = get_blocked_site_by_id(999, db_session)
        
        assert result is None

    def test_get_blocked_site_by_domain_success(self, db_session, sample_blocked_site):
        result = get_blocked_site_by_domain("example.com", db_session)
        
        assert result is not None
        assert result.domain == "example.com"

    def test_get_blocked_site_by_domain_not_found(self, db_session):
        result = get_blocked_site_by_domain("nonexistent.com", db_session)
        
        assert result is None

    def test_get_blocked_sites_default_pagination(self, db_session, multiple_blocked_sites):
        sites, total = get_blocked_sites(db_session)
        
        assert len(sites) == 3
        assert total == 3

    def test_get_blocked_sites_with_pagination(self, db_session, multiple_blocked_sites):
        sites, total = get_blocked_sites(db_session, page=1, page_size=2)
        
        assert len(sites) == 2
        assert total == 3

    def test_get_blocked_sites_with_domain_search(self, db_session, multiple_blocked_sites):
        sites, total = get_blocked_sites(db_session, domain_search="example")
        
        assert len(sites) == 1
        assert total == 1
        assert sites[0].domain == "example.com"

    def test_get_blocked_sites_handles_database_error(self, db_session):
        with patch.object(BlockedSiteRepository, 'get_blocked_sites', side_effect=SQLAlchemyError("DB Error")):
            with pytest.raises(SQLAlchemyError):
                get_blocked_sites(db_session)

    def test_update_blocked_site_success(self, db_session, sample_blocked_site):
        update_data = BlockedSiteCreate(
            domain="updated.com",
            reason="Updated reason",
            category="Updated Category",
        )
        
        result = update_blocked_site(sample_blocked_site.id, update_data, db_session)
        
        assert result is not None
        assert result.domain == "updated.com"
        assert result.reason == "Updated reason"

    def test_update_blocked_site_not_found(self, db_session):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        with pytest.raises(BlockedSiteNotFoundError) as exc_info:
            update_blocked_site(999, update_data, db_session)
        
        assert "999" in str(exc_info.value)

    def test_update_blocked_site_duplicate_domain(self, db_session, multiple_blocked_sites):
        update_data = BlockedSiteCreate(
            domain="test.com",
            reason="test",
            category=None,
        )
        
        with pytest.raises(BlockedSiteAlreadyExistsError) as exc_info:
            update_blocked_site(multiple_blocked_sites[0].id, update_data, db_session)
        
        assert "test.com" in str(exc_info.value)

    def test_update_blocked_site_handles_database_error(self, db_session, sample_blocked_site):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        with patch.object(BlockedSiteRepository, 'update', side_effect=SQLAlchemyError("DB Error")):
            with pytest.raises(SQLAlchemyError):
                update_blocked_site(sample_blocked_site.id, update_data, db_session)

    def test_delete_blocked_site_success(self, db_session, sample_blocked_site):
        result = delete_blocked_site(sample_blocked_site.id, db_session)
        
        assert result["message"] == "Blocked site deleted successfully"
        assert result["blocked_site_id"] == sample_blocked_site.id

    def test_delete_blocked_site_not_found(self, db_session):
        with pytest.raises(BlockedSiteNotFoundError) as exc_info:
            delete_blocked_site(999, db_session)
        
        assert "999" in str(exc_info.value)

    def test_delete_blocked_site_handles_database_error(self, db_session, sample_blocked_site):
        with patch.object(BlockedSiteRepository, 'delete', side_effect=SQLAlchemyError("DB Error")):
            with pytest.raises(SQLAlchemyError):
                delete_blocked_site(sample_blocked_site.id, db_session)

    def test_get_blocked_sites_counts_by_category(self, db_session, multiple_blocked_sites):
        counts = get_blocked_sites_counts_by_category(db_session)
        
        assert isinstance(counts, dict)
        assert "Malware" in counts
        assert "Phishing" in counts
        assert counts["Malware"] == 1
        assert counts["Phishing"] == 1

    def test_get_blocked_sites_counts_by_category_handles_database_error(self, db_session):
        with patch.object(BlockedSiteRepository, 'get_counts_by_category', side_effect=SQLAlchemyError("DB Error")):
            with pytest.raises(SQLAlchemyError):
                get_blocked_sites_counts_by_category(db_session)

