from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from wdl_be_identity.domain.entities._common import new_entity_id, raise_invariant, utc_now
from wdl_be_identity.domain.entities.base import Entity


@dataclass(eq=False, kw_only=True)
class Session(Entity[UUID]):
    """Refreshable authenticated account session."""

    _dictionary_path: ClassVar[str] = "entities.session"

    id:                 UUID       = field(default_factory=new_entity_id, init=False)
    account_id:         UUID
    ip:                 str
    refresh_token_hash: str        = field(repr=False)
    user_agent:         str
    expires_at:         datetime
    created_at:         datetime   = field(default_factory=utc_now, init=False)
    last_refreshed_at:  datetime   = field(init=False)

    def __post_init__(self) -> None:
        super().__post_init__()
        self.last_refreshed_at = self.created_at

    def is_expired(self, *, at: datetime | None = None) -> bool:
        return self.expires_at <= (at or utc_now())

    def refresh(self, *, refresh_token_hash: str, expires_at: datetime) -> None:
        refreshed_at = utc_now()
        if self.is_expired(at=refreshed_at):
            raise_invariant(self._dictionary_path, "EXPIRED")
        if expires_at <= refreshed_at:
            raise_invariant(self._dictionary_path, "INVALID_EXPIRATION")

        self.refresh_token_hash = refresh_token_hash
        self.expires_at = expires_at
        self.last_refreshed_at = refreshed_at
