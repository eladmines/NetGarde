from app.shared.errors import ConflictError, NotFoundError


class UserAlreadyExistsError(ConflictError):
    def __init__(self, identifier: str):
        super().__init__(f"User '{identifier}' already exists")


class UserNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(f"User '{identifier}' not found")
