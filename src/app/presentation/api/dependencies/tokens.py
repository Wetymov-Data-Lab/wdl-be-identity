from datetime import timedelta
from functools import lru_cache

from app.application.tokens import TokenCodec
from app.infrastructure.config import settings
from app.infrastructure.tokens import JWTTokenCodec


@lru_cache
def get_token_codec() -> TokenCodec:
    return JWTTokenCodec(
        secret_key=settings.JWT_SECRET_KEY.get_secret_value(),
        issuer=settings.JWT_ISSUER,
        audience=settings.JWT_AUDIENCE,
        access_token_ttl=timedelta(minutes=settings.JWT_ACCESS_TOKEN_EXPIRES_MINUTES),
        refresh_token_ttl=timedelta(days=settings.JWT_REFRESH_TOKEN_EXPIRES_DAYS),
    )
