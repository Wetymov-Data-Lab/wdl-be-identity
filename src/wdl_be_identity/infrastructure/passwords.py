from anyio import to_thread
from argon2 import PasswordHasher as Argon2Hasher
from argon2 import Type
from argon2.exceptions import VerificationError


class Argon2PasswordHasher:
    """Argon2id password hasher."""

    def __init__(self) -> None:
        self._hasher = Argon2Hasher(type=Type.ID)

    async def hash(self, password: str) -> str:
        return await to_thread.run_sync(self._hasher.hash, password)

    async def verify(self, password: str, password_hash: str) -> bool:
        try:
            return await to_thread.run_sync(self._hasher.verify, password_hash, password)
        except VerificationError:
            return False

    async def needs_rehash(self, password_hash: str) -> bool:
        return await to_thread.run_sync(self._hasher.check_needs_rehash, password_hash)
