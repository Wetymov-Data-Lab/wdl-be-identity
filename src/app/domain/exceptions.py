class DomainError(Exception):
    """Base exception for violations of domain rules."""


class InvariantViolationError(DomainError):
    """Raised when an operation would violate a domain invariant."""

    def __init__(self, *, message_key: str) -> None:
        self.message_key = message_key
        super().__init__(message_key)


class EntityNotFoundError(DomainError):
    """Requested domain entity does not exist."""


class EntityAlreadyExistsError(DomainError):
    """An entity violates a uniqueness constraint."""


class AuthenticationError(DomainError):
    """Credentials or a bearer token cannot be authenticated."""


class AuthorizationError(DomainError):
    """An authenticated account is not allowed to proceed."""
