from __future__ import annotations

from sqlalchemy.orm import Session

from app.features.vpn.models.ip_lease import IpLease


class IpLeaseRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_by_peer_id(self, peer_id: int) -> IpLease | None:
        return (
            self.db.query(IpLease)
            .filter(IpLease.peer_id == peer_id, IpLease.released_at.is_(None))
            .first()
        )

    def list_active_ips_by_pool_id(self, pool_id: int) -> set[str]:
        rows = (
            self.db.query(IpLease.ip)
            .filter(IpLease.pool_id == pool_id, IpLease.released_at.is_(None))
            .all()
        )
        return {r[0] for r in rows}

    def create(self, lease: IpLease) -> IpLease:
        self.db.add(lease)
        self.db.flush()
        self.db.refresh(lease)
        return lease

