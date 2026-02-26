from sqlalchemy.orm import Session
from datetime import datetime, timezone
from typing import List, Optional, Dict

from app.features.devices.models.device import Device
from app.features.devices.schemas.device import DeviceCreate, DeviceUpdate, DhcpLeaseRecord
from app.shared.mac_vendor import infer_vendor_from_mac


class DeviceRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: DeviceCreate) -> Device:
        payload = data.model_dump()
        payload["vendor"] = infer_vendor_from_mac(payload.get("mac_address"))
        device = Device(**payload)
        self.db.add(device)
        self.db.commit()
        self.db.refresh(device)
        return device

    def get_all(self, active_only: bool = False) -> List[Device]:
        query = self.db.query(Device)
        if active_only:
            query = query.filter(Device.is_active == True)
        return query.order_by(Device.hostname.asc().nulls_last(), Device.client_ip.asc()).all()

    def get_by_id(self, device_id: int) -> Optional[Device]:
        return self.db.query(Device).filter(Device.id == device_id).first()

    def get_by_client_ip(self, client_ip: str) -> Optional[Device]:
        return self.db.query(Device).filter(Device.client_ip == client_ip).first()

    def get_by_mac_address(self, mac_address: str) -> Optional[Device]:
        return self.db.query(Device).filter(Device.mac_address == mac_address.lower()).first()

    def update(self, device_id: int, data: DeviceUpdate) -> Optional[Device]:
        device = self.get_by_id(device_id)
        if not device:
            return None

        updates = data.model_dump(exclude_unset=True)
        if "mac_address" in updates:
            updates["vendor"] = infer_vendor_from_mac(updates.get("mac_address"))
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
        """Upsert device based on MAC address first, then client IP. Returns 'created' or 'updated'."""
        device = None

        if lease.mac_address:
            device = self.get_by_mac_address(lease.mac_address)

        if not device:
            device = self.get_by_client_ip(lease.client_ip)

        now = datetime.now(timezone.utc)
        if device:
            device.client_ip = lease.client_ip
            if lease.hostname:
                device.hostname = lease.hostname
            if lease.mac_address:
                device.mac_address = lease.mac_address
                device.vendor = infer_vendor_from_mac(lease.mac_address)
            device.source = "dhcp_lease"
            device.is_active = True
            device.updated_at = now
            self.db.commit()
            return "updated"

        new_device = Device(
            client_ip=lease.client_ip,
            hostname=lease.hostname,
            mac_address=lease.mac_address,
            vendor=infer_vendor_from_mac(lease.mac_address),
            source="dhcp_lease",
            is_active=True,
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
            self.db.query(Device.client_ip, Device.hostname)
            .filter(Device.client_ip.in_(client_ips))
            .all()
        )
        return {ip: hostname for ip, hostname in rows}

    def get_identity_map_by_client_ips(self, client_ips: List[str]) -> Dict[str, Dict[str, Optional[str]]]:
        """
        Return a mapping of client IP to device identity fields:
        {
            "10.0.0.2": {"device_name": "Mines-Laptop", "device_vendor": "Dell"}
        }
        """
        if not client_ips:
            return {}

        rows = (
            self.db.query(Device.client_ip, Device.hostname, Device.vendor)
            .filter(Device.client_ip.in_(client_ips))
            .all()
        )
        return {
            ip: {"device_name": hostname, "device_vendor": vendor}
            for ip, hostname, vendor in rows
        }
