from datetime import datetime, timedelta, timezone
from typing import List, Optional, Tuple

from sqlalchemy.orm import Session

from app.features.client_behavior.behavior_whitelist import is_whitelisted_root
from app.features.client_behavior.repositories.behavior_profile_repository import BehaviorProfileRepository
from app.features.client_behavior.repositories.behavior_rollup_repository import BehaviorRollupRepository
from app.features.client_behavior.repositories.client_blocked_domain_repository import ClientBlockedDomainRepository
from app.features.client_behavior.repositories.device_security_policy_repository import DeviceSecurityPolicyRepository
from app.features.client_behavior.services.behavior_baseline_service import BehaviorBaselineService
from app.features.devices.repositories.device_repository import DeviceRepository
from app.features.dns_queries.dns_anomaly import get_suspicious_domain_reasons
from app.features.dns_queries.models.dns_alert import DnsAlert
from app.features.dns_queries.repositories.dns_alert_repository import DnsAlertRepository
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate
from app.shared.config import settings
from app.shared.domain_utils import extract_root_domain, is_noise_domain
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class BehaviorScoringService:
    """Score recent activity vs baseline; alert and optionally auto-block per device."""

    def __init__(self, db: Session):
        self.db = db
        self.rollup_repo = BehaviorRollupRepository(db)
        self.profile_repo = BehaviorProfileRepository(db)
        self.policy_repo = DeviceSecurityPolicyRepository(db)
        self.block_repo = ClientBlockedDomainRepository(db)
        self.alert_repo = DnsAlertRepository(db)
        self.device_repo = DeviceRepository(db)
        self.baseline_service = BehaviorBaselineService(db)

    def process_queries(self, queries: List[DnsQueryCreate]) -> int:
        if not queries:
            return 0

        device_domains: dict[int, List[Tuple[str, str, str]]] = {}
        for q in queries:
            if is_noise_domain(q.domain):
                continue
            device = self.device_repo.get_by_client_ip(q.client_ip)
            if not device:
                continue
            root = extract_root_domain(q.domain)
            device_domains.setdefault(device.id, []).append((q.client_ip, q.domain, root))

        alerts = 0
        for device_id, entries in device_domains.items():
            alerts += self._score_device(device_id, entries)
        return alerts

    def _score_device(self, device_id: int, entries: List[Tuple[str, str, str]]) -> int:
        profile = self.profile_repo.get_by_device_id(device_id)
        if not profile or not profile.profile_ready:
            if self._should_recompute_baseline(profile):
                self.baseline_service.recompute_device(device_id)
                profile = self.profile_repo.get_by_device_id(device_id)
            if not profile or not profile.profile_ready:
                return 0

        baseline = self.profile_repo.parse_baseline(profile)
        window_min = settings.BEHAVIOR_SCORE_WINDOW_MINUTES
        since = datetime.now(timezone.utc) - timedelta(minutes=window_min)
        query_count, _, new_roots = self.rollup_repo.sum_recent_window(device_id, since)

        score, reasons, top_domain = self._compute_score(
            baseline, query_count, new_roots, entries
        )
        self.profile_repo.update_score(device_id, score)

        alert_threshold = settings.BEHAVIOR_ALERT_THRESHOLD
        if score < alert_threshold:
            return 0

        cooldown_since = datetime.now(timezone.utc) - timedelta(
            minutes=settings.BEHAVIOR_SCORE_WINDOW_MINUTES
        )
        recent_alert = (
            self.db.query(DnsAlert)
            .filter(
                DnsAlert.device_id == device_id,
                DnsAlert.alert_type == "behavior_anomaly",
                DnsAlert.timestamp >= cooldown_since,
            )
            .first()
        )
        if recent_alert:
            return 0

        client_ip = entries[0][0]
        message = f"Behavior score {score}: " + "; ".join(reasons)
        if top_domain:
            message += f" (top domain: {top_domain})"

        self.alert_repo.create(
            timestamp=datetime.now(timezone.utc),
            client_ip=client_ip,
            alert_type="behavior_anomaly",
            severity="high" if score >= 85 else "medium",
            domain=top_domain,
            root_domain=extract_root_domain(top_domain) if top_domain else None,
            message=message,
            device_id=device_id,
        )

        policy = self.policy_repo.get_or_create(device_id)
        block_threshold = policy.auto_block_threshold or settings.BEHAVIOR_AUTO_BLOCK_THRESHOLD
        if (
            policy.auto_block_enabled
            and score >= block_threshold
            and top_domain
            and not is_whitelisted_root(extract_root_domain(top_domain))
        ):
            self._maybe_auto_block(device_id, top_domain, score)

        return 1

    def _should_recompute_baseline(self, profile) -> bool:
        if profile is None:
            return True
        if profile.updated_at is None:
            return True
        age = datetime.now(timezone.utc) - profile.updated_at
        return age > timedelta(hours=settings.BEHAVIOR_BASELINE_RECOMPUTE_HOURS)

    def _compute_score(
        self,
        baseline: dict,
        query_count: int,
        new_roots: int,
        entries: List[Tuple[str, str, str]],
    ) -> Tuple[int, List[str], Optional[str]]:
        reasons: List[str] = []
        points = 0

        median = float(baseline.get("median_queries_per_hour", 1) or 1)
        mad = float(baseline.get("mad_queries_per_hour", 1) or 1)
        window_min = max(1, settings.BEHAVIOR_SCORE_WINDOW_MINUTES)
        expected = median * (window_min / 60.0)
        threshold = expected + 5 * mad
        if query_count > max(threshold, expected * 5):
            reasons.append(f"query volume {query_count} vs expected ~{expected:.0f}")
            points += 35

        p95_new = float(baseline.get("p95_new_roots_per_hour", 3) or 3)
        scaled_p95 = p95_new * (window_min / 60.0)
        if new_roots >= max(10, scaled_p95 * 3):
            reasons.append(f"new root burst {new_roots} in {window_min}m")
            points += 35

        now = datetime.now(timezone.utc)
        hour_hist = baseline.get("hour_histogram") or {}
        hist_count = int(hour_hist.get(now.hour, hour_hist.get(str(now.hour), 0)))
        total_hist = sum(int(v) for v in hour_hist.values()) or 1
        if hist_count == 0 and query_count >= 20:
            reasons.append(f"unusual activity at hour {now.hour} UTC")
            points += 15

        top_domain: Optional[str] = None
        for _ip, domain, root in entries:
            if get_suspicious_domain_reasons(domain):
                reasons.append(f"suspicious domain {domain}")
                points += 25
                top_domain = domain
                break
            if not is_whitelisted_root(root) and top_domain is None:
                top_domain = domain

        if top_domain is None and entries:
            top_domain = entries[-1][1]

        return min(100, points), reasons, top_domain

    def _maybe_auto_block(self, device_id: int, domain: str, score: int) -> None:
        policy = self.policy_repo.get_or_create(device_id)
        if self.block_repo.count_blocks_today(device_id) >= policy.max_blocks_per_day:
            logger.info("Auto-block skipped: daily limit", extra={"device_id": device_id})
            return

        root = extract_root_domain(domain)
        ttl_hours = settings.BEHAVIOR_AUTO_BLOCK_TTL_HOURS
        expires = datetime.now(timezone.utc) + timedelta(hours=ttl_hours)
        self.block_repo.create_block(
            device_id=device_id,
            domain=domain.lower(),
            root_domain=root,
            source="behavior_auto",
            score=score,
            expires_at=expires,
        )
        logger.info(
            "Behavior auto-block created",
            extra={"device_id": device_id, "domain": domain, "score": score},
        )
