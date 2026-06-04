import json
from datetime import datetime, timezone
from typing import Any, Dict, Optional

from sqlalchemy.orm import Session

from app.features.client_behavior.models.client_behavior_profile import ClientBehaviorProfile


class BehaviorProfileRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, device_id: int) -> ClientBehaviorProfile:
        profile = (
            self.db.query(ClientBehaviorProfile)
            .filter(ClientBehaviorProfile.device_id == device_id)
            .first()
        )
        if profile:
            return profile
        now = datetime.now(timezone.utc)
        profile = ClientBehaviorProfile(
            device_id=device_id,
            profile_ready=False,
            created_at=now,
            updated_at=now,
        )
        self.db.add(profile)
        self.db.flush()
        return profile

    def get_by_device_id(self, device_id: int) -> Optional[ClientBehaviorProfile]:
        return (
            self.db.query(ClientBehaviorProfile)
            .filter(ClientBehaviorProfile.device_id == device_id)
            .first()
        )

    def update_baseline(
        self,
        device_id: int,
        baseline: Dict[str, Any],
        profile_ready: bool,
    ) -> ClientBehaviorProfile:
        profile = self.get_or_create(device_id)
        profile.baseline_json = json.dumps(baseline)
        profile.profile_ready = profile_ready
        profile.updated_at = datetime.now(timezone.utc)
        return profile

    def update_score(self, device_id: int, score: int) -> None:
        profile = self.get_or_create(device_id)
        profile.last_score = score
        profile.last_scored_at = datetime.now(timezone.utc)

    def parse_baseline(self, profile: ClientBehaviorProfile) -> Dict[str, Any]:
        if not profile.baseline_json:
            return {}
        try:
            return json.loads(profile.baseline_json)
        except json.JSONDecodeError:
            return {}
