from datetime import datetime, timedelta, timezone

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.features.client_behavior.models.client_behavior_profile import ClientBehaviorProfile
from app.features.dashboard.schemas.network_overview import NetworkOverviewRead, NetworkOverviewStats
from app.features.dashboard.services.overview_templates import build_network_overview_bullets
from app.features.dns_queries.models.dns_alert import DnsAlert
from app.features.dns_queries.models.dns_query import DnsQuery
from app.features.dns_queries.repositories.dns_query_repository import DnsQueryRepository
from app.features.policy.repositories.policy_repository import PolicyRepository
from app.features.vpn.services.usage_service import UsageService
from app.shared.config import settings


class NetworkOverviewService:
    def __init__(self, db: Session):
        self.db = db
        self.usage_service = UsageService(db)
        self.dns_repo = DnsQueryRepository(db)
        self.policy_repo = PolicyRepository(db)

    def build_overview(self, *, period_minutes: int = 60) -> NetworkOverviewRead:
        period = max(5, min(period_minutes, 24 * 60))
        now = datetime.now(timezone.utc)
        since = now - timedelta(minutes=period)

        live = self.usage_service.list_live_bandwidth()
        reporting = len(live.items)
        live_total = round(sum(item.total_mib_per_sec for item in live.items), 3)

        history = self.usage_service.list_usage_history(minutes=period)
        peak = 0.0
        for point in history.points:
            peak = max(peak, point.total_mib_per_sec)
        peak = round(peak, 3)

        alert_rows = (
            self.db.query(DnsAlert.alert_type, func.count(DnsAlert.id))
            .filter(DnsAlert.timestamp >= since)
            .group_by(DnsAlert.alert_type)
            .all()
        )
        alerts_by_type = {alert_type: int(count) for alert_type, count in alert_rows}
        alerts_total = sum(alerts_by_type.values())

        blocked_count = (
            self.db.query(DnsQuery)
            .filter(DnsQuery.timestamp >= since, DnsQuery.blocked.is_(True))
            .count()
        )
        top_blocked_rows = (
            self.db.query(DnsQuery.domain, func.count(DnsQuery.id).label("count"))
            .filter(DnsQuery.timestamp >= since, DnsQuery.blocked.is_(True))
            .group_by(DnsQuery.domain)
            .order_by(desc("count"))
            .limit(5)
            .all()
        )
        top_blocked = [{"domain": domain, "count": int(count)} for domain, count in top_blocked_rows]

        enabled_packs = [p for p in self.policy_repo.list_packs() if p.enabled_globally]
        pack_names = [p.name for p in enabled_packs]

        threshold = settings.BEHAVIOR_ALERT_THRESHOLD
        elevated_count = (
            self.db.query(ClientBehaviorProfile)
            .filter(ClientBehaviorProfile.last_score.isnot(None))
            .filter(ClientBehaviorProfile.last_score >= threshold)
            .count()
        )

        snapshot = {
            "period_minutes": period,
            "live": {"reporting": reporting, "total_mib_per_sec": live_total},
            "history": {"peak_mib_per_sec": peak},
            "alerts": {"total": alerts_total, "by_type": alerts_by_type},
            "blocked": {"count": blocked_count, "top_domains": top_blocked},
            "policy": {"enabled_pack_names": pack_names},
            "behavior": {"elevated_count": elevated_count, "threshold": threshold},
        }

        bullets = build_network_overview_bullets(snapshot)
        stats = NetworkOverviewStats(
            reporting_clients=reporting,
            live_total_mib_per_sec=live_total,
            peak_mib_per_sec=peak,
            alerts_total=alerts_total,
            blocked_queries=blocked_count,
            enabled_policy_packs=len(enabled_packs),
            elevated_behavior_clients=elevated_count,
        )

        return NetworkOverviewRead(
            generated_at=now,
            period_minutes=period,
            bullets=bullets,
            stats=stats,
        )
