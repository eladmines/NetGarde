from unittest.mock import patch

import pytest

from app.features.policy.schemas.policy import DestinationCountryRuleUpdate, GeoCountryPolicyUpdate
from app.features.policy.services.geo_country_policy_service import GeoCountryPolicyService
from app.features.policy.services.vpn_login_geo_block_service import VpnLoginGeoBlockedError
from app.shared.geoip import GeoLocation


@patch("app.features.policy.services.vpn_login_geo_block_service.lookup_geo")
def test_save_and_block_vpn_enroll_from_db(mock_lookup, db_session, monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.VPN_LOGIN_GEO_BLOCK_ENABLED", False)
    monkeypatch.setattr("app.shared.config.settings.BLOCKED_VPN_LOGIN_COUNTRIES", "")
    mock_lookup.return_value = GeoLocation(country_code="IR", country_name="Iran")

    svc = GeoCountryPolicyService(db_session)
    svc.save_policy(
        GeoCountryPolicyUpdate(
            vpn_login_block_enabled=True,
            destination_rules_enabled=True,
            vpn_login_denied_countries=["IR"],
            destination_rules=[
                DestinationCountryRuleUpdate(user_country="IL", blocked_countries=["IR"]),
            ],
        )
    )

    read = svc.get_policy_read()
    assert read.managed_in_database is True
    assert "IR" in read.blocked_vpn_login_countries
    assert read.rules[0].user_country == "IL"

    with pytest.raises(VpnLoginGeoBlockedError):
        svc.assert_vpn_enroll_allowed(connect_ip="8.8.8.8", client_reported_ip=None)
