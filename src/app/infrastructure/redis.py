from functools import lru_cache
from typing import cast

from redis.asyncio import Redis

from app.infrastructure.config import settings


@lru_cache
def get_redis_client() -> Redis:
    if settings.REDIS_URL is None:
        raise RuntimeError("REDIS_URL is not configured")
    return cast(Redis, Redis.from_url(settings.REDIS_URL, decode_responses=True))
