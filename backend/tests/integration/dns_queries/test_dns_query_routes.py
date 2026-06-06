from tests.helpers.integration import dns_query_payload


def test_create_dns_query(post_dns_query, dns_ingest_env, vpn_device):
    response = post_dns_query(
        domain="blocked.test",
        query_type="A",
        action="block",
    )
    assert response.status_code == 200
    body = response.json()
    assert body["domain"] == "blocked.test"
    assert body["blocked"] is True
    assert body["id"] > 0


def test_bulk_create_and_list_dns_queries(api_client, dns_ingest_env, vpn_device):
    bulk = api_client.post(
        "/dns-queries/bulk",
        json={
            "queries": [
                dns_query_payload(domain="one.test", blocked=False),
                dns_query_payload(domain="two.test", blocked=True),
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


def test_get_dns_stats(post_dns_query, api_client, dns_ingest_env, vpn_device):
    post_dns_query(domain="stats.test", blocked=True)
    response = api_client.get("/dns-queries/stats")
    assert response.status_code == 200
    stats = response.json()
    assert stats["total_queries"] >= 1
