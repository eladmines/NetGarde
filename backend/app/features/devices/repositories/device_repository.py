from sqlalchemy.orm import Session, joinedload
from datetime import datetime, timezone
from typing import List, Optional, Dict

from app.features.devices.models.device import Device
from app.features.devices.schemas.device import DeviceCreate, DeviceUpdate, DhcpLeaseRecord
from app.features.vpn.models.ip_lease import IpLease


class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: DeviceCreate) -> Device:
        device = Device(**data.model_dump())
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def get_all(self) -> List[Device]:
        return (
            self.db.query(Device)
            .options(joinedload(Device.ip_lease))
            .join(IpLease, Device.ip_lease_id == IpLease.id)
            .order_by(IpLease.ip.asc())
            .all()
        )

    def get_by_id(self, device_id: int) -> Optional[Device]:
        return (
            self.db.query(Device)
            .options(joinedload(Device.ip_lease))
            .filter(Device.id == device_id)
            .first()
        )

    def get_by_client_ip(self, client_ip: str) -> Optional[Device]:
        return (
            self.db.query(Device)
            .options(joinedload(Device.ip_lease))
            .join(IpLease, Device.ip_lease_id == IpLease.id)
            .filter(IpLease.ip == client_ip, IpLease.released_at.is_(None))
            .first()
        )

    def get_by_mac_address(self, mac_address: str) -> Optional[Device]:
        return (
            self.db.query(Device)
            .options(joinedload(Device.ip_lease))
            .filter(Device.mac_address == mac_address.lower())
            .first()
        )

    def update(self, device_id: int, data: DeviceUpdate) -> Optional[Device]:
        device = self.get_by_id(device_id)
        if not device:
            return None

        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(device, key, value)

        device.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(device)
        return device

    def delete(self, device_id: int) -> bool:
        device = self.get_by_id(device_id)
        if not device:
            return False

        self.db.delete(device)
        self.db.commit()
        return True

    def upsert_from_dhcp_lease(self, lease: DhcpLeaseRecord) -> str:
        """
        Upsert when client_ip matches an active VPN lease IP.
        Returns 'created', 'updated', or 'skipped' if no matching lease.
        """
        il = (
            self.db.query(IpLease)
            .filter(IpLease.ip == lease.client_ip, IpLease.released_at.is_(None))
            .first()
        )
        if not il:
            return "skipped"

        device = None
        if lease.mac_address:
            device = self.get_by_mac_address(lease.mac_address)

        if not device:
            device = self.db.query(Device).filter(Device.ip_lease_id == il.id).first()

        now = datetime.now(timezone.utc)
        if device:
            device.ip_lease_id = il.id
            if lease.hostname:
                device.hostname = lease.hostname
            if lease.mac_address:
                device.mac_address = lease.mac_address
            device.source = "dhcp_lease"
            device.updated_at = now
            self.db.commit()
            return "updated"

        new_device = Device(
            ip_lease_id=il.id,
            hostname=lease.hostname,
            mac_address=lease.mac_address,
            source="dhcp_lease",
            created_at=now,
            updated_at=now,
        )
        self.db.add(new_device)
        self.db.commit()
        return "created"

    def get_hostname_map_by_client_ips(self, client_ips: List[str]) -> Dict[str, Optional[str]]:
        if not client_ips:
            return {}

        rows = (
            self.db.query(IpLease.ip, Device.hostname)
            .join(Device, Device.ip_lease_id == IpLease.id)
            .filter(IpLease.ip.in_(client_ips), IpLease.released_at.is_(None))
            .all()
        )
        return {ip: hostname for ip, hostname in rows}

    def get_identity_map_by_client_ips(self, client_ips: List[str]) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Map client IP (VPN inner IP when queries exit through the tunnel) to device identity.
        """
        if not client_ips:
            return {}

        rows = (
            self.db.query(IpLease.ip, Device.hostname)
            .join(Device, Device.ip_lease_id == IpLease.id)
            .filter(IpLease.ip.in_(client_ips), IpLease.released_at.is_(None))
            .all()
        )
        return {
            ip: {"device_name": hostname, "device_vendor": None, "user_name": None}
            for ip, hostname in rows
        }

    def ensure_devices_for_client_ips(self, client_ips: List[str], source: str = "dns_observed") -> int:
        """Create device rows for client IPs that match an active lease and have no device yet."""
        unique_ips = sorted({ip.strip() for ip in client_ips if ip and ip.strip()})
        if not unique_ips:
            return 0

        now = datetime.now(timezone.utc)
        created = 0

        for ip in unique_ips:
            lease = (
                self.db.query(IpLease)
                .filter(IpLease.ip == ip, IpLease.released_at.is_(None))
                .first()
            )
            if not lease:
                continue
            exists = self.db.query(Device.id).filter(Device.ip_lease_id == lease.id).first()
            if exists:
                continue
            self.db.add(
                Device(
                    ip_lease_id=lease.id,
                    source=source,
                    created_at=now,
                    updated_at=now,
                )
            )
            created += 1

        if created:
            self.db.commit()
        return created
