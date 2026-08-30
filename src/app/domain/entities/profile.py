from dataclasses import dataclass, field
from datetime import datetime
from uuid import UUID

from app.domain.entities._common import new_entity_id, utc_now
from app.domain.entities.base import Entity


@dataclass(eq=False, kw_only=True)
class Profile(Entity[UUID]):
    """User-facing account profile."""

    id:           UUID            = field(default_factory=new_entity_id, init=False)
    account_id:   UUID
    display_name: str
    given_name:   str | None      = None
    family_name:  str | None      = None
    bio:          str | None      = None
    job_title:    str | None      = None
    organization: str | None      = None
    locale:       str | None      = None
    time_zone:    str | None      = None
    picture_url:  str | None      = None
    website_url:  str | None      = None
    created_at:   datetime        = field(default_factory=utc_now, init=False)
    updated_at:   datetime | None = field(default=None, init=False)

    def update(
        self,
        *,
        display_name: str,
        given_name: str | None,
        family_name: str | None,
        bio: str | None,
        job_title: str | None,
        organization: str | None,
        locale: str | None,
        time_zone: str | None,
        picture_url: str | None,
        website_url: str | None,
    ) -> None:
        self.display_name = display_name
        self.given_name = given_name
        self.family_name = family_name
        self.bio = bio
        self.job_title = job_title
        self.organization = organization
        self.locale = locale
        self.time_zone = time_zone
        self.picture_url = picture_url
        self.website_url = website_url
        self.updated_at = utc_now()
