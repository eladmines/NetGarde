from datetime import datetime, timezone

from tests.helpers.integration import dns_query_payload


def test_unique_clients(api_client, post_dns_query, dns_ingest_env, vpn_device):
    post_dns_query(domain="client.test", blocked=True)
    response = api_client.get("/dns-queries/clients")
    assert response.status_code == 200
    clients = response.json()
    assert "10.0.0.10" in clients


def test_dns_alerts_list(post_dns_query, api_client, dns_ingest_env, vpn_device):
    post_dns_query(domain="blocked.alert", blocked=True)
    response = api_client.get("/dns-queries/alerts")
    assert response.status_code == 200
    body = response.json()
    assert "items" in body
    assert "total" in body


def test_grouped_sites(post_dns_query, api_client, dns_live_stats_env, vpn_device):
    post_dns_query(domain="www.example.com", blocked=False)
    response = api_client.get("/dns-queries/sites", params={"limit": 20})
    assert response.status_code == 200
    body = response.json()
    assert "sites" in body


def test_whois_route(api_client, mock_whois_lookup):
    response = api_client.get("/dns-queries/whois", params={"domain": "example.com"})
    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "example.com"
    assert "Test Registrar" in body["text"]


def test_cleanup_old_records(api_client, dns_ingest_env, vpn_device):
    api_client.post(
        "/dns-queries",
        json=dns_query_payload(
            domain="old.test",
            blocked=True,
            timestamp=datetime(2020, 1, 1, tzinfo=timezone.utc),
        ),
    )
    response = api_client.delete("/dns-queries/cleanup", params={"days": 1})
    assert response.status_code == 200
    body = response.json()
    assert body["deleted"] >= 0
