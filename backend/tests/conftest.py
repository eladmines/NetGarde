import os

import pytest
from fastapi.testclient import TestClient
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker
from sqlalchemy.pool import StaticPool

os.environ.setdefault("DB_URL", "sqlite:///:memory:")

from app.main import app
from app.shared.database import Base
from app.shared.dependencies import get_db
from tests.helpers.factories import create_vpn_device, seed_policy_catalog

# Register all models on Base.metadata (required for create_all FK resolution)
from app.features.dns_queries.models.dns_query import DnsQuery  # noqa: F401
from app.features.dns_queries.models.dns_alert import DnsAlert  # noqa: F401
from app.features.dns_queries.models.domain_first_seen import DomainFirstSeen  # noqa: F401
from app.features.devices.models.device import Device  # noqa: F401
from app.features.devices.models.device_country_presence import DeviceCountryPresence  # noqa: F401
from app.features.devices.models.device_login_geo import DeviceLoginGeoObservation  # noqa: F401
from app.features.vpn.models.ip_pool import IpPool  # noqa: F401
from app.features.vpn.models.vpn_peer import VpnPeer  # noqa: F401
from app.features.vpn.models.ip_lease import IpLease  # noqa: F401
from app.features.vpn.models.vpn_enroll_event import VpnEnrollEvent  # noqa: F401
from app.features.vpn.models.device_usage_sample import DeviceUsageSample  # noqa: F401
from app.features.client_behavior.models.client_behavior_rollup import ClientBehaviorRollup  # noqa: F401
from app.features.client_behavior.models.client_behavior_profile import ClientBehaviorProfile  # noqa: F401
from app.features.client_behavior.models.client_blocked_domain import ClientBlockedDomain  # noqa: F401
from app.features.client_behavior.models.device_security_policy import DeviceSecurityPolicy  # noqa: F401
from app.features.policy.models.policy_pack import PolicyPack  # noqa: F401
from app.features.policy.models.policy_profile import PolicyProfile  # noqa: F401
from app.features.policy.models.geo_country_block import (  # noqa: F401
    GeoCountryBlock,
    GeoCountryPolicyConfig,
)
from app.features.policy.models.device_quarantine import DeviceQuarantine  # noqa: F401
from app.features.policy.models.policy_sync_status import PolicySyncStatus  # noqa: F401


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
    }


@pytest.fixture
def sample_blocked_site(db_session, sample_blocked_site_data):
    """Backward-compat fixture kept for older tests; returns dict only."""
    return sample_blocked_site_data


@pytest.fixture
def seed_policy(db_session):
    return seed_policy_catalog(db_session)


@pytest.fixture
def vpn_device(db_session):
    device, _lease = create_vpn_device(db_session)
    return device


@pytest.fixture
def api_client(db_session, monkeypatch):
    """FastAPI TestClient with in-memory DB and admin auth disabled."""
    monkeypatch.setattr("app.shared.config.settings.ADMIN_API_TOKEN", "")

    def override_get_db():
        try:
            yield db_session
        finally:
            pass

    app.dependency_overrides[get_db] = override_get_db
    with TestClient(app) as client:
        yield client
    app.dependency_overrides.clear()

