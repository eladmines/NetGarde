class DomainError(Exception):
    """Base class for domain-level errors."""


class ValidationError(DomainError):
    pass


class NotFoundError(DomainError):
    pass


class ConflictError(DomainError):
    pass

