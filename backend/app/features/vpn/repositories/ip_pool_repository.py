from __future__ import annotations

from sqlalchemy.orm import Session

from app.features.vpn.models.ip_pool import IpPool


class IpPoolRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_active_by_name(self, name: str) -> IpPool | None:
        return (
            self.db.query(IpPool)
            .filter(IpPool.name == name, IpPool.is_active == True)  # noqa: E712
            .first()
        )

    def create(self, pool: IpPool) -> IpPool:
        self.db.add(pool)
        self.db.flush()
        self.db.refresh(pool)
        return pool

