from typing import Protocol


class PasswordHasher(Protocol):
    """Application port for password hashing and verification."""

    async def hash(self, password: str) -> str: ...

    async def verify(self, password: str, password_hash: str) -> bool: ...

    async def needs_rehash(self, password_hash: str) -> bool: ...
