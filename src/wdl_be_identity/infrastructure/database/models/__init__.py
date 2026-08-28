"""Import SQLAlchemy mappings here so Alembic can discover them."""

from .identity import (
    accounts,
    identifiers,
    password_history,
    passwords,
    profiles,
    recovery_codes,
    second_factors,
    sessions,
)

__all__ = [
    "accounts",
    "identifiers",
    "password_history",
    "passwords",
    "profiles",
    "recovery_codes",
    "second_factors",
    "sessions",
]
