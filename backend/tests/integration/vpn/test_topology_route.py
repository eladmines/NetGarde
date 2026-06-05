from unittest.mock import patch

from app.features.vpn.models.ip_pool import IpPool


def test_topology_route(api_client, topology_env, db_session):
    db_session.add(
        IpPool(
            name="default",
            cidr="10.8.0.0/24",
            gateway_ip="10.8.0.1",
            dns_ip="10.8.0.1",
            endpoint="vpn.test.example:51820",
            server_public_key="serverPubKeyTest=",
            is_active=True,
        )
    )
    db_session.commit()

    with patch(
        "app.features.vpn.services.vpn_topology_service.list_peers_on_host",
        return_value=[],
    ):
        response = api_client.get("/vpn/topology")
    assert response.status_code == 200
    body = response.json()
    assert body["server"]["endpoint"] == "vpn.test.example:51820"
    assert isinstance(body["peers"], list)
