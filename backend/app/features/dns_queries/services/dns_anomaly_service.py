from typing import List

from sqlalchemy.orm import Session

from app.features.dns_queries.dns_anomaly import get_suspicious_domain_reasons
from app.features.dns_queries.repositories.dns_alert_repository import DnsAlertRepository
from app.features.dns_queries.repositories.domain_first_seen_repository import DomainFirstSeenRepository
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate
from app.shared.config import settings
from app.shared.domain_utils import extract_root_domain, is_noise_domain
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class DnsAnomalyService:
    def __init__(self, db: Session):
        self.db = db
        self.alert_repo = DnsAlertRepository(db)
        self.first_seen_repo = DomainFirstSeenRepository(db)

    def process_queries(self, queries: List[DnsQueryCreate]) -> int:
        created = 0
        for query in queries:
            if is_noise_domain(query.domain):
                continue
            created += self._process_one(query)
        if created:
            self.db.commit()
            logger.info("DNS anomaly alerts created", extra={"count": created})
        return created

    def _process_one(self, query: DnsQueryCreate) -> int:
        alerts = 0
        root = extract_root_domain(query.domain)

        if query.blocked:
            self.alert_repo.create(
                timestamp=query.timestamp,
                client_ip=query.client_ip,
                alert_type="blocked_attempt",
                severity="high",
                domain=query.domain,
                root_domain=root,
                message=f"Blocked DNS query for {query.domain}",
            )
            alerts += 1

        existing = self.first_seen_repo.get(query.client_ip, root)
        if existing is None:
            self.first_seen_repo.record_first_seen(
                query.client_ip,
                root,
                query.timestamp,
            )
            if settings.NEW_DOMAIN_ALERTS:
                self.alert_repo.create(
                    timestamp=query.timestamp,
                    client_ip=query.client_ip,
                    alert_type="new_domain",
                    severity="low",
                    domain=query.domain,
                    root_domain=root,
                    message=f"First visit to {root} from {query.client_ip}",
                )
                alerts += 1

        suspicious_reasons = get_suspicious_domain_reasons(query.domain)
        if suspicious_reasons:
            self.alert_repo.create(
                timestamp=query.timestamp,
                client_ip=query.client_ip,
                alert_type="suspicious_domain",
                severity="high",
                domain=query.domain,
                root_domain=root,
                message="; ".join(suspicious_reasons),
            )
            alerts += 1

        return alerts
