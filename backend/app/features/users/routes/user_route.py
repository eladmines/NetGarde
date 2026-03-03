from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session

from app.features.users.controllers.user_controller import (
    create_user_controller,
    delete_user_controller,
    get_users_controller,
    update_user_controller,
)
from app.features.users.dependencies import get_user_service
from app.features.users.schemas.user import UserCreate, UserUpdate
from app.features.users.services.user_service_interface import IUserService
from app.shared.dependencies import get_db

router = APIRouter(prefix="/users", tags=["Users"])


@router.post("")
def create_user_endpoint(
    data: UserCreate,
    db: Session = Depends(get_db),
    service: IUserService = Depends(get_user_service),
):
    return create_user_controller(data, db, service)


@router.get("")
def get_users_endpoint(
    active_only: bool = Query(default=False, description="Return active users only"),
    db: Session = Depends(get_db),
    service: IUserService = Depends(get_user_service),
):
    return get_users_controller(db, service, active_only=active_only)


@router.put("/{user_id}")
def update_user_endpoint(
    user_id: int,
    data: UserUpdate,
    db: Session = Depends(get_db),
    service: IUserService = Depends(get_user_service),
):
    return update_user_controller(user_id, data, db, service)


@router.delete("/{user_id}")
def delete_user_endpoint(
    user_id: int,
    db: Session = Depends(get_db),
    service: IUserService = Depends(get_user_service),
):
    return delete_user_controller(user_id, db, service)
