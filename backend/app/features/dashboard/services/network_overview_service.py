from datetime import datetime, timedelta, timezone
from typing import Any, Literal, Optional

from sqlalchemy import desc, func
from sqlalchemy.orm import Session

from app.features.client_behavior.models.client_behavior_profile import ClientBehaviorProfile
from app.features.dashboard.schemas.network_overview import NetworkOverviewRead, NetworkOverviewStats
from app.features.dashboard.services import network_overview_cache
from app.features.dashboard.services.overview_templates import build_network_overview_bullets
from app.features.dns_queries.models.dns_alert import DnsAlert
from app.features.dns_queries.models.dns_query import DnsQuery
from app.features.dns_queries.repositories.dns_query_repository import DnsQueryRepository
from app.features.policy.repositories.policy_repository import PolicyRepository
from app.features.vpn.services.usage_service import UsageService
from app.shared.config import settings
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)

OverviewSource = Literal["template", "llm"]


class NetworkOverviewService:
    def __init__(self, db: Session):
        self.db = db
        self.usage_service = UsageService(db)
        self.dns_repo = DnsQueryRepository(db)
        self.policy_repo = PolicyRepository(db)

    def build_overview(self, *, period_minutes: int = 60, refresh: bool = False) -> NetworkOverviewRead:
        period = max(5, min(period_minutes, 24 * 60))

        if not refresh:
            cached = network_overview_cache.get_cached_overview(period)
            if cached is not None:
                return cached

        now = datetime.now(timezone.utc)
        snapshot = self._build_snapshot(period=period, now=now)
        bullets, source, llm_model = self._resolve_bullets(snapshot)

        stats = NetworkOverviewStats(
            reporting_clients=int(snapshot["live"]["reporting"]),
            live_total_mib_per_sec=float(snapshot["live"]["total_mib_per_sec"]),
            peak_mib_per_sec=float(snapshot["history"]["peak_mib_per_sec"]),
            alerts_total=int(snapshot["alerts"]["total"]),
            blocked_queries=int(snapshot["blocked"]["count"]),
            enabled_policy_packs=len(snapshot["policy"]["enabled_pack_names"]),
            elevated_behavior_clients=int(snapshot["behavior"]["elevated_count"]),
        )

        overview = NetworkOverviewRead(
            generated_at=now,
            period_minutes=period,
            bullets=bullets,
            stats=stats,
            source=source,
            llm_model=llm_model,
            review_mode=settings.NETWORK_REVIEW_MODE.strip().lower() or "template",
        )
        network_overview_cache.set_cached_overview(overview, period)
        return overview

    def _build_snapshot(self, *, period: int, now: datetime) -> dict[str, Any]:
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

        return {
            "period_minutes": period,
            "live": {"reporting": reporting, "total_mib_per_sec": live_total},
            "history": {"peak_mib_per_sec": peak},
            "alerts": {"total": alerts_total, "by_type": alerts_by_type},
            "blocked": {"count": blocked_count, "top_domains": top_blocked},
            "policy": {"enabled_pack_names": pack_names},
            "behavior": {"elevated_count": elevated_count, "threshold": threshold},
        }

    def _resolve_bullets(self, snapshot: dict[str, Any]) -> tuple[list[str], OverviewSource, Optional[str]]:
        mode = settings.NETWORK_REVIEW_MODE.strip().lower()
        if mode == "template":
            return build_network_overview_bullets(snapshot), "template", None

        llm_model: Optional[str] = None
        try:
            if mode == "openai":
                from app.features.dashboard.services import openai_llm_client

                llm_model = settings.OPENAI_MODEL
                bullets = openai_llm_client.summarize_network_review(snapshot)
                return bullets, "llm", llm_model
            if mode == "ollama":
                from app.features.dashboard.services import ollama_llm_client

                llm_model = settings.OLLAMA_MODEL
                bullets = ollama_llm_client.summarize_network_review(snapshot)
                return bullets, "llm", llm_model
            logger.warning("Unknown NETWORK_REVIEW_MODE=%s, using template", mode)
        except Exception as exc:
            logger.warning("LLM network review failed, using template fallback: %s", exc)

        return build_network_overview_bullets(snapshot), "template", None
