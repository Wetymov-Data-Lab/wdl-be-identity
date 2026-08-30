from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import uuid4

from app.infrastructure.revocations import RedisSessionRevocationStore


class FakeRedis:
    def __init__(self) -> None:
        self.values: dict[str, tuple[str, int]] = {}

    async def exists(self, key: str) -> int:
        return int(key in self.values)

    async def set(self, key: str, value: str, *, ex: int) -> None:
        self.values[key] = (value, ex)


async def test_redis_revocation_store_uses_namespaced_key_and_expiration() -> None:
    redis = FakeRedis()
    store = RedisSessionRevocationStore(cast(Any, redis), key_prefix="wdl:identity:test")
    session_id = uuid4()

    assert await store.is_revoked(session_id) is False
    await store.revoke(session_id, expires_at=datetime.now(UTC) + timedelta(minutes=5))

    assert await store.is_revoked(session_id) is True
    value, ttl = redis.values[f"wdl:identity:test:revoked-session:{session_id}"]
    assert value == "1"
    assert 299 <= ttl <= 300
