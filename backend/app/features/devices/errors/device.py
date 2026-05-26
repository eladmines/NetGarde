from app.shared.errors import ConflictError, NotFoundError


class DeviceAlreadyExistsError(ConflictError):
    def __init__(self, identifier: str):
        super().__init__(f"Device '{identifier}' already exists")


class DeviceNotFoundError(NotFoundError):
    def __init__(self, identifier: str):
        super().__init__(f"Device '{identifier}' not found")
