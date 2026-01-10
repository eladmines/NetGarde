import pytest
from app.features.blocked_sites.repositories.blocked_site_repository import BlockedSiteRepository
from app.features.blocked_sites.schemas.blocked_site import BlockedSiteCreate
from app.features.blocked_sites.models.blocked_site import BlockedSite


class TestBlockedSiteRepository:
    def test_create_blocked_site(self, db_session, sample_blocked_site_data):
        repository = BlockedSiteRepository(db_session)
        create_data = BlockedSiteCreate(**sample_blocked_site_data)
        
        result = repository.create(create_data)
        
        assert result.id is not None
        assert result.domain == "example.com"
        assert result.reason == "Test reason"
        assert result.category == "Malware"
        assert result.is_deleted is False
        assert result.created_by == 1
        assert result.updated_by == 1

    def test_create_blocked_site_with_custom_user_ids(self, db_session):
        repository = BlockedSiteRepository(db_session)
        create_data = BlockedSiteCreate(
            domain="custom.com",
            reason="Custom reason",
            category=None,
            created_by=5,
            updated_by=5,
        )
        
        result = repository.create(create_data)
        
        assert result.created_by == 5
        assert result.updated_by == 5

    def test_get_by_id_existing(self, db_session, sample_blocked_site):
        repository = BlockedSiteRepository(db_session)
        
        result = repository.get_by_id(sample_blocked_site.id)
        
        assert result is not None
        assert result.id == sample_blocked_site.id
        assert result.domain == sample_blocked_site.domain

    def test_get_by_id_not_found(self, db_session):
        repository = BlockedSiteRepository(db_session)
        
        result = repository.get_by_id(999)
        
        assert result is None

    def test_get_by_id_excludes_deleted(self, db_session, sample_blocked_site):
        repository = BlockedSiteRepository(db_session)
        sample_blocked_site.is_deleted = True
        db_session.commit()
        
        result = repository.get_by_id(sample_blocked_site.id)
        
        assert result is None

    def test_get_by_domain_existing(self, db_session, sample_blocked_site):
        repository = BlockedSiteRepository(db_session)
        
        result = repository.get_by_domain("example.com")
        
        assert result is not None
        assert result.domain == "example.com"

    def test_get_by_domain_not_found(self, db_session):
        repository = BlockedSiteRepository(db_session)
        
        result = repository.get_by_domain("nonexistent.com")
        
        assert result is None

    def test_get_by_domain_excludes_deleted(self, db_session, sample_blocked_site):
        repository = BlockedSiteRepository(db_session)
        sample_blocked_site.is_deleted = True
        db_session.commit()
        
        result = repository.get_by_domain("example.com")
        
        assert result is None

    def test_get_blocked_sites_without_pagination(self, db_session, multiple_blocked_sites):
        repository = BlockedSiteRepository(db_session)
        
        sites, total = repository.get_blocked_sites()
        
        assert len(sites) == 3
        assert total == 3
        assert all(not site.is_deleted for site in sites)

    def test_get_blocked_sites_with_pagination(self, db_session, multiple_blocked_sites):
        repository = BlockedSiteRepository(db_session)
        
        sites, total = repository.get_blocked_sites(skip=0, limit=2)
        
        assert len(sites) == 2
        assert total == 3

    def test_get_blocked_sites_pagination_second_page(self, db_session, multiple_blocked_sites):
        repository = BlockedSiteRepository(db_session)
        
        sites, total = repository.get_blocked_sites(skip=2, limit=2)
        
        assert len(sites) == 1
        assert total == 3

    def test_get_blocked_sites_with_domain_search(self, db_session, multiple_blocked_sites):
        repository = BlockedSiteRepository(db_session)
        
        sites, total = repository.get_blocked_sites(domain_search="example")
        
        assert len(sites) == 1
        assert total == 1
        assert sites[0].domain == "example.com"

    def test_get_blocked_sites_domain_search_case_insensitive(self, db_session, multiple_blocked_sites):
        repository = BlockedSiteRepository(db_session)
        
        sites, total = repository.get_blocked_sites(domain_search="EXAMPLE")
        
        assert len(sites) == 1
        assert sites[0].domain == "example.com"

    def test_get_blocked_sites_domain_search_partial_match(self, db_session, multiple_blocked_sites):
        repository = BlockedSiteRepository(db_session)
        
        sites, total = repository.get_blocked_sites(domain_search="test")
        
        assert len(sites) == 1
        assert sites[0].domain == "test.com"

    def test_get_blocked_sites_domain_search_empty_string(self, db_session, multiple_blocked_sites):
        repository = BlockedSiteRepository(db_session)
        
        sites, total = repository.get_blocked_sites(domain_search="")
        
        assert len(sites) == 3
        assert total == 3

    def test_get_blocked_sites_domain_search_whitespace(self, db_session, multiple_blocked_sites):
        repository = BlockedSiteRepository(db_session)
        
        sites, total = repository.get_blocked_sites(domain_search="   ")
        
        assert len(sites) == 3
        assert total == 3

    def test_update_blocked_site(self, db_session, sample_blocked_site):
        repository = BlockedSiteRepository(db_session)
        update_data = BlockedSiteCreate(
            domain="updated.com",
            reason="Updated reason",
            category="Updated Category",
        )
        
        result = repository.update(sample_blocked_site.id, update_data)
        
        assert result is not None
        assert result.domain == "updated.com"
        assert result.reason == "Updated reason"
        assert result.category == "Updated Category"
        assert result.updated_at is not None

    def test_update_blocked_site_not_found(self, db_session):
        repository = BlockedSiteRepository(db_session)
        update_data = BlockedSiteCreate(domain="test.com", reason="test")
        
        result = repository.update(999, update_data)
        
        assert result is None

    def test_update_blocked_site_excludes_deleted(self, db_session, sample_blocked_site):
        repository = BlockedSiteRepository(db_session)
        sample_blocked_site.is_deleted = True
        db_session.commit()
        update_data = BlockedSiteCreate(domain="updated.com", reason="test")
        
        result = repository.update(sample_blocked_site.id, update_data)
        
        assert result is None

    def test_delete_blocked_site(self, db_session, sample_blocked_site):
        repository = BlockedSiteRepository(db_session)
        
        result = repository.delete(sample_blocked_site.id)
        
        assert result is True
        deleted_site = db_session.query(BlockedSite).filter(BlockedSite.id == sample_blocked_site.id).first()
        assert deleted_site.is_deleted is True

    def test_delete_blocked_site_not_found(self, db_session):
        repository = BlockedSiteRepository(db_session)
        
        result = repository.delete(999)
        
        assert result is False

    def test_delete_blocked_site_excludes_deleted(self, db_session, sample_blocked_site):
        repository = BlockedSiteRepository(db_session)
        sample_blocked_site.is_deleted = True
        db_session.commit()
        
        result = repository.delete(sample_blocked_site.id)
        
        assert result is False

    def test_get_counts_by_category(self, db_session, multiple_blocked_sites):
        repository = BlockedSiteRepository(db_session)
        
        counts = repository.get_counts_by_category()
        
        assert "Malware" in counts
        assert "Phishing" in counts
        assert counts["Malware"] == 1
        assert counts["Phishing"] == 1
        assert None not in counts

    def test_get_counts_by_category_excludes_deleted(self, db_session):
        repository = BlockedSiteRepository(db_session)
        deleted = BlockedSite(domain="deleted1.com", reason="test", category="Malware", is_deleted=True)
        active1 = BlockedSite(domain="active1.com", reason="test", category="Malware", is_deleted=False)
        active2 = BlockedSite(domain="active2.com", reason="test", category="Malware", is_deleted=False)
        db_session.add(deleted)
        db_session.add(active1)
        db_session.add(active2)
        db_session.commit()
        
        counts = repository.get_counts_by_category()
        
        assert counts["Malware"] == 2

    def test_get_counts_by_category_excludes_null_categories(self, db_session, multiple_blocked_sites):
        repository = BlockedSiteRepository(db_session)
        
        counts = repository.get_counts_by_category()
        
        assert None not in counts

