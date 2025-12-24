from app.shared.errors import ConflictError, NotFoundError


class BlockedSiteAlreadyExistsError(ConflictError):
    def __init__(self, domain: str):
        super().__init__(f"Blocked site with domain '{domain}' already exists")

class BlockedSiteNotFoundError(NotFoundError):
    def __init__(self, identifier: int):
        super().__init__(f"Blocked site '{identifier}' not found")


