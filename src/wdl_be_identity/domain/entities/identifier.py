from dataclasses import dataclass, field
from datetime import datetime
from typing import ClassVar
from uuid import UUID

from wdl_be_identity.domain.entities._common import new_entity_id, raise_invariant, utc_now
from wdl_be_identity.domain.entities.base import Entity


@dataclass(eq=False, kw_only=True)
class Identifier(Entity[UUID]):
    """An account sign-in or contact identifier."""

    _dictionary_path: ClassVar[str] = "entities.identifier"

    id:                    UUID            = field(default_factory=new_entity_id, init=False)
    account_id:            UUID
    type:                  str
    value:                 str
    provider:              str | None      = None
    provider_user_id:      str | None      = None
    is_verified:           bool            = field(default=False, init=False)
    is_public_contact:     bool            = False
    receive_notifications: bool            = False
    verified_at:           datetime | None = field(default=None, init=False)
    last_used_at:          datetime | None = field(default=None, init=False)
    created_at:            datetime        = field(default_factory=utc_now, init=False)

    def verify(self) -> None:
        if self.is_verified:
            raise_invariant(self._dictionary_path, "ALREADY_VERIFIED")

        self.is_verified = True
        self.verified_at = utc_now()

    def touch(self) -> None:
        self.last_used_at = utc_now()

    def set_contact_preferences(
        self,
        *,
        is_public_contact: bool,
        receive_notifications: bool,
    ) -> None:
        self.is_public_contact = is_public_contact
        self.receive_notifications = receive_notifications
