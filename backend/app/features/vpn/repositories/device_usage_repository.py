from datetime import datetime, timedelta, timezone
from typing import NamedTuple, Optional

from sqlalchemy import and_, func
from sqlalchemy.orm import Session

from app.features.devices.models.device import Device
from app.features.vpn.models.device_usage_sample import DeviceUsageSample
from app.features.vpn.models.ip_lease import IpLease
from app.features.vpn.models.vpn_peer import VpnPeer


class UsageSampleWithDevice(NamedTuple):
    sample: DeviceUsageSample
    device_id: Optional[int]
    client_ip: Optional[str]


class DeviceUsageRepository:
    def __init__(self, db: Session):
        self.db = db

    def create_sample(
        self,
        *,
        device_external_id: str,
        recorded_at: datetime,
        interval_sec: float,
        rx_bytes: int,
        tx_bytes: int,
        delta_rx_bytes: int,
        delta_tx_bytes: int,
    ) -> DeviceUsageSample:
        sample = DeviceUsageSample(
            device_external_id=device_external_id,
            recorded_at=recorded_at,
            interval_sec=interval_sec,
            rx_bytes=rx_bytes,
            tx_bytes=tx_bytes,
            delta_rx_bytes=delta_rx_bytes,
            delta_tx_bytes=delta_tx_bytes,
        )
        self.db.add(sample)
        self.db.flush()
        return sample

    def list_latest_with_device_since(self, since: datetime) -> list[UsageSampleWithDevice]:
        """Most recent usage sample per VPN device_id with optional registered Device row."""
        latest = (
            self.db.query(
                DeviceUsageSample.device_external_id,
                func.max(DeviceUsageSample.id).label("max_id"),
            )
            .filter(DeviceUsageSample.recorded_at >= since)
            .group_by(DeviceUsageSample.device_external_id)
            .subquery()
        )
        rows = (
            self.db.query(DeviceUsageSample, Device.id, IpLease.ip)
            .join(latest, DeviceUsageSample.id == latest.c.max_id)
            .outerjoin(VpnPeer, VpnPeer.device_id == DeviceUsageSample.device_external_id)
            .outerjoin(
                IpLease,
                and_(IpLease.peer_id == VpnPeer.id, IpLease.released_at.is_(None)),
            )
            .outerjoin(Device, Device.ip_lease_id == IpLease.id)
            .order_by(DeviceUsageSample.recorded_at.desc())
            .all()
        )
        return [
            UsageSampleWithDevice(sample=sample, device_id=device_id, client_ip=client_ip)
            for sample, device_id, client_ip in rows
        ]

    def delete_older_than(self, days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        count = (
            self.db.query(DeviceUsageSample)
            .filter(DeviceUsageSample.recorded_at < cutoff)
            .delete()
        )
        self.db.commit()
        return count
