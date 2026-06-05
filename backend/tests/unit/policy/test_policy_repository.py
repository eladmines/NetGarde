from app.features.policy.repositories.policy_repository import PolicyRepository
from tests.helpers.factories import create_vpn_device, seed_policy_catalog


def test_list_and_get_packs(db_session):
    seed_policy_catalog(db_session)
    repo = PolicyRepository(db_session)
    packs = repo.list_packs()
    assert len(packs) >= 2
    malware = repo.get_pack_by_slug("malware")
    assert malware is not None
    assert malware.enabled_globally is True


def test_update_pack_global(db_session):
    seed_policy_catalog(db_session)
    repo = PolicyRepository(db_session)
    pack = repo.update_pack_global("social", True)
    assert pack is not None
    assert pack.enabled_globally is True
    db_session.commit()
    assert repo.get_pack_by_slug("social").enabled_globally is True


def test_assign_profile_to_device(db_session):
    seed_policy_catalog(db_session)
    device, _ = create_vpn_device(db_session)
    repo = PolicyRepository(db_session)
    profile = repo.get_profile_by_slug("teen")
    updated = repo.assign_profile_to_device(device.id, profile.id)
    db_session.commit()
    assert updated.policy_profile_id == profile.id


def test_get_default_profile(db_session):
    seed_policy_catalog(db_session)
    repo = PolicyRepository(db_session)
    profile = repo.get_default_profile()
    assert profile is not None
    assert profile.slug == "teen"
