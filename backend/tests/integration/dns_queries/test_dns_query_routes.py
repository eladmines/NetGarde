from datetime import datetime, timezone


def test_create_dns_query(api_client, dns_ingest_env, vpn_device):
    ts = datetime.now(timezone.utc).isoformat()
    response = api_client.post(
        "/dns-queries",
        json={
            "timestamp": ts,
            "client_ip": "10.0.0.10",
            "domain": "blocked.test",
            "query_type": "A",
            "action": "block",
            "blocked": True,
        },
    )
    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "blocked.test"
    assert body["blocked"] is True
    assert body["id"] > 0


def test_bulk_create_and_list_dns_queries(api_client, dns_ingest_env, vpn_device):
    ts = datetime.now(timezone.utc).isoformat()
    bulk = api_client.post(
        "/dns-queries/bulk",
        json={
            "queries": [
                {
                    "timestamp": ts,
                    "client_ip": "10.0.0.10",
                    "domain": "one.test",
                    "blocked": False,
                },
                {
                    "timestamp": ts,
                    "client_ip": "10.0.0.10",
                    "domain": "two.test",
                    "blocked": True,
                },
            ]
        },
    )
    assert bulk.status_code == 200

    listed = api_client.get("/dns-queries", params={"page": 1, "page_size": 10})
    assert listed.status_code == 200
    payload = listed.json()
    assert payload["total"] >= 2
    domains = {item["domain"] for item in payload["items"]}
    assert "one.test" in domains
    assert "two.test" in domains


def test_get_dns_stats(api_client, dns_ingest_env, vpn_device):
    ts = datetime.now(timezone.utc).isoformat()
    api_client.post(
        "/dns-queries",
        json={
            "timestamp": ts,
            "client_ip": "10.0.0.10",
            "domain": "stats.test",
            "blocked": True,
        },
    )
    response = api_client.get("/dns-queries/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_queries"] >= 1
