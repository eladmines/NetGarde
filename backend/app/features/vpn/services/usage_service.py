from datetime import datetime, timezone

from sqlalchemy.orm import Session

from app.features.dns_queries.repositories.dns_alert_repository import DnsAlertRepository
from app.features.vpn.repositories.device_usage_repository import DeviceUsageRepository
from app.features.vpn.schemas.usage import UsageReportRequest, UsageReportResponse
from app.shared.config import settings
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)

MIB = 1024 * 1024


class UsageService:
    def __init__(self, db: Session):
        self.db = db
        self.usage_repo = DeviceUsageRepository(db)
        self.alert_repo = DnsAlertRepository(db)

    def report_usage(self, payload: UsageReportRequest) -> UsageReportResponse:
        now = datetime.now(timezone.utc)
        total_delta = payload.delta_rx_bytes + payload.delta_tx_bytes
        rate_mib_per_sec = (total_delta / MIB) / payload.interval_sec

        self.usage_repo.create_sample(
            device_external_id=payload.device_id.strip(),
            recorded_at=now,
            interval_sec=payload.interval_sec,
            rx_bytes=payload.rx_bytes,
            tx_bytes=payload.tx_bytes,
            delta_rx_bytes=payload.delta_rx_bytes,
            delta_tx_bytes=payload.delta_tx_bytes,
        )

        alert_created = False
        if rate_mib_per_sec >= settings.BANDWIDTH_ALERT_MIB_PER_SEC:
            self.alert_repo.create(
                timestamp=now,
                client_ip="",
                alert_type="bandwidth_spike",
                severity="high",
                domain=None,
                root_domain=None,
                message=(
                    f"Device {payload.device_id}: "
                    f"{rate_mib_per_sec:.1f} MiB/s "
                    f"(down {payload.delta_rx_bytes / MIB:.1f} MiB, "
                    f"up {payload.delta_tx_bytes / MIB:.1f} MiB "
                    f"in {payload.interval_sec:.0f}s)"
                ),
            )
            alert_created = True

        self.db.commit()
        logger.info(
            "Usage sample stored",
            extra={
                "device_id": payload.device_id,
                "rate_mib_per_sec": round(rate_mib_per_sec, 2),
                "alert": alert_created,
            },
        )
        return UsageReportResponse(
            stored=True,
            alert_created=alert_created,
            rate_mib_per_sec=round(rate_mib_per_sec, 2),
        )
