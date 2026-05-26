from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.features.client_behavior.repositories.behavior_profile_repository import BehaviorProfileRepository
from app.features.client_behavior.repositories.client_blocked_domain_repository import ClientBlockedDomainRepository
from app.features.client_behavior.repositories.device_security_policy_repository import DeviceSecurityPolicyRepository
from app.features.client_behavior.schemas.behavior import (
    BehaviorProfileRead,
    ClientBlockSyncEntry,
    ClientBlockSyncResponse,
    ClientBlockedDomainRead,
    DeviceSecurityPolicyRead,
    DeviceSecurityPolicyUpdate,
)
from app.features.client_behavior.services.behavior_baseline_service import BehaviorBaselineService
from fastapi import HTTPException
from app.features.devices.repositories.device_repository import DeviceRepository
from app.features.dns_queries.models.dns_alert import DnsAlert
from app.features.dns_queries.schemas.dns_alert import DnsAlertResponse


class ClientBehaviorApiService:
    def __init__(self, db: Session):
        self.db = db
        self.device_repo = DeviceRepository(db)
        self.profile_repo = BehaviorProfileRepository(db)
        self.policy_repo = DeviceSecurityPolicyRepository(db)
        self.block_repo = ClientBlockedDomainRepository(db)

    def _require_device(self, device_id: int):
        device = self.device_repo.get_by_id(device_id)
        if not device:
            raise HTTPException(status_code=404, detail=f"Device {device_id} not found")
        return device

    def get_behavior_profile(self, device_id: int) -> BehaviorProfileRead:
        self._require_device(device_id)
        profile = self.profile_repo.get_or_create(device_id)
        return BehaviorProfileRead(
            device_id=device_id,
            profile_ready=profile.profile_ready,
            last_score=profile.last_score,
            last_scored_at=profile.last_scored_at,
            baseline=self.profile_repo.parse_baseline(profile),
            updated_at=profile.updated_at,
        )

    def get_behavior_events(
        self,
        device_id: int,
        *,
        page: int = 1,
        page_size: int = 20,
    ) -> dict:
        self._require_device(device_id)
        query = self.db.query(DnsAlert).filter(
            DnsAlert.device_id == device_id,
            DnsAlert.alert_type == "behavior_anomaly",
        )
        total = query.count()
        offset = (page - 1) * page_size
        items = (
            query.order_by(DnsAlert.timestamp.desc())
            .offset(offset)
            .limit(page_size)
            .all()
        )
        return {
            "items": [DnsAlertResponse.model_validate(a) for a in items],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": max(1, (total + page_size - 1) // page_size),
        }

    def get_security_policy(self, device_id: int) -> DeviceSecurityPolicyRead:
        self._require_device(device_id)
        policy = self.policy_repo.get_or_create(device_id)
        return DeviceSecurityPolicyRead.model_validate(policy)

    def update_security_policy(
        self, device_id: int, data: DeviceSecurityPolicyUpdate
    ) -> DeviceSecurityPolicyRead:
        self._require_device(device_id)
        policy = self.policy_repo.update(
            device_id,
            auto_block_enabled=data.auto_block_enabled,
            auto_block_threshold=data.auto_block_threshold,
            max_blocks_per_day=data.max_blocks_per_day,
        )
        self.db.commit()
        return DeviceSecurityPolicyRead.model_validate(policy)

    def list_client_blocks(self, device_id: int) -> List[ClientBlockedDomainRead]:
        self._require_device(device_id)
        blocks = self.block_repo.list_active_for_device(device_id)
        return [ClientBlockedDomainRead.model_validate(b) for b in blocks]

    def revoke_client_block(self, device_id: int, block_id: int) -> dict:
        self._require_device(device_id)
        block = self.block_repo.revoke(block_id, device_id=device_id)
        if not block:
            return {"revoked": False, "message": "Block not found"}
        self.db.commit()
        return {"revoked": True, "block_id": block_id}

    def recompute_baselines(self) -> int:
        return BehaviorBaselineService(self.db).recompute_all()

    def get_client_blocks_for_sync(self) -> ClientBlockSyncResponse:
        blocks = self.block_repo.list_active_for_sync()
        by_device: dict[int, ClientBlockSyncEntry] = {}
        for block in blocks:
            device = block.device
            if not device or not device.mac_address:
                continue
            tag = f"ng_device_{device.id}"
            entry = by_device.get(device.id)
            if not entry:
                entry = ClientBlockSyncEntry(
                    device_id=device.id,
                    mac_address=device.mac_address,
                    tag=tag,
                    domains=[],
                )
                by_device[device.id] = entry
            if block.domain not in entry.domains:
                entry.domains.append(block.domain)
        return ClientBlockSyncResponse(entries=list(by_device.values()))
