from functools import lru_cache

from wdl_be_identity.application.passwords import PasswordHasher
from wdl_be_identity.infrastructure.passwords import Argon2PasswordHasher


@lru_cache
def get_password_hasher() -> PasswordHasher:
    return Argon2PasswordHasher()
