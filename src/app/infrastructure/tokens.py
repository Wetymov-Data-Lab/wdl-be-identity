import hashlib
from datetime import UTC, datetime, timedelta
from typing import Any, cast
from uuid import UUID, uuid4

import jwt

from app.application.tokens import TokenClaims, TokenCodec, TokenKind, TokenPair
from app.domain.exceptions import AuthenticationError


class JWTTokenCodec(TokenCodec):
    """HS256 JWT codec with short-lived access and rotating refresh tokens."""

    def __init__(
        self,
        *,
        secret_key: str,
        issuer: str,
        audience: str,
        access_token_ttl: timedelta,
        refresh_token_ttl: timedelta,
    ) -> None:
        self._secret_key = secret_key
        self._issuer = issuer
        self._audience = audience
        self._access_token_ttl = access_token_ttl
        self._refresh_token_ttl = refresh_token_ttl

    def issue_pair(self, *, account_id: UUID, session_id: UUID) -> TokenPair:
        now = datetime.now(UTC)
        access_expires_at = now + self._access_token_ttl
        refresh_expires_at = now + self._refresh_token_ttl
        return TokenPair(
            access_token=self._encode(
                account_id=account_id,
                session_id=session_id,
                kind="access",
                issued_at=now,
                expires_at=access_expires_at,
            ),
            refresh_token=self._encode(
                account_id=account_id,
                session_id=session_id,
                kind="refresh",
                issued_at=now,
                expires_at=refresh_expires_at,
            ),
            access_expires_in=int(self._access_token_ttl.total_seconds()),
            refresh_expires_at=refresh_expires_at,
        )

    def decode(self, token: str, *, expected_kind: TokenKind | None = None) -> TokenClaims:
        try:
            payload: dict[str, Any] = jwt.decode(
                token,
                self._secret_key,
                algorithms=["HS256"],
                audience=self._audience,
                issuer=self._issuer,
                options={"require": ["sub", "sid", "type", "iat", "nbf", "exp", "jti"]},
            )
            kind = payload["type"]
            if kind not in ("access", "refresh") or (expected_kind is not None and kind != expected_kind):
                raise AuthenticationError("Invalid token type")
            return TokenClaims(
                account_id=UUID(payload["sub"]),
                session_id=UUID(payload["sid"]),
                kind=cast(TokenKind, kind),
            )
        except AuthenticationError:
            raise
        except (jwt.PyJWTError, KeyError, TypeError, ValueError) as error:
            raise AuthenticationError("Invalid or expired token") from error

    def hash_refresh_token(self, token: str) -> str:
        return hashlib.sha256(token.encode()).hexdigest()

    def _encode(
        self,
        *,
        account_id: UUID,
        session_id: UUID,
        kind: TokenKind,
        issued_at: datetime,
        expires_at: datetime,
    ) -> str:
        return jwt.encode(
            {
                "sub": str(account_id),
                "sid": str(session_id),
                "type": kind,
                "iss": self._issuer,
                "aud": self._audience,
                "iat": issued_at,
                "nbf": issued_at,
                "exp": expires_at,
                "jti": str(uuid4()),
            },
            self._secret_key,
            algorithm="HS256",
        )
