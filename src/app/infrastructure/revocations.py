from datetime import UTC, datetime
from math import ceil
from uuid import UUID

from redis.asyncio import Redis

from app.application.revocations import SessionRevocationStore


class RedisSessionRevocationStore(SessionRevocationStore):
    def __init__(self, redis: Redis, *, key_prefix: str) -> None:
        self._redis = redis
        self._key_prefix = key_prefix

    async def is_revoked(self, session_id: UUID) -> bool:
        return bool(await self._redis.exists(self._key(session_id)))

    async def revoke(self, session_id: UUID, *, expires_at: datetime) -> None:
        ttl = max(1, ceil((expires_at - datetime.now(UTC)).total_seconds()))
        await self._redis.set(self._key(session_id), "1", ex=ttl)

    def _key(self, session_id: UUID) -> str:
        return f"{self._key_prefix}:revoked-session:{session_id}"
