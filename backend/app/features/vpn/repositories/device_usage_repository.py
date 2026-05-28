from sqlalchemy.orm import Session
from datetime import datetime, timedelta, timezone
from app.features.vpn.models.device_usage_sample import DeviceUsageSample


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

    def delete_older_than(self, days: int) -> int:
        cutoff = datetime.now(timezone.utc) - timedelta(days=days)
        count = (
            self.db.query(DeviceUsageSample)
            .filter(DeviceUsageSample.recorded_at < cutoff)
            .delete()
        )
        self.db.commit()
        return count
