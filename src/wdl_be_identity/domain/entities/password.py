from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from wdl_be_identity.domain.entities._common import new_entity_id, utc_now
from wdl_be_identity.domain.entities.base import Entity


@dataclass(eq=False, kw_only=True)
class Password(Entity[UUID]):
    """Current password credential for an account."""

    id:         UUID     = field(default_factory=new_entity_id, init=False)
    account_id: UUID
    hash:       str      = field(repr=False)
    set_at:     datetime = field(default_factory=utc_now, init=False)
    version:    int      = field(default=1, init=False)

    def change(self, *, new_hash: str) -> None:
        self.hash = new_hash
        self.set_at = utc_now()
        self.version += 1
