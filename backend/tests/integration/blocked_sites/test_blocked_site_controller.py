import pytest
from fastapi import HTTPException
from unittest.mock import Mock, patch
from app.features.blocked_sites.controllers.blocked_site_controller import (
    create_blocked_site_controller,
    get_blocked_site_by_id_controller,
    get_blocked_site_by_domain_controller,
    get_blocked_sites_controller,
    update_blocked_site_controller,
    delete_blocked_site_controller,
    get_blocked_sites_counts_by_category_controller,
)
from app.features.blocked_sites.schemas.blocked_site import BlockedSiteCreate
from app.features.blocked_sites.errors.blocked_site import (
    BlockedSiteAlreadyExistsError,
    BlockedSiteNotFoundError,
)


class TestBlockedSiteController:
    def test_create_blocked_site_controller_success(self, db_session, sample_blocked_site):
        create_data = BlockedSiteCreate(
            domain="newdomain.com",
            reason="New reason",
            category=None,
        )
        
        result = create_blocked_site_controller(create_data, db_session)
        
        assert result.id is not None
        assert result.domain == "newdomain.com"

    def test_create_blocked_site_controller_conflict(self, db_session, sample_blocked_site):
        create_data = BlockedSiteCreate(
            domain="example.com",
            reason="Duplicate",
            category=None,
        )
        
        with pytest.raises(HTTPException) as exc_info:
            create_blocked_site_controller(create_data, db_session)
        
        assert exc_info.value.status_code == 409
        assert "example.com" in str(exc_info.value.detail)

    def test_create_blocked_site_controller_generic_error(self, db_session):
        create_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.create_blocked_site', side_effect=ValueError("Invalid data")):
            with pytest.raises(HTTPException) as exc_info:
                create_blocked_site_controller(create_data, db_session)
            
            assert exc_info.value.status_code == 400

    def test_get_blocked_site_by_id_controller_success(self, db_session, sample_blocked_site):
        result = get_blocked_site_by_id_controller(sample_blocked_site.id, db_session)
        
        assert result.id == sample_blocked_site.id
        assert result.domain == sample_blocked_site.domain

    def test_get_blocked_site_by_id_controller_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            get_blocked_site_by_id_controller(999, db_session)
        
        assert exc_info.value.status_code == 404
        assert "999" in str(exc_info.value.detail)

    def test_get_blocked_site_by_id_controller_generic_error(self, db_session):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_site_by_id', side_effect=ValueError("Error")):
            with pytest.raises(HTTPException) as exc_info:
                get_blocked_site_by_id_controller(1, db_session)
            
            assert exc_info.value.status_code == 400

    def test_get_blocked_site_by_domain_controller_success(self, db_session, sample_blocked_site):
        result = get_blocked_site_by_domain_controller("example.com", db_session)
        
        assert result.domain == "example.com"

    def test_get_blocked_site_by_domain_controller_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            get_blocked_site_by_domain_controller("nonexistent.com", db_session)
        
        assert exc_info.value.status_code == 404

    def test_get_blocked_sites_controller_success(self, db_session, multiple_blocked_sites):
        result = get_blocked_sites_controller(db_session, page=1, page_size=10)
        
        assert result.total == 3
        assert len(result.items) == 3
        assert result.page == 1
        assert result.page_size == 10

    def test_get_blocked_sites_controller_with_pagination(self, db_session, multiple_blocked_sites):
        result = get_blocked_sites_controller(db_session, page=1, page_size=2)
        
        assert result.total == 3
        assert len(result.items) == 2
        assert result.page == 1
        assert result.page_size == 2

    def test_get_blocked_sites_controller_with_domain_search(self, db_session, multiple_blocked_sites):
        result = get_blocked_sites_controller(db_session, page=1, page_size=10, domain_search="example")
        
        assert result.total == 1
        assert len(result.items) == 1
        assert result.items[0].domain == "example.com"

    def test_get_blocked_sites_controller_handles_error(self, db_session):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_sites', side_effect=Exception("Error")):
            with pytest.raises(HTTPException) as exc_info:
                get_blocked_sites_controller(db_session)
            
            assert exc_info.value.status_code == 500

    def test_update_blocked_site_controller_success(self, db_session, sample_blocked_site):
        update_data = BlockedSiteCreate(
            domain="updated.com",
            reason="Updated reason",
            category="Updated",
        )
        
        result = update_blocked_site_controller(sample_blocked_site.id, update_data, db_session)
        
        assert result.domain == "updated.com"
        assert result.reason == "Updated reason"

    def test_update_blocked_site_controller_not_found(self, db_session):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        with pytest.raises(HTTPException) as exc_info:
            update_blocked_site_controller(999, update_data, db_session)
        
        assert exc_info.value.status_code == 404

    def test_update_blocked_site_controller_conflict(self, db_session, multiple_blocked_sites):
        update_data = BlockedSiteCreate(
            domain="test.com",
            reason="test",
            category=None,
        )
        
        with pytest.raises(HTTPException) as exc_info:
            update_blocked_site_controller(multiple_blocked_sites[0].id, update_data, db_session)
        
        assert exc_info.value.status_code == 409

    def test_update_blocked_site_controller_generic_error(self, db_session, sample_blocked_site):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.update_blocked_site', side_effect=ValueError("Error")):
            with pytest.raises(HTTPException) as exc_info:
                update_blocked_site_controller(sample_blocked_site.id, update_data, db_session)
            
            assert exc_info.value.status_code == 400

    def test_delete_blocked_site_controller_success(self, db_session, sample_blocked_site):
        result = delete_blocked_site_controller(sample_blocked_site.id, db_session)
        
        assert result["message"] == "Blocked site deleted successfully"
        assert result["blocked_site_id"] == sample_blocked_site.id

    def test_delete_blocked_site_controller_not_found(self, db_session):
        with pytest.raises(HTTPException) as exc_info:
            delete_blocked_site_controller(999, db_session)
        
        assert exc_info.value.status_code == 404

    def test_delete_blocked_site_controller_handles_error(self, db_session, sample_blocked_site):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.delete_blocked_site', side_effect=Exception("Error")):
            with pytest.raises(HTTPException) as exc_info:
                delete_blocked_site_controller(sample_blocked_site.id, db_session)
            
            assert exc_info.value.status_code == 500

    def test_get_blocked_sites_counts_by_category_controller_success(self, db_session, multiple_blocked_sites):
        result = get_blocked_sites_counts_by_category_controller(db_session)
        
        assert isinstance(result.counts, dict)
        assert "Malware" in result.counts
        assert "Phishing" in result.counts
        assert result.counts["Malware"] == 1

    def test_get_blocked_sites_counts_by_category_controller_handles_error(self, db_session):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_sites_counts_by_category', side_effect=Exception("Error")):
            with pytest.raises(HTTPException) as exc_info:
                get_blocked_sites_counts_by_category_controller(db_session)
            
            assert exc_info.value.status_code == 500

