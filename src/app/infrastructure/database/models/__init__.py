"""Expose declarative ORM models and register their metadata for Alembic."""

from .account import AccountModel, accounts
from .identifier import IdentifierModel, identifiers
from .password import PasswordModel, passwords
from .password_history import PasswordHistoryModel, password_history
from .profile import ProfileModel, profiles
from .recovery_code import RecoveryCodeModel, recovery_codes
from .second_factor import SecondFactorModel, second_factors
from .session import SessionModel, sessions

__all__ = [
    "AccountModel",
    "IdentifierModel",
    "PasswordHistoryModel",
    "PasswordModel",
    "ProfileModel",
    "RecoveryCodeModel",
    "SecondFactorModel",
    "SessionModel",
    "accounts",
    "identifiers",
    "password_history",
    "passwords",
    "profiles",
    "recovery_codes",
    "second_factors",
    "sessions",
]
