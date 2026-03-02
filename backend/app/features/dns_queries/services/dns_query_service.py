from typing import List, Optional
from datetime import datetime
from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session
from app.features.dns_queries.repositories.dns_query_repository import DnsQueryRepository
from app.features.dns_queries.schemas.dns_query import DnsQueryCreate, DnsQueryResponse
from app.features.dns_queries.services.dns_query_service_interface import IDnsQueryService
from app.features.devices.repositories.device_repository import DeviceRepository
from app.features.categories.models.category import Category
from app.features.domain_categories.repositories.domain_category_repository import DomainCategoryRepository
from app.features.domain_categories.schemas.domain_category import DomainCategoryCreate
from app.features.domain_classification_jobs.repositories.domain_classification_job_repository import (
    DomainClassificationJobRepository,
)
from app.shared.domain_classifier import classify_domain_category
from app.shared.domain_utils import extract_root_domain
from app.shared.config import settings
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class DnsQueryService:
    """Implementation of IDnsQueryService."""

    def create_query(self, dns_query_data: DnsQueryCreate, db: Session) -> DnsQueryResponse:
        repository = DnsQueryRepository(db)
        logger.info("Creating DNS query", extra={"domain": dns_query_data.domain})
        dns_query = repository.create(dns_query_data)
        self._classify_and_cache_domains([dns_query_data], db)
        logger.info("DNS query created", extra={"id": getattr(dns_query, "id", None)})
        return DnsQueryResponse.model_validate(dns_query)

    def bulk_create_queries(self, queries: List[DnsQueryCreate], db: Session) -> dict:
        repository = DnsQueryRepository(db)
        logger.info("Bulk creating DNS queries", extra={"count": len(queries)})
        count = repository.bulk_create(queries)
        self._classify_and_cache_domains(queries, db)
        logger.info("Bulk DNS queries created", extra={"inserted": count})
        return {"inserted": count}

    @staticmethod
    def _get_or_create_category_id(category_name: str, db: Session) -> int:
        category = (
            db.query(Category)
            .filter(Category.name == category_name, Category.is_deleted.is_(False))
            .first()
        )
        if category:
            return category.id

        try:
            category = Category(name=category_name, created_by=1, updated_by=1)
            db.add(category)
            db.commit()
            db.refresh(category)
            return category.id
        except IntegrityError:
            db.rollback()
            existing = (
                db.query(Category)
                .filter(Category.name == category_name, Category.is_deleted.is_(False))
                .first()
            )
            if existing:
                return existing.id
            raise

    def _classify_and_cache_domains(self, queries: List[DnsQueryCreate], db: Session) -> None:
        """
        Classify unseen root domains and cache the mapping in domain_categories.
        This runs best-effort and never fails DNS ingestion.
        """
        try:
            root_domains = sorted(
                {
                    extract_root_domain(q.domain.strip().lower())
                    for q in queries
                    if q.domain and q.domain.strip()
                }
            )
            if not root_domains:
                return

            mapping_repo = DomainCategoryRepository(db)
            mapped_domains = mapping_repo.get_mapped_domains(root_domains)
            new_domains = [d for d in root_domains if d not in mapped_domains]
            if not new_domains:
                return

            if settings.AI_CLASSIFIER_ENABLED:
                job_repo = DomainClassificationJobRepository(db)
                for domain in new_domains:
                    try:
                        job_repo.enqueue(domain)
                    except Exception:
                        db.rollback()
                        logger.warning("Failed to enqueue domain classification job", extra={"domain": domain}, exc_info=True)
                logger.info("Domain classification jobs enqueued", extra={"new_domains": len(new_domains)})
                return

            for domain in new_domains:
                category_name, confidence, source = classify_domain_category(domain)
                category_id = self._get_or_create_category_id(category_name, db)
                payload = DomainCategoryCreate(
                    domain=domain,
                    category_id=category_id,
                    confidence=confidence,
                    source=source,
                    created_by=1,
                    updated_by=1,
                )
                try:
                    mapping_repo.create(payload)
                except IntegrityError:
                    db.rollback()
                except Exception:
                    db.rollback()
                    logger.warning("Failed to cache domain classification", extra={"domain": domain}, exc_info=True)

            logger.info("Heuristic domain classification cache updated", extra={"new_domains": len(new_domains)})
        except Exception:
            logger.warning("Domain classification pass failed", exc_info=True)

    def get_queries(
        self,
        db: Session,
        page: int = 1,
        page_size: int = 50,
        domain_search: Optional[str] = None,
        client_ip: Optional[str] = None,
        blocked_only: bool = False,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        repository = DnsQueryRepository(db)
        items, total = repository.get_all(
            page=page,
            page_size=page_size,
            domain_search=domain_search,
            client_ip=client_ip,
            blocked_only=blocked_only,
            start_date=start_date,
            end_date=end_date
        )
        client_ips = list({item.client_ip for item in items})
        identity_map = DeviceRepository(db).get_identity_map_by_client_ips(client_ips)
        logger.info("Fetched DNS queries", extra={"count": len(items), "total": total, "page": page})
        return {
            "items": [
                DnsQueryResponse.model_validate(item).model_copy(
                    update=identity_map.get(
                        item.client_ip,
                        {"device_name": None, "device_vendor": None}
                    )
                )
                for item in items
            ],
            "total": total,
            "page": page,
            "page_size": page_size,
            "pages": (total + page_size - 1) // page_size
        }

    def get_stats(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None
    ) -> dict:
        repository = DnsQueryRepository(db)
        logger.info("Fetching DNS stats")
        return repository.get_stats(start_date=start_date, end_date=end_date)

    def get_unique_clients(self, db: Session) -> List[str]:
        repository = DnsQueryRepository(db)
        logger.info("Fetching unique clients")
        return repository.get_unique_clients()

    def cleanup_old_records(self, db: Session, days: int = 30) -> dict:
        repository = DnsQueryRepository(db)
        logger.info("Cleaning up old DNS records", extra={"days": days})
        count = repository.delete_old_records(days=days)
        logger.info("Old DNS records deleted", extra={"deleted": count})
        return {"deleted": count}

    def get_grouped_by_site(
        self,
        db: Session,
        start_date: Optional[datetime] = None,
        end_date: Optional[datetime] = None,
        client_ip: Optional[str] = None,
        blocked_only: bool = False,
        filter_noise: bool = True,
        limit: int = 50
    ) -> dict:
        repository = DnsQueryRepository(db)
        logger.info("Fetching grouped sites")
        return repository.get_grouped_by_site(
            start_date=start_date,
            end_date=end_date,
            client_ip=client_ip,
            blocked_only=blocked_only,
            filter_noise=filter_noise,
            limit=limit
        )
