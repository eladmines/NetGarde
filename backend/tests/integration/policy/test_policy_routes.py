def test_list_policy_packs(api_client, seed_policy):
    response = api_client.get("/policy/packs")
    assert response.status_code == 200
    packs = response.json()
    slugs = {p["slug"] for p in packs}
    assert "malware" in slugs
    assert "social" in slugs
    malware = next(p for p in packs if p["slug"] == "malware")
    assert malware["enabled_globally"] is True


def test_update_policy_pack_enabled(api_client, seed_policy):
    response = api_client.put("/policy/packs/social", json={"enabled_globally": True})
    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "social"
    assert body["enabled_globally"] is True


def test_list_policy_profiles(api_client, seed_policy):
    response = api_client.get("/policy/profiles")
    assert response.status_code == 200
    profiles = response.json()
    assert any(p["slug"] == "teen" for p in profiles)


def test_get_forbidden_country_policy_defaults(api_client, seed_policy, monkeypatch):
    monkeypatch.setattr("app.shared.config.settings.VPN_LOGIN_GEO_BLOCK_ENABLED", False)
    monkeypatch.setattr("app.shared.config.settings.BLOCKED_VPN_LOGIN_COUNTRIES", "")
    monkeypatch.setattr("app.shared.config.settings.FORBIDDEN_COUNTRY_RULES", "[]")

    response = api_client.get("/policy/forbidden-countries")
    assert response.status_code == 200
    body = response.json()
    assert body["managed_in_database"] is False
    assert body["rules"] == []


def test_save_forbidden_country_policy(api_client, seed_policy):
    payload = {
        "vpn_login_block_enabled": True,
        "destination_rules_enabled": True,
        "vpn_login_denied_countries": ["IR"],
        "destination_rules": [
            {"user_country": "IL", "blocked_countries": ["IR"]},
        ],
    }
    response = api_client.put("/policy/forbidden-countries", json=payload)
    assert response.status_code == 200
    body = response.json()
    assert body["managed_in_database"] is True
    assert "IR" in body["blocked_vpn_login_countries"]
    assert body["rules"][0]["user_country"] == "IL"


def test_list_geo_country_choices(api_client):
    response = api_client.get("/policy/geo-countries/choices")
    assert response.status_code == 200
    choices = response.json()
    assert len(choices) > 0
    assert all("code" in c and "name" in c for c in choices)
