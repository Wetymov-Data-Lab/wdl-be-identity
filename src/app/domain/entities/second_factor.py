from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from app.domain.entities._common import new_entity_id, raise_invariant, utc_now
from app.domain.entities.base import Entity


@dataclass(eq=False, kw_only=True)
class SecondFactor(Entity[UUID]):
    """A second authentication factor owned by an account."""

    _dictionary_path: ClassVar[str] = "entities.second_factor"

    id:           UUID            = field(default_factory=new_entity_id, init=False)
    account_id:   UUID
    type:         str
    secret:       str             = field(repr=False)
    name:         str | None      = None
    confirmed_at: datetime | None = field(default=None, init=False)
    created_at:   datetime        = field(default_factory=utc_now, init=False)

    def confirm(self) -> None:
        if self.confirmed_at is not None:
            raise_invariant(self._dictionary_path, "ALREADY_CONFIRMED")

        self.confirmed_at = utc_now()
