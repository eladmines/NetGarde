from datetime import datetime, timezone
from typing import List, Optional

from sqlalchemy.orm import Session

from app.features.users.models.user import User
from app.features.users.schemas.user import UserCreate, UserUpdate


class UserRepository:
    def __init__(self, db: Session):
        self.db = db

    def create(self, data: UserCreate) -> User:
        user = User(**data.model_dump())
        self.db.add(user)
        self.db.commit()
        self.db.refresh(user)
        return user

    def get_all(self, active_only: bool = False) -> List[User]:
        query = self.db.query(User)
        if active_only:
            query = query.filter(User.is_active.is_(True))
        return query.order_by(User.name.asc()).all()

    def get_by_id(self, user_id: int) -> Optional[User]:
        return self.db.query(User).filter(User.id == user_id).first()

    def update(self, user_id: int, data: UserUpdate) -> Optional[User]:
        user = self.get_by_id(user_id)
        if not user:
            return None

        updates = data.model_dump(exclude_unset=True)
        for key, value in updates.items():
            setattr(user, key, value)
        user.updated_at = datetime.now(timezone.utc)
        self.db.commit()
        self.db.refresh(user)
        return user

    def delete(self, user_id: int) -> bool:
        user = self.get_by_id(user_id)
        if not user:
            return False

        self.db.delete(user)
        self.db.commit()
        return True
