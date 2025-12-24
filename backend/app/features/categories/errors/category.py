from app.shared.errors import ConflictError, NotFoundError


class CategoryAlreadyExistsError(ConflictError):
    def __init__(self, name: str):
        super().__init__(f"Category with name '{name}' already exists")


class CategoryNotFoundError(NotFoundError):
    def __init__(self, identifier: int):
        super().__init__(f"Category '{identifier}' not found")

