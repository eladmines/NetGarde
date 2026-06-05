import pytest
from fastapi import HTTPException

from app.features.policy.schemas.policy import PolicyProfileUpdate
from app.features.policy.services.policy_service import PolicyService
from tests.helpers.factories import create_vpn_device, seed_policy_catalog


def test_list_packs_returns_seeded_catalog(db_session):
    seed_policy_catalog(db_session)
    packs = PolicyService(db_session).list_packs()
    slugs = {p.slug for p in packs}
    assert "malware" in slugs
    assert "social" in slugs


def test_set_pack_enabled_globally(db_session):
    seed_policy_catalog(db_session)
    svc = PolicyService(db_session)
    updated = svc.set_pack_enabled_globally("social", True)
    assert updated.slug == "social"
    assert updated.enabled_globally is True


def test_set_pack_enabled_globally_not_found(db_session):
    svc = PolicyService(db_session)
    with pytest.raises(HTTPException) as exc:
        svc.set_pack_enabled_globally("missing", True)
    assert exc.value.status_code == 404


def test_list_profiles_returns_builtin_teen(db_session):
    seed_policy_catalog(db_session)
    profiles = PolicyService(db_session).list_profiles()
    assert any(p.slug == "teen" for p in profiles)


def test_assign_profile_to_device(db_session):
    seed_policy_catalog(db_session)
    device, _ = create_vpn_device(db_session)
    svc = PolicyService(db_session)
    assignment = svc.assign_profile_to_device(device.id, "teen")
    assert assignment.device_id == device.id
    assert assignment.policy_profile_slug == "teen"


def test_assign_profile_to_device_not_found(db_session):
    seed_policy_catalog(db_session)
    svc = PolicyService(db_session)
    with pytest.raises(HTTPException) as exc:
        svc.assign_profile_to_device(999, "teen")
    assert exc.value.status_code == 404


def test_update_builtin_profile_rejected(db_session):
    seed_policy_catalog(db_session)
    profiles = PolicyService(db_session).list_profiles()
    teen = next(p for p in profiles if p.slug == "teen")
    svc = PolicyService(db_session)
    with pytest.raises(HTTPException) as exc:
        svc.update_profile(teen.id, PolicyProfileUpdate(behavior_sensitivity="high"))
    assert exc.value.status_code == 404
