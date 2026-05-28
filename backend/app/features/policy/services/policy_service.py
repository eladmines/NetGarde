from typing import List, Optional

from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.features.client_behavior.repositories.device_security_policy_repository import (
    DeviceSecurityPolicyRepository,
)
from app.features.devices.repositories.device_repository import DeviceRepository
from app.features.policy.pack_loader import load_all_packs
from app.features.policy.repositories.policy_repository import PolicyRepository
from app.features.policy.schemas.policy import (
    DevicePolicyAssignmentRead,
    PolicyPackRead,
    PolicyProfileRead,
    PolicyProfileUpdate,
)
from app.features.policy.sensitivity import block_threshold_for_sensitivity


class PolicyService:
    def __init__(self, db: Session):
        self.db = db
        self.repo = PolicyRepository(db)
        self.device_repo = DeviceRepository(db)
        self.security_repo = DeviceSecurityPolicyRepository(db)

    def list_packs(self) -> List[PolicyPackRead]:
        counts = {slug: len(domains) for slug, domains in load_all_packs().items()}
        return [
            PolicyPackRead(
                id=p.id,
                slug=p.slug,
                name=p.name,
                description=p.description,
                enabled_globally=p.enabled_globally,
                domain_count=counts.get(p.slug, 0),
            )
            for p in self.repo.list_packs()
        ]

    def set_pack_enabled_globally(self, slug: str, enabled: bool) -> PolicyPackRead:
        pack = self.repo.update_pack_global(slug, enabled)
        if not pack:
            raise HTTPException(status_code=404, detail=f"Pack {slug} not found")
        self.db.commit()
        counts = {s: len(d) for s, d in load_all_packs().items()}
        return PolicyPackRead(
            id=pack.id,
            slug=pack.slug,
            name=pack.name,
            description=pack.description,
            enabled_globally=pack.enabled_globally,
            domain_count=counts.get(pack.slug, 0),
        )

    def list_profiles(self) -> List[PolicyProfileRead]:
        return [PolicyProfileRead.model_validate(p) for p in self.repo.list_profiles()]

    def update_profile(self, profile_id: int, data: PolicyProfileUpdate) -> PolicyProfileRead:
        profile = self.repo.update_profile(profile_id, **data.model_dump(exclude_unset=True))
        if not profile:
            raise HTTPException(status_code=404, detail="Profile not found or builtin")
        self.db.commit()
        return PolicyProfileRead.model_validate(profile)

    def get_device_policy(self, device_id: int) -> DevicePolicyAssignmentRead:
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        profile = None
        if device.policy_profile_id:
            profile = self.repo.get_profile_by_id(device.policy_profile_id)
        quarantine = self.repo.get_active_quarantine(device_id)
        return DevicePolicyAssignmentRead(
            device_id=device_id,
            policy_profile_id=profile.id if profile else None,
            policy_profile_slug=profile.slug if profile else None,
            policy_profile_name=profile.name if profile else None,
            in_quarantine=quarantine is not None,
            quarantine_expires_at=quarantine.expires_at if quarantine else None,
        )

    def assign_profile_to_device(self, device_id: int, profile_slug: str) -> DevicePolicyAssignmentRead:
        profile = self.repo.get_profile_by_slug(profile_slug)
        if not profile:
            raise HTTPException(status_code=404, detail=f"Profile {profile_slug} not found")
        device = self.repo.assign_profile_to_device(device_id, profile.id)
        if not device:
            raise HTTPException(status_code=404, detail="Device not found")
        self._sync_security_policy_from_profile(device_id, profile.behavior_sensitivity)
        self.db.commit()
        return self.get_device_policy(device_id)

    def assign_profile_by_slug_on_enroll(self, device_id: int, profile_slug: Optional[str]) -> None:
        if not profile_slug:
            profile = self.repo.get_default_profile()
        else:
            profile = self.repo.get_profile_by_slug(profile_slug)
        if not profile:
            return
        self.repo.assign_profile_to_device(device_id, profile.id)
        self._sync_security_policy_from_profile(device_id, profile.behavior_sensitivity)

    def _sync_security_policy_from_profile(self, device_id: int, sensitivity: str) -> None:
        policy = self.security_repo.get_or_create(device_id)
        from app.shared.config import settings

        policy.auto_block_enabled = True
        policy.auto_block_threshold = block_threshold_for_sensitivity(sensitivity)
        policy.max_blocks_per_day = settings.BEHAVIOR_MAX_BLOCKS_PER_DAY
