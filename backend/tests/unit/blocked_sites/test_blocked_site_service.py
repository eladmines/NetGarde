import pytest
from unittest.mock import Mock, patch, MagicMock
from sqlalchemy.exc import IntegrityError, SQLAlchemyError
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


class TestBlockedSiteService:
    @pytest.fixture
    def mock_db_session(self):
        return Mock()

    @pytest.fixture
    def mock_repository(self):
        return Mock()

    @pytest.fixture
    def sample_blocked_site_data(self):
        return {
            "domain": "example.com",
            "reason": "Test reason",
            "category": "Malware",
        }

    @pytest.fixture
    def mock_blocked_site(self):
        mock = Mock()
        mock.id = 1
        mock.domain = "example.com"
        mock.reason = "Test reason"
        mock.category = "Malware"
        return mock

    def test_create_blocked_site_success(self, mock_db_session, mock_repository, sample_blocked_site_data, mock_blocked_site):
        create_data = BlockedSiteCreate(**sample_blocked_site_data)
        mock_repository.create.return_value = mock_blocked_site
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            result = create_blocked_site(create_data, mock_db_session)
        
        assert result.id == 1
        assert result.domain == "example.com"
        mock_repository.create.assert_called_once_with(create_data)

    def test_create_blocked_site_duplicate_domain(self, mock_db_session, mock_repository, sample_blocked_site_data):
        create_data = BlockedSiteCreate(**sample_blocked_site_data)
        mock_repository.create.side_effect = IntegrityError("", "", "")
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            with pytest.raises(BlockedSiteAlreadyExistsError) as exc_info:
                create_blocked_site(create_data, mock_db_session)
        
        assert "example.com" in str(exc_info.value)

    def test_get_blocked_site_by_id_success(self, mock_db_session, mock_repository, mock_blocked_site):
        mock_repository.get_by_id.return_value = mock_blocked_site
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            result = get_blocked_site_by_id(1, mock_db_session)
        
        assert result.id == 1
        assert result.domain == "example.com"
        mock_repository.get_by_id.assert_called_once_with(1)

    def test_get_blocked_site_by_id_not_found(self, mock_db_session, mock_repository):
        mock_repository.get_by_id.return_value = None
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            result = get_blocked_site_by_id(999, mock_db_session)
        
        assert result is None
        mock_repository.get_by_id.assert_called_once_with(999)

    def test_get_blocked_site_by_domain_success(self, mock_db_session, mock_repository, mock_blocked_site):
        mock_repository.get_by_domain.return_value = mock_blocked_site
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            result = get_blocked_site_by_domain("example.com", mock_db_session)
        
        assert result.domain == "example.com"
        mock_repository.get_by_domain.assert_called_once_with("example.com")

    def test_get_blocked_site_by_domain_not_found(self, mock_db_session, mock_repository):
        mock_repository.get_by_domain.return_value = None
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            result = get_blocked_site_by_domain("nonexistent.com", mock_db_session)
        
        assert result is None

    def test_get_blocked_sites_default_pagination(self, mock_db_session, mock_repository):
        mock_sites = [Mock(), Mock(), Mock()]
        mock_repository.get_blocked_sites.return_value = (mock_sites, 3)
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            sites, total = get_blocked_sites(mock_db_session)
        
        assert len(sites) == 3
        assert total == 3
        mock_repository.get_blocked_sites.assert_called_once_with(skip=0, limit=10, domain_search=None)

    def test_get_blocked_sites_with_pagination(self, mock_db_session, mock_repository):
        mock_sites = [Mock(), Mock()]
        mock_repository.get_blocked_sites.return_value = (mock_sites, 3)
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            sites, total = get_blocked_sites(mock_db_session, page=1, page_size=2)
        
        assert len(sites) == 2
        assert total == 3
        mock_repository.get_blocked_sites.assert_called_once_with(skip=0, limit=2, domain_search=None)

    def test_get_blocked_sites_with_domain_search(self, mock_db_session, mock_repository):
        mock_site = Mock()
        mock_site.domain = "example.com"
        mock_repository.get_blocked_sites.return_value = ([mock_site], 1)
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            sites, total = get_blocked_sites(mock_db_session, domain_search="example")
        
        assert len(sites) == 1
        assert total == 1
        mock_repository.get_blocked_sites.assert_called_once_with(skip=0, limit=10, domain_search="example")

    def test_get_blocked_sites_handles_database_error(self, mock_db_session, mock_repository):
        mock_repository.get_blocked_sites.side_effect = SQLAlchemyError("DB Error")
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            with pytest.raises(SQLAlchemyError):
                get_blocked_sites(mock_db_session)

    def test_update_blocked_site_success(self, mock_db_session, mock_repository, mock_blocked_site):
        update_data = BlockedSiteCreate(
            domain="updated.com",
            reason="Updated reason",
            category="Updated Category",
        )
        mock_blocked_site.domain = "updated.com"
        mock_repository.update.return_value = mock_blocked_site
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            result = update_blocked_site(1, update_data, mock_db_session)
        
        assert result.domain == "updated.com"
        mock_repository.update.assert_called_once_with(1, update_data)

    def test_update_blocked_site_not_found(self, mock_db_session, mock_repository):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        mock_repository.update.return_value = None
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            with pytest.raises(BlockedSiteNotFoundError) as exc_info:
                update_blocked_site(999, update_data, mock_db_session)
        
        assert "999" in str(exc_info.value)

    def test_update_blocked_site_duplicate_domain(self, mock_db_session, mock_repository):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        mock_repository.update.side_effect = IntegrityError("", "", "")
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            with pytest.raises(BlockedSiteAlreadyExistsError) as exc_info:
                update_blocked_site(1, update_data, mock_db_session)
        
        assert "test.com" in str(exc_info.value)

    def test_update_blocked_site_handles_database_error(self, mock_db_session, mock_repository):
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        mock_repository.update.side_effect = SQLAlchemyError("DB Error")
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            with pytest.raises(SQLAlchemyError):
                update_blocked_site(1, update_data, mock_db_session)

    def test_delete_blocked_site_success(self, mock_db_session, mock_repository):
        mock_repository.delete.return_value = True
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            result = delete_blocked_site(1, mock_db_session)
        
        assert result["message"] == "Blocked site deleted successfully"
        assert result["blocked_site_id"] == 1
        mock_repository.delete.assert_called_once_with(1)

    def test_delete_blocked_site_not_found(self, mock_db_session, mock_repository):
        mock_repository.delete.return_value = False
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            with pytest.raises(BlockedSiteNotFoundError) as exc_info:
                delete_blocked_site(999, mock_db_session)
        
        assert "999" in str(exc_info.value)

    def test_delete_blocked_site_handles_database_error(self, mock_db_session, mock_repository):
        mock_repository.delete.side_effect = SQLAlchemyError("DB Error")
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            with pytest.raises(SQLAlchemyError):
                delete_blocked_site(1, mock_db_session)

    def test_get_blocked_sites_counts_by_category(self, mock_db_session, mock_repository):
        mock_counts = {"Malware": 5, "Phishing": 3}
        mock_repository.get_counts_by_category.return_value = mock_counts
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            counts = get_blocked_sites_counts_by_category(mock_db_session)
        
        assert counts["Malware"] == 5
        assert counts["Phishing"] == 3
        mock_repository.get_counts_by_category.assert_called_once()

    def test_get_blocked_sites_counts_by_category_handles_database_error(self, mock_db_session, mock_repository):
        mock_repository.get_counts_by_category.side_effect = SQLAlchemyError("DB Error")
        
        with patch('app.features.blocked_sites.services.blocked_site_service.BlockedSiteRepository', return_value=mock_repository):
            with pytest.raises(SQLAlchemyError):
                get_blocked_sites_counts_by_category(mock_db_session)
