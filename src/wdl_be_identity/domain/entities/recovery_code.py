from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from wdl_be_identity.domain.entities._common import new_entity_id, raise_invariant, utc_now
from wdl_be_identity.domain.entities.base import Entity


@dataclass(eq=False, kw_only=True)
class RecoveryCode(Entity[UUID]):
    """A single-use recovery code stored only as a hash."""

    _dictionary_path: ClassVar[str] = "entities.recovery_code"

    id:         UUID            = field(default_factory=new_entity_id, init=False)
    account_id: UUID
    hash:       str             = field(repr=False)
    used_at:    datetime | None = field(default=None, init=False)
    created_at: datetime        = field(default_factory=utc_now, init=False)

    def use(self) -> None:
        if self.used_at is not None:
            raise_invariant(self._dictionary_path, "ALREADY_USED")

        self.used_at = utc_now()
