from sqlalchemy.orm import Session
from typing import Optional
from datetime import datetime
from app.features.dns_queries.models.domain_first_seen import DomainFirstSeen


class DomainFirstSeenRepository:
    def __init__(self, db: Session):
        self.db = db

    def get(self, client_ip: str, root_domain: str) -> Optional[DomainFirstSeen]:
        return (
            self.db.query(DomainFirstSeen)
            .filter(
                DomainFirstSeen.client_ip == client_ip,
                DomainFirstSeen.root_domain == root_domain,
            )
            .first()
        )

    def record_first_seen(
        self,
        client_ip: str,
        root_domain: str,
        first_seen_at: datetime,
    ) -> DomainFirstSeen:
        row = DomainFirstSeen(
            client_ip=client_ip,
            root_domain=root_domain,
            first_seen_at=first_seen_at,
        )
        self.db.add(row)
        self.db.flush()
        return row
