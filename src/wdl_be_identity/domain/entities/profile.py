from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from wdl_be_identity.domain.entities._common import new_entity_id, utc_now
from wdl_be_identity.domain.entities.base import Entity


@dataclass(eq=False, kw_only=True)
class Profile(Entity[UUID]):
    """User-facing account profile."""

    id:           UUID            = field(default_factory=new_entity_id, init=False)
    account_id:   UUID
    display_name: str
    locale:       str | None      = None
    time_zone:    str | None      = None
    picture_url:  str | None      = None
    updated_at:   datetime | None = field(default=None, init=False)

    def update(
        self,
        *,
        display_name: str,
        locale: str | None,
        time_zone: str | None,
        picture_url: str | None,
    ) -> None:
        self.display_name = display_name
        self.locale = locale
        self.time_zone = time_zone
        self.picture_url = picture_url
        self.updated_at = utc_now()
