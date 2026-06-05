def test_request_id_header_on_api_response(api_client):
    response = api_client.get("/health")
    assert response.status_code == 200
    assert response.headers.get("X-Request-ID")


def test_request_id_echoed_when_provided(api_client):
    custom_id = "test-correlation-id-12345"
    response = api_client.get(
        "/health",
        headers={"X-Request-ID": custom_id},
    )
    assert response.headers.get("X-Request-ID") == custom_id
