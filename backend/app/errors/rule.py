from app.errors import ConflictError, NotFoundError


class RuleAlreadyExistsError(ConflictError):
    def __init__(self, domain: str):
        super().__init__(f"Rule with domain '{domain}' already exists")

class RuleNotFoundError(NotFoundError):
    def __init__(self, identifier: int):
        super().__init__(f"Rule '{identifier}' not found")