from datetime import datetime, timezone
from typing import Optional

from sqlalchemy.orm import Session

from app.features.client_behavior.models.device_security_policy import DeviceSecurityPolicy
from app.shared.config import settings


class DeviceSecurityPolicyRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_or_create(self, device_id: int) -> DeviceSecurityPolicy:
        policy = (
            self.db.query(DeviceSecurityPolicy)
            .filter(DeviceSecurityPolicy.device_id == device_id)
            .first()
        )
        if policy:
            return policy
        now = datetime.now(timezone.utc)
        policy = DeviceSecurityPolicy(
            device_id=device_id,
            auto_block_enabled=settings.BEHAVIOR_AUTO_BLOCK_DEFAULT,
            auto_block_threshold=settings.BEHAVIOR_AUTO_BLOCK_THRESHOLD,
            max_blocks_per_day=settings.BEHAVIOR_MAX_BLOCKS_PER_DAY,
            created_at=now,
            updated_at=now,
        )
        self.db.add(policy)
        self.db.flush()
        return policy

    def update(
        self,
        device_id: int,
        *,
        auto_block_enabled: Optional[bool] = None,
        auto_block_threshold: Optional[int] = None,
        max_blocks_per_day: Optional[int] = None,
    ) -> DeviceSecurityPolicy:
        policy = self.get_or_create(device_id)
        now = datetime.now(timezone.utc)
        if auto_block_enabled is not None:
            policy.auto_block_enabled = auto_block_enabled
        if auto_block_threshold is not None:
            policy.auto_block_threshold = auto_block_threshold
        if max_blocks_per_day is not None:
            policy.max_blocks_per_day = max_blocks_per_day
        policy.updated_at = now
        return policy
