import pytest

from app.infrastructure.passwords import Argon2PasswordHasher


@pytest.mark.asyncio
async def test_argon2id_hash_and_verify_password() -> None:
    hasher = Argon2PasswordHasher()

    password_hash = await hasher.hash("correct horse battery staple")

    assert password_hash.startswith("$argon2id$")
    assert await hasher.verify("correct horse battery staple", password_hash) is True
    assert await hasher.verify("wrong password", password_hash) is False
