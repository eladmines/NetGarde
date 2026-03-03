from fastapi import HTTPException
from sqlalchemy.orm import Session

from app.features.users.errors.user import UserAlreadyExistsError, UserNotFoundError
from app.features.users.schemas.user import UserCreate, UserUpdate
from app.features.users.services.user_service_interface import IUserService
from app.shared.utils.logging import get_logger

logger = get_logger(__name__)


def create_user_controller(data: UserCreate, db: Session, service: IUserService):
    try:
        return service.create_user(data, db)
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.error("POST /users - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))


def get_users_controller(db: Session, service: IUserService, active_only: bool = False):
    try:
        return service.get_users(db, active_only=active_only)
    except Exception:
        logger.error("GET /users - error", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to fetch users")


def update_user_controller(user_id: int, data: UserUpdate, db: Session, service: IUserService):
    try:
        return service.update_user(user_id, data, db)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except UserAlreadyExistsError as exc:
        raise HTTPException(status_code=409, detail=str(exc))
    except Exception as exc:
        logger.error("PUT /users/{user_id} - error", exc_info=True)
        raise HTTPException(status_code=400, detail=str(exc))


def delete_user_controller(user_id: int, db: Session, service: IUserService):
    try:
        return service.delete_user(user_id, db)
    except UserNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc))
    except Exception:
        logger.error("DELETE /users/{user_id} - error", exc_info=True)
        raise HTTPException(status_code=500, detail="Failed to delete user")
