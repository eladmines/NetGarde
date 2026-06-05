def test_topology_route(api_client, topology_env, active_vpn_pool, mock_wireguard_peers):
    response = api_client.get("/vpn/topology")
    assert response.status_code == 200
    body = response.json()
    assert body["server"]["endpoint"] == "vpn.test.example:51820"
    assert isinstance(body["peers"], list)
