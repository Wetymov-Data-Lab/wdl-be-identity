from dataclasses import dataclass
from datetime import datetime
from typing import Literal, Protocol
from uuid import UUID

TokenKind = Literal["access", "refresh"]


@dataclass(frozen=True, slots=True)
class TokenClaims:
    account_id: UUID
    session_id: UUID
    kind: TokenKind


@dataclass(frozen=True, slots=True)
class TokenPair:
    access_token: str
    refresh_token: str
    access_expires_in: int
    refresh_expires_at: datetime


class TokenCodec(Protocol):
    """Application port for issuing and validating signed bearer tokens."""

    def issue_pair(self, *, account_id: UUID, session_id: UUID) -> TokenPair: ...

    def decode(self, token: str, *, expected_kind: TokenKind | None = None) -> TokenClaims: ...

    def hash_refresh_token(self, token: str) -> str: ...
