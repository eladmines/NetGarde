import pytest
import os
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, Session
from sqlalchemy.pool import StaticPool

os.environ.setdefault('DB_URL', 'sqlite:///:memory:')

from app.shared.database import Base
from app.features.blocked_sites.models.blocked_site import BlockedSite


@pytest.fixture(scope="function")
def db_session():
    engine = create_engine(
        "sqlite:///:memory:",
        connect_args={"check_same_thread": False},
        poolclass=StaticPool,
    )
    Base.metadata.create_all(bind=engine)
    TestingSessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
    
    session = TestingSessionLocal()
    try:
        yield session
    finally:
        session.close()
        Base.metadata.drop_all(bind=engine)


@pytest.fixture
def sample_blocked_site_data():
    return {
        "domain": "example.com",
        "reason": "Test reason",
        "category": "Malware",
    }


@pytest.fixture
def sample_blocked_site(db_session, sample_blocked_site_data):
    blocked_site = BlockedSite(**sample_blocked_site_data)
    db_session.add(blocked_site)
    db_session.commit()
    db_session.refresh(blocked_site)
    return blocked_site


@pytest.fixture
def multiple_blocked_sites(db_session):
    sites = [
        BlockedSite(domain="example.com", reason="Reason 1", category="Malware"),
        BlockedSite(domain="test.com", reason="Reason 2", category="Phishing"),
        BlockedSite(domain="sample.org", reason="Reason 3", category=None),
        BlockedSite(domain="deleted.com", reason="Reason 4", category="Malware", is_deleted=True),
    ]
    for site in sites:
        db_session.add(site)
    db_session.commit()
    return sites

