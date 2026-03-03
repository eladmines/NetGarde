from typing import List

from sqlalchemy.exc import IntegrityError
from sqlalchemy.orm import Session

from app.features.users.errors.user import UserAlreadyExistsError, UserNotFoundError
from app.features.users.repositories.user_repository import UserRepository
from app.features.users.schemas.user import UserCreate, UserRead, UserUpdate
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


class UserService:
    def create_user(self, data: UserCreate, db: Session) -> UserRead:
        repository = UserRepository(db)
        try:
            user = repository.create(data)
            return UserRead.model_validate(user)
        except IntegrityError as exc:
            identifier = data.email or data.name
            raise UserAlreadyExistsError(identifier) from exc

    def get_users(self, db: Session, active_only: bool = False) -> List[UserRead]:
        repository = UserRepository(db)
        users = repository.get_all(active_only=active_only)
        return [UserRead.model_validate(user) for user in users]

    def update_user(self, user_id: int, data: UserUpdate, db: Session) -> UserRead:
        repository = UserRepository(db)
        try:
            user = repository.update(user_id, data)
            if not user:
                raise UserNotFoundError(str(user_id))
            return UserRead.model_validate(user)
        except IntegrityError as exc:
            identifier = data.email or data.name or str(user_id)
            raise UserAlreadyExistsError(identifier) from exc

    def delete_user(self, user_id: int, db: Session) -> dict:
        repository = UserRepository(db)
        deleted = repository.delete(user_id)
        if not deleted:
            raise UserNotFoundError(str(user_id))
        return {"message": "User deleted successfully", "user_id": user_id}
