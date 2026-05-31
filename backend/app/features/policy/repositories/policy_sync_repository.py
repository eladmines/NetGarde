import json
from datetime import datetime, timezone
from typing import Optional

from sqlalchemy import text
from sqlalchemy.orm import Session

from app.features.policy.models.policy_sync_status import PolicySyncStatus
from app.features.policy.schemas.policy import PolicySyncStatusRead


class PolicySyncRepository:
    def __init__(self, db: Session):
        self.db = db

    def get_status(self) -> PolicySyncStatusRead:
        row = self.db.query(PolicySyncStatus).filter(PolicySyncStatus.id == 1).first()
        if not row:
            return PolicySyncStatusRead(last_sync_at=None, last_success=None, last_message=None)
        return PolicySyncStatusRead(
            last_sync_at=row.last_sync_at,
            last_success=row.last_success,
            last_message=row.last_message,
        )

    def record_sync(self, *, success: bool, message: Optional[str] = None) -> PolicySyncStatusRead:
        row = self.db.query(PolicySyncStatus).filter(PolicySyncStatus.id == 1).first()
        now = datetime.now(timezone.utc)
        if row is None:
            row = PolicySyncStatus(id=1, last_sync_at=now, last_success=success, last_message=message)
            self.db.add(row)
        else:
            row.last_sync_at = now
            row.last_success = success
            row.last_message = message
        self.db.commit()
        return self.get_status()

    def notify_policy_changed(self, source: str = "api") -> None:
        payload = json.dumps({"source": source, "at": datetime.now(timezone.utc).isoformat()})
        self.db.execute(text("SELECT pg_notify('policy_changed', :payload)"), {"payload": payload})
        self.db.commit()
