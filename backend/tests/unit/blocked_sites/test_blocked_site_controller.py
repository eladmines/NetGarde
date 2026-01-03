import pytest
from unittest.mock import Mock, patch
from fastapi import HTTPException
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
    @pytest.fixture
    def mock_db_session(self):
        return Mock()

    @pytest.fixture
    def mock_blocked_site(self):
        mock = Mock()
        mock.id = 1
        mock.domain = "example.com"
        mock.reason = "Test reason"
        return mock

    def test_create_blocked_site_controller_success(self, mock_db_session, mock_blocked_site):
        create_data = BlockedSiteCreate(
            domain="newdomain.com",
            reason="New reason",
            category=None,
        )
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.create_blocked_site', return_value=mock_blocked_site):
            result = create_blocked_site_controller(create_data, mock_db_session)
        
        assert result.id == 1
        assert result.domain == "example.com"

    def test_create_blocked_site_controller_conflict(self, mock_db_session):
        create_data = BlockedSiteCreate(
            domain="example.com",
            reason="Duplicate",
            category=None,
        )
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.create_blocked_site', side_effect=BlockedSiteAlreadyExistsError("example.com")):
            with pytest.raises(HTTPException) as exc_info:
                create_blocked_site_controller(create_data, mock_db_session)
        
        assert exc_info.value.status_code == 409
        assert "example.com" in str(exc_info.value.detail)

    def test_create_blocked_site_controller_generic_error(self, mock_db_session):
        create_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.create_blocked_site', side_effect=ValueError("Invalid data")):
            with pytest.raises(HTTPException) as exc_info:
                create_blocked_site_controller(create_data, mock_db_session)
            
            assert exc_info.value.status_code == 400

    def test_get_blocked_site_by_id_controller_success(self, mock_db_session, mock_blocked_site):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_site_by_id', return_value=mock_blocked_site):
            result = get_blocked_site_by_id_controller(1, mock_db_session)
        
        assert result.id == 1
        assert result.domain == "example.com"

    def test_get_blocked_site_by_id_controller_not_found(self, mock_db_session):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_site_by_id', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                get_blocked_site_by_id_controller(999, mock_db_session)
        
        assert exc_info.value.status_code == 404
        assert "999" in str(exc_info.value.detail)

    def test_get_blocked_site_by_id_controller_generic_error(self, mock_db_session):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_site_by_id', side_effect=ValueError("Error")):
            with pytest.raises(HTTPException) as exc_info:
                get_blocked_site_by_id_controller(1, mock_db_session)
            
            assert exc_info.value.status_code == 400

    def test_get_blocked_site_by_domain_controller_success(self, mock_db_session, mock_blocked_site):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_site_by_domain', return_value=mock_blocked_site):
            result = get_blocked_site_by_domain_controller("example.com", mock_db_session)
        
        assert result.domain == "example.com"

    def test_get_blocked_site_by_domain_controller_not_found(self, mock_db_session):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_site_by_domain', return_value=None):
            with pytest.raises(HTTPException) as exc_info:
                get_blocked_site_by_domain_controller("nonexistent.com", mock_db_session)
        
        assert exc_info.value.status_code == 404

    def test_get_blocked_sites_controller_success(self, mock_db_session):
        mock_sites = [Mock(), Mock(), Mock()]
        mock_paginated_response = Mock()
        mock_paginated_response.total = 3
        mock_paginated_response.items = mock_sites
        mock_paginated_response.page = 1
        mock_paginated_response.page_size = 10
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_sites', return_value=(mock_sites, 3)):
            with patch('app.features.blocked_sites.controllers.blocked_site_controller.PaginatedResponse') as mock_paginated:
                mock_paginated.create.return_value = mock_paginated_response
                result = get_blocked_sites_controller(mock_db_session, page=1, page_size=10)
        
        assert result.total == 3
        assert len(result.items) == 3

    def test_get_blocked_sites_controller_handles_error(self, mock_db_session):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_sites', side_effect=Exception("Error")):
            with pytest.raises(HTTPException) as exc_info:
                get_blocked_sites_controller(mock_db_session)
            
            assert exc_info.value.status_code == 500

    def test_update_blocked_site_controller_success(self, mock_db_session, mock_blocked_site):
        update_data = BlockedSiteCreate(
            domain="updated.com",
            reason="Updated reason",
            category="Updated",
        )
        mock_blocked_site.domain = "updated.com"
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.update_blocked_site', return_value=mock_blocked_site):
            result = update_blocked_site_controller(1, update_data, mock_db_session)
        
        assert result.domain == "updated.com"

    def test_update_blocked_site_controller_not_found(self, mock_db_session):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.update_blocked_site', side_effect=BlockedSiteNotFoundError(999)):
            with pytest.raises(HTTPException) as exc_info:
                update_blocked_site_controller(999, update_data, mock_db_session)
        
        assert exc_info.value.status_code == 404

    def test_update_blocked_site_controller_conflict(self, mock_db_session):
        update_data = BlockedSiteCreate(
            domain="test.com",
            reason="test",
            category=None,
        )
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.update_blocked_site', side_effect=BlockedSiteAlreadyExistsError("test.com")):
            with pytest.raises(HTTPException) as exc_info:
                update_blocked_site_controller(1, update_data, mock_db_session)
        
        assert exc_info.value.status_code == 409

    def test_update_blocked_site_controller_generic_error(self, mock_db_session):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.update_blocked_site', side_effect=ValueError("Error")):
            with pytest.raises(HTTPException) as exc_info:
                update_blocked_site_controller(1, update_data, mock_db_session)
            
            assert exc_info.value.status_code == 400

    def test_delete_blocked_site_controller_success(self, mock_db_session):
        mock_result = {"message": "Blocked site deleted successfully", "blocked_site_id": 1}
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.delete_blocked_site', return_value=mock_result):
            result = delete_blocked_site_controller(1, mock_db_session)
        
        assert result["message"] == "Blocked site deleted successfully"
        assert result["blocked_site_id"] == 1

    def test_delete_blocked_site_controller_not_found(self, mock_db_session):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.delete_blocked_site', side_effect=BlockedSiteNotFoundError(999)):
            with pytest.raises(HTTPException) as exc_info:
                delete_blocked_site_controller(999, mock_db_session)
        
        assert exc_info.value.status_code == 404

    def test_delete_blocked_site_controller_handles_error(self, mock_db_session):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.delete_blocked_site', side_effect=Exception("Error")):
            with pytest.raises(HTTPException) as exc_info:
                delete_blocked_site_controller(1, mock_db_session)
            
            assert exc_info.value.status_code == 500

    def test_get_blocked_sites_counts_by_category_controller_success(self, mock_db_session):
        mock_counts = {"Malware": 5, "Phishing": 3}
        mock_response = Mock()
        mock_response.counts = mock_counts
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_sites_counts_by_category', return_value=mock_counts):
            with patch('app.features.blocked_sites.controllers.blocked_site_controller.CategoryCountsResponse', return_value=mock_response):
                result = get_blocked_sites_counts_by_category_controller(mock_db_session)
        
        assert result.counts["Malware"] == 5

    def test_get_blocked_sites_counts_by_category_controller_handles_error(self, mock_db_session):
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.get_blocked_sites_counts_by_category', side_effect=Exception("Error")):
            with pytest.raises(HTTPException) as exc_info:
                get_blocked_sites_counts_by_category_controller(mock_db_session)
            
            assert exc_info.value.status_code == 500
