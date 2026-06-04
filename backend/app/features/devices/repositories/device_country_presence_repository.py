from datetime import datetime, timezone
from typing import Dict, List, Optional, Set

from sqlalchemy.orm import Session

from app.features.devices.models.device_country_presence import DeviceCountryPresence

_SKIP_CODES: Set[str] = {"GLOBAL", "UNKNOWN"}


class DeviceCountryPresenceRepository:
    def __init__(self, db: Session):
        self.db = db

    def list_for_device(self, device_id: int) -> List[DeviceCountryPresence]:
        return (
            self.db.query(DeviceCountryPresence)
            .filter(DeviceCountryPresence.device_id == device_id)
            .order_by(DeviceCountryPresence.query_count.desc())
            .all()
        )

    def known_codes(self, device_id: int) -> Set[str]:
        rows = (
            self.db.query(DeviceCountryPresence.country_code)
            .filter(DeviceCountryPresence.device_id == device_id)
            .all()
        )
        return {code for (code,) in rows}

    def record_batch(
        self,
        device_id: int,
        country_counts: Dict[str, int],
        *,
        now: Optional[datetime] = None,
    ) -> List[str]:
        """
        Upsert country activity. Returns country codes that were newly recorded for this device.
        """
        if not country_counts:
            return []

        ts = now or datetime.now(timezone.utc)
        newly_seen: List[str] = []

        for raw_code, count in country_counts.items():
            code = (raw_code or "").strip().upper()
            if not code or code in _SKIP_CODES or count <= 0:
                continue

            row = (
                self.db.query(DeviceCountryPresence)
                .filter(
                    DeviceCountryPresence.device_id == device_id,
                    DeviceCountryPresence.country_code == code,
                )
                .first()
            )
            if row is None:
                self.db.add(
                    DeviceCountryPresence(
                        device_id=device_id,
                        country_code=code,
                        first_seen_at=ts,
                        last_seen_at=ts,
                        query_count=int(count),
                    )
                )
                newly_seen.append(code)
            else:
                row.query_count += int(count)
                row.last_seen_at = ts

        return newly_seen
