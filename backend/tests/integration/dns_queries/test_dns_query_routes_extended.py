from datetime import datetime, timezone
from unittest.mock import patch


def test_unique_clients(api_client, dns_ingest_env, vpn_device):
    ts = datetime.now(timezone.utc).isoformat()
    api_client.post(
        "/dns-queries",
        json={
            "timestamp": ts,
            "client_ip": "10.0.0.10",
            "domain": "client.test",
            "blocked": True,
        },
    )
    response = api_client.get("/dns-queries/clients")
    assert response.status_code == 200
    clients = response.json()
    assert "10.0.0.10" in clients


def test_dns_alerts_list(api_client, dns_ingest_env, vpn_device):
    ts = datetime.now(timezone.utc).isoformat()
    api_client.post(
        "/dns-queries",
        json={
            "timestamp": ts,
            "client_ip": "10.0.0.10",
            "domain": "blocked.alert",
            "blocked": True,
        },
    )
    response = api_client.get("/dns-queries/alerts")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body


def test_grouped_sites(api_client, dns_live_stats_env, vpn_device):
    ts = datetime.now(timezone.utc).isoformat()
    api_client.post(
        "/dns-queries",
        json={
            "timestamp": ts,
            "client_ip": "10.0.0.10",
            "domain": "www.example.com",
            "blocked": False,
        },
    )
    response = api_client.get("/dns-queries/sites", params={"limit": 20})
    assert response.status_code == 200
    body = response.json()
    assert "sites" in body


@patch("app.features.dns_queries.controllers.dns_query_controller.lookup_domain_whois")
def test_whois_route(mock_lookup, api_client):
    mock_lookup.return_value = {
        "domain": "example.com",
        "source": "rdap",
        "text": "Registrar: Test Registrar",
    }
    response = api_client.get("/dns-queries/whois", params={"domain": "example.com"})
    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "example.com"
    assert "Test Registrar" in body["text"]


def test_cleanup_old_records(api_client, dns_ingest_env, vpn_device):
    old_ts = datetime(2020, 1, 1, tzinfo=timezone.utc).isoformat()
    api_client.post(
        "/dns-queries",
        json={
            "timestamp": old_ts,
            "client_ip": "10.0.0.10",
            "domain": "old.test",
            "blocked": True,
        },
    )
    response = api_client.delete("/dns-queries/cleanup", params={"days": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["deleted"] >= 0
