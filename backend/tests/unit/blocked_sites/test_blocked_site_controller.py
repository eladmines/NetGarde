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
    def mock_service(self):
        """Mock service implementing IBlockedSiteService protocol."""
        return Mock()

    @pytest.fixture
    def mock_blocked_site(self):
        mock = Mock()
        mock.id = 1
        mock.domain = "example.com"
        mock.reason = "Test reason"
        return mock

    def test_create_blocked_site_controller_success(self, mock_db_session, mock_service, mock_blocked_site):
        create_data = BlockedSiteCreate(
            domain="newdomain.com",
            reason="New reason",
            category=None,
        )
        
        mock_service.create_blocked_site.return_value = mock_blocked_site
        
        result = create_blocked_site_controller(create_data, mock_db_session, mock_service)
        
        assert result.id == 1
        assert result.domain == "example.com"
        mock_service.create_blocked_site.assert_called_once_with(create_data, mock_db_session)

    def test_create_blocked_site_controller_conflict(self, mock_db_session, mock_service):
        create_data = BlockedSiteCreate(
            domain="example.com",
            reason="Duplicate",
            category=None,
        )
        
        mock_service.create_blocked_site.side_effect = BlockedSiteAlreadyExistsError("example.com")
        
        with pytest.raises(HTTPException) as exc_info:
            create_blocked_site_controller(create_data, mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 409
        assert "example.com" in str(exc_info.value.detail)

    def test_create_blocked_site_controller_generic_error(self, mock_db_session, mock_service):
        create_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        mock_service.create_blocked_site.side_effect = ValueError("Invalid data")
        
        with pytest.raises(HTTPException) as exc_info:
            create_blocked_site_controller(create_data, mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 400

    def test_get_blocked_site_by_id_controller_success(self, mock_db_session, mock_service, mock_blocked_site):
        mock_service.get_blocked_site_by_id.return_value = mock_blocked_site
        
        result = get_blocked_site_by_id_controller(1, mock_db_session, mock_service)
        
        assert result.id == 1
        assert result.domain == "example.com"
        mock_service.get_blocked_site_by_id.assert_called_once_with(1, mock_db_session)

    def test_get_blocked_site_by_id_controller_not_found(self, mock_db_session, mock_service):
        mock_service.get_blocked_site_by_id.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_blocked_site_by_id_controller(999, mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 404
        assert "999" in str(exc_info.value.detail)
        mock_service.get_blocked_site_by_id.assert_called_once_with(999, mock_db_session)

    def test_get_blocked_site_by_id_controller_generic_error(self, mock_db_session, mock_service):
        mock_service.get_blocked_site_by_id.side_effect = ValueError("Error")
        
        with pytest.raises(HTTPException) as exc_info:
            get_blocked_site_by_id_controller(1, mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 400

    def test_get_blocked_site_by_domain_controller_success(self, mock_db_session, mock_service, mock_blocked_site):
        mock_service.get_blocked_site_by_domain.return_value = mock_blocked_site
        
        result = get_blocked_site_by_domain_controller("example.com", mock_db_session, mock_service)
        
        assert result.domain == "example.com"
        mock_service.get_blocked_site_by_domain.assert_called_once_with("example.com", mock_db_session)

    def test_get_blocked_site_by_domain_controller_not_found(self, mock_db_session, mock_service):
        mock_service.get_blocked_site_by_domain.return_value = None
        
        with pytest.raises(HTTPException) as exc_info:
            get_blocked_site_by_domain_controller("nonexistent.com", mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 404
        mock_service.get_blocked_site_by_domain.assert_called_once_with("nonexistent.com", mock_db_session)

    def test_get_blocked_sites_controller_success(self, mock_db_session, mock_service):
        mock_sites = [Mock(), Mock(), Mock()]
        mock_paginated_response = Mock()
        mock_paginated_response.total = 3
        mock_paginated_response.items = mock_sites
        mock_paginated_response.page = 1
        mock_paginated_response.page_size = 10
        mock_paginated_response.total_pages = 1
        
        mock_service.get_blocked_sites.return_value = (mock_sites, 3)
        
        mock_param_type = Mock()
        mock_param_type.create = Mock(return_value=mock_paginated_response)
        
        with patch('app.features.blocked_sites.controllers.blocked_site_controller.PaginatedResponse') as mock_paginated:
            mock_paginated.__getitem__ = Mock(return_value=mock_param_type)
            result = get_blocked_sites_controller(mock_db_session, mock_service, page=1, page_size=10)
        
        assert result.total == 3
        assert len(result.items) == 3
        assert result.page == 1
        assert result.page_size == 10
        assert result.total_pages == 1
        mock_service.get_blocked_sites.assert_called_once_with(mock_db_session, page=1, page_size=10, domain_search=None)

    def test_get_blocked_sites_controller_handles_error(self, mock_db_session, mock_service):
        mock_service.get_blocked_sites.side_effect = Exception("Error")
        
        with pytest.raises(HTTPException) as exc_info:
            get_blocked_sites_controller(mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 500

    def test_update_blocked_site_controller_success(self, mock_db_session, mock_service, mock_blocked_site):
        update_data = BlockedSiteCreate(
            domain="updated.com",
            reason="Updated reason",
            category="Updated",
        )
        mock_blocked_site.domain = "updated.com"
        mock_service.update_blocked_site.return_value = mock_blocked_site
        
        result = update_blocked_site_controller(1, update_data, mock_db_session, mock_service)
        
        assert result.domain == "updated.com"
        mock_service.update_blocked_site.assert_called_once_with(1, update_data, mock_db_session)

    def test_update_blocked_site_controller_not_found(self, mock_db_session, mock_service):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        mock_service.update_blocked_site.side_effect = BlockedSiteNotFoundError(999)
        
        with pytest.raises(HTTPException) as exc_info:
            update_blocked_site_controller(999, update_data, mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 404

    def test_update_blocked_site_controller_conflict(self, mock_db_session, mock_service):
        update_data = BlockedSiteCreate(
            domain="test.com",
            reason="test",
            category=None,
        )
        
        mock_service.update_blocked_site.side_effect = BlockedSiteAlreadyExistsError("test.com")
        
        with pytest.raises(HTTPException) as exc_info:
            update_blocked_site_controller(1, update_data, mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 409

    def test_update_blocked_site_controller_generic_error(self, mock_db_session, mock_service):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        mock_service.update_blocked_site.side_effect = ValueError("Error")
        
        with pytest.raises(HTTPException) as exc_info:
            update_blocked_site_controller(1, update_data, mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 400

    def test_delete_blocked_site_controller_success(self, mock_db_session, mock_service):
        mock_result = {"message": "Blocked site deleted successfully", "blocked_site_id": 1}
        mock_service.delete_blocked_site.return_value = mock_result
        
        result = delete_blocked_site_controller(1, mock_db_session, mock_service)
        
        assert result["message"] == "Blocked site deleted successfully"
        assert result["blocked_site_id"] == 1
        mock_service.delete_blocked_site.assert_called_once_with(1, mock_db_session)

    def test_delete_blocked_site_controller_not_found(self, mock_db_session, mock_service):
        mock_service.delete_blocked_site.side_effect = BlockedSiteNotFoundError(999)
        
        with pytest.raises(HTTPException) as exc_info:
            delete_blocked_site_controller(999, mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 404

    def test_delete_blocked_site_controller_handles_error(self, mock_db_session, mock_service):
        mock_service.delete_blocked_site.side_effect = Exception("Error")
        
        with pytest.raises(HTTPException) as exc_info:
            delete_blocked_site_controller(1, mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 500

    def test_get_blocked_sites_counts_by_category_controller_success(self, mock_db_session, mock_service):
        from app.features.blocked_sites.schemas.blocked_site import CategoryCountsResponse
        
        mock_counts = {"Malware": 5, "Phishing": 3}
        
        mock_service.get_blocked_sites_counts_by_category.return_value = mock_counts
        
        result = get_blocked_sites_counts_by_category_controller(mock_db_session, mock_service)
        
        assert isinstance(result, CategoryCountsResponse)
        assert result.counts["Malware"] == 5
        assert result.counts["Phishing"] == 3
        mock_service.get_blocked_sites_counts_by_category.assert_called_once_with(mock_db_session)

    def test_get_blocked_sites_counts_by_category_controller_handles_error(self, mock_db_session, mock_service):
        mock_service.get_blocked_sites_counts_by_category.side_effect = Exception("Error")
        
        with pytest.raises(HTTPException) as exc_info:
            get_blocked_sites_counts_by_category_controller(mock_db_session, mock_service)
        
        assert exc_info.value.status_code == 500
