from functools import lru_cache

from app.application.passwords import PasswordHasher
from app.infrastructure.passwords import Argon2PasswordHasher


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()
