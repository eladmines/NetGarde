from app.features.policy.services.policy_dns_service import PolicyDnsService
from tests.helpers.factories import create_behavior_block, create_vpn_device, seed_policy_catalog


def test_build_dns_sync_includes_device(db_session):
    seed_policy_catalog(db_session)
    device, _ = create_vpn_device(db_session, mac_address="11:22:33:44:55:66")
    svc = PolicyDnsService(db_session)
    result = svc.build_dns_sync()

    assert isinstance(result.global_domains, list)
    entry = next(e for e in result.entries if e.device_id == device.id)
    assert entry.mac_address == "11:22:33:44:55:66"
    assert entry.allowlist_only is False


def test_build_dns_sync_includes_behavior_blocks(db_session):
    seed_policy_catalog(db_session)
    device, _ = create_vpn_device(db_session, mac_address="aa:bb:cc:dd:ee:01")
    create_behavior_block(db_session, device, domain="blocked.behavior.test")

    svc = PolicyDnsService(db_session)
    result = svc.build_dns_sync()
    entry = next(e for e in result.entries if e.device_id == device.id)
    assert "blocked.behavior.test" in entry.block_domains
