from enum import StrEnum


class AccountSubject(StrEnum):
    """The kind of principal represented by an account."""

    USER = "user"
    SERVICE = "service"


class AccountStatus(StrEnum):
    """Lifecycle state of an account."""

    PENDING = "pending"
    ACTIVE = "active"
    DEACTIVATED = "deactivated"
    SUSPENDED = "suspended"
