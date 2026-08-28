from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from wdl_be_identity.domain.entities._common import new_entity_id, utc_now
from wdl_be_identity.domain.entities.base import Entity


@dataclass(eq=False, kw_only=True)
class MasterCode(Entity[UUID]):
    """Account master recovery code stored only as a hash."""

    id:         UUID     = field(default_factory=new_entity_id, init=False)
    account_id: UUID
    hash:       str      = field(repr=False)
    created_at: datetime = field(default_factory=utc_now, init=False)
