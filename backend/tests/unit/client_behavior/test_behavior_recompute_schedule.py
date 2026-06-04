from datetime import datetime, timedelta, timezone
from unittest.mock import MagicMock

from app.features.client_behavior.services.behavior_scoring_service import BehaviorScoringService


def _service() -> BehaviorScoringService:
    svc = BehaviorScoringService(db=None)  # type: ignore[arg-type]
    svc.profile_repo = MagicMock()
    return svc


def test_should_recompute_when_no_profile():
    svc = _service()
    assert svc._should_recompute_baseline(None) is True


def test_should_recompute_when_computed_at_stale():
    svc = _service()
    old = (datetime.now(timezone.utc) - timedelta(hours=3)).isoformat()
    profile = MagicMock()
    profile.baseline_json = '{"computed_at":"' + old + '"}'
    profile.updated_at = datetime.now(timezone.utc)
    svc.profile_repo.parse_baseline.return_value = {"computed_at": old}
    assert svc._should_recompute_baseline(profile) is True


def test_should_not_recompute_when_computed_at_fresh():
    svc = _service()
    recent = (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()
    profile = MagicMock()
    profile.baseline_json = "{}"
    profile.updated_at = datetime.now(timezone.utc) - timedelta(days=1)
    svc.profile_repo.parse_baseline.return_value = {"computed_at": recent}
    assert svc._should_recompute_baseline(profile) is False
