from unittest.mock import patch

import pytest

from app.features.policy.services.vpn_login_geo_block_service import (
    VpnLoginGeoBlockService,
    VpnLoginGeoBlockedError,
)
from app.shared.geoip import GeoLocation


@patch("app.features.policy.services.vpn_login_geo_block_service.lookup_geo")
def test_blocks_enroll_from_iran(mock_lookup, monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.VPN_LOGIN_GEO_BLOCK_ENABLED", True)
    monkeypatch.setattr("app.shared.config.settings.BLOCKED_VPN_LOGIN_COUNTRIES", "IR")
    mock_lookup.return_value = GeoLocation(country_code="IR", country_name="Iran")

    svc = VpnLoginGeoBlockService()
    with pytest.raises(VpnLoginGeoBlockedError, match="Iran"):
        svc.assert_enroll_allowed(connect_ip="8.8.8.8", client_reported_ip=None)


@patch("app.features.policy.services.vpn_login_geo_block_service.lookup_geo")
def test_allows_enroll_from_israel(mock_lookup, monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.VPN_LOGIN_GEO_BLOCK_ENABLED", True)
    monkeypatch.setattr("app.shared.config.settings.BLOCKED_VPN_LOGIN_COUNTRIES", "IR")
    mock_lookup.return_value = GeoLocation(country_code="IL", country_name="Israel")

    VpnLoginGeoBlockService().assert_enroll_allowed(connect_ip="8.8.8.8", client_reported_ip=None)


@patch("app.features.policy.services.vpn_login_geo_block_service.lookup_geo")
def test_allows_when_geo_unknown(mock_lookup, monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.VPN_LOGIN_GEO_BLOCK_ENABLED", True)
    monkeypatch.setattr("app.shared.config.settings.BLOCKED_VPN_LOGIN_COUNTRIES", "IR")
    mock_lookup.return_value = None

    VpnLoginGeoBlockService().assert_enroll_allowed(connect_ip="8.8.8.8", client_reported_ip=None)
