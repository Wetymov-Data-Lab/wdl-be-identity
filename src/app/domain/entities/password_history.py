from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.entities._common import new_entity_id
from app.domain.entities.base import Entity


@dataclass(eq=False, kw_only=True)
class PasswordHistory(Entity[UUID]):
    """Snapshot of an earlier account password."""

    id:         UUID = field(default_factory=new_entity_id, init=False)
    account_id: UUID
    hash:       str  = field(repr=False)
    set_at:     datetime
    version:    int
