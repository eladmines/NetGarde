from datetime import datetime, timedelta, timezone
from typing import List, Optional

from sqlalchemy.orm import Session, joinedload

from app.features.devices.models.device import Device
from app.features.policy.models.device_quarantine import DeviceQuarantine
from app.features.policy.models.policy_pack import PolicyPack
from app.features.policy.models.policy_profile import PolicyProfile
from app.features.vpn.models.ip_lease import IpLease


class PolicyRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_packs(self) -> List[PolicyPack]:
        return self.db.query(PolicyPack).order_by(PolicyPack.slug).all()

    def get_pack_by_slug(self, slug: str) -> Optional[PolicyPack]:
        return self.db.query(PolicyPack).filter(PolicyPack.slug == slug).first()

    def list_profiles(self) -> List[PolicyProfile]:
        return self.db.query(PolicyProfile).order_by(PolicyProfile.slug).all()

    def get_profile_by_id(self, profile_id: int) -> Optional[PolicyProfile]:
        return self.db.query(PolicyProfile).filter(PolicyProfile.id == profile_id).first()

    def get_profile_by_slug(self, slug: str) -> Optional[PolicyProfile]:
        return self.db.query(PolicyProfile).filter(PolicyProfile.slug == slug).first()

    def get_default_profile(self) -> Optional[PolicyProfile]:
        return self.get_profile_by_slug("teen")

    def update_pack_global(self, slug: str, enabled: bool) -> Optional[PolicyPack]:
        pack = self.get_pack_by_slug(slug)
        if not pack:
            return None
        pack.enabled_globally = enabled
        return pack

    def update_profile(self, profile_id: int, **fields) -> Optional[PolicyProfile]:
        profile = self.get_profile_by_id(profile_id)
        if not profile or profile.is_builtin:
            return None
        for key, value in fields.items():
            if value is not None and hasattr(profile, key):
                setattr(profile, key, value)
        return profile

    def assign_profile_to_device(self, device_id: int, profile_id: Optional[int]) -> Optional[Device]:
        device = (
            self.db.query(Device)
            .options(joinedload(Device.ip_lease))
            .filter(Device.id == device_id)
            .first()
        )
        if not device:
            return None
        device.policy_profile_id = profile_id
        return device

    def list_devices_for_dns_sync(self) -> List[Device]:
        return (
            self.db.query(Device)
            .options(joinedload(Device.ip_lease))
            .join(IpLease, Device.ip_lease_id == IpLease.id)
            .filter(Device.mac_address.isnot(None), IpLease.released_at.is_(None))
            .all()
        )

    def get_active_quarantine(self, device_id: int) -> Optional[DeviceQuarantine]:
        now = datetime.now(timezone.utc)
        return (
            self.db.query(DeviceQuarantine)
            .filter(
                DeviceQuarantine.device_id == device_id,
                DeviceQuarantine.ended_at.is_(None),
                DeviceQuarantine.expires_at > now,
            )
            .order_by(DeviceQuarantine.expires_at.desc())
            .first()
        )

    def start_quarantine(self, device_id: int, score: int, hours: int) -> DeviceQuarantine:
        now = datetime.now(timezone.utc)
        existing = self.get_active_quarantine(device_id)
        expires = now + timedelta(hours=hours)
        if existing:
            existing.score = score
            if existing.expires_at < expires:
                existing.expires_at = expires
            return existing
        row = DeviceQuarantine(device_id=device_id, score=score, started_at=now, expires_at=expires)
        self.db.add(row)
        self.db.flush()
        return row

    def end_expired_quarantines(self) -> int:
        now = datetime.now(timezone.utc)
        rows = (
            self.db.query(DeviceQuarantine)
            .filter(DeviceQuarantine.ended_at.is_(None), DeviceQuarantine.expires_at <= now)
            .all()
        )
        for row in rows:
            row.ended_at = now
        return len(rows)
