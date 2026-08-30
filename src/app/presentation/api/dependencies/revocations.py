from app.application.revocations import SessionRevocationStore
from app.infrastructure.config import settings
from app.infrastructure.redis import get_redis_client
from app.infrastructure.revocations import RedisSessionRevocationStore


def get_session_revocation_store() -> SessionRevocationStore:
    return RedisSessionRevocationStore(
        get_redis_client(),
        key_prefix=settings.REDIS_KEY_PREFIX,
    )
