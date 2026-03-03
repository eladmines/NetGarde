from app.features.users.services.user_service import UserService
from app.features.users.services.user_service_interface import IUserService


def get_user_service() -> IUserService:
    return UserService()
