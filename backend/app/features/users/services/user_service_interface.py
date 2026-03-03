from typing import List, Protocol

from sqlalchemy.orm import Session

from app.features.users.schemas.user import UserCreate, UserRead, UserUpdate


class IUserService(Protocol):
    def create_user(self, data: UserCreate, db: Session) -> UserRead:
        ...

    def get_users(self, db: Session, active_only: bool = False) -> List[UserRead]:
        ...

    def update_user(self, user_id: int, data: UserUpdate, db: Session) -> UserRead:
        ...

    def delete_user(self, user_id: int, db: Session) -> dict:
        ...
