from unittest.mock import patch


def test_policy_sync_status_empty(api_client, seed_policy):
    response = api_client.get("/policy/sync-status")
    assert response.status_code == 200
    body = response.json()
    assert body["last_sync_at"] is None
    assert body["last_success"] is None


def test_policy_sync_report(api_client, seed_policy, dns_ingest_env):
    response = api_client.post(
        "/policy/sync-report",
        json={"success": True, "message": "dns-sync ok"},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["last_success"] is True
    assert body["last_message"] == "dns-sync ok"


@patch("app.features.policy.repositories.policy_sync_repository.PolicySyncRepository.notify_policy_changed")
def test_apply_policy_now(mock_notify, api_client, seed_policy):
    response = api_client.post("/policy/apply")
    assert response.status_code == 200
    body = response.json()
    assert body["queued"] is True
    mock_notify.assert_called_once()


def test_policy_dns_sync(api_client, seed_policy, dns_ingest_env):
    response = api_client.get("/policy/dns-sync")
    assert response.status_code == 200
    body = response.json()
    assert "global_domains" in body
    assert "entries" in body


def test_list_pack_domains(api_client, seed_policy):
    response = api_client.get("/policy/packs/malware/domains", params={"limit": 10})
    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "malware"
    assert isinstance(body["domains"], list)


@patch("app.features.policy.services.policy_service.refresh_pack")
def test_refresh_policy_pack(mock_refresh, api_client, seed_policy):
    mock_refresh.return_value = 42
    response = api_client.post("/policy/packs/social/refresh")
    assert response.status_code == 200
    body = response.json()
    assert body["slug"] == "social"
    assert body["domain_count"] == 42


def test_update_custom_policy_profile(api_client, seed_policy):
    profiles = api_client.get("/policy/profiles").json()
    work = next(p for p in profiles if p["slug"] == "work")
    response = api_client.put(
        f"/policy/profiles/{work['id']}",
        json={"behavior_sensitivity": "high", "quarantine_hours": 8},
    )
    assert response.status_code == 200
    body = response.json()
    assert body["behavior_sensitivity"] == "high"
    assert body["quarantine_hours"] == 8
