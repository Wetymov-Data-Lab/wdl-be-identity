from __future__ import annotations

from dataclasses import dataclass, field
from datetime import datetime
from typing import TYPE_CHECKING, ClassVar
from uuid import UUID

from wdl_be_identity.domain.entities._common import new_entity_id, utc_now
from wdl_be_identity.domain.entities.base import Entity
from wdl_be_identity.domain.enums import AccountStatus, AccountSubject
from wdl_be_identity.domain.exceptions import InvariantViolationError

if TYPE_CHECKING:
    from wdl_be_identity.domain.entities.identifier import Identifier
    from wdl_be_identity.domain.entities.password import Password
    from wdl_be_identity.domain.entities.profile import Profile
    from wdl_be_identity.domain.entities.recovery_code import RecoveryCode
    from wdl_be_identity.domain.entities.second_factor import SecondFactor
    from wdl_be_identity.domain.entities.session import Session


@dataclass(eq=False, kw_only=True)
class Account(Entity[UUID]):
    """Account aggregate root with lifecycle rules enforced by its methods."""

    _dictionary_path: ClassVar[str] = "entities.account"

    # Base
    id:             UUID            = field(default_factory=new_entity_id, init=False)
    created_at:     datetime        = field(default_factory=utc_now, init=False)
    updated_at:     datetime | None = field(default=None, init=False)
    last_active_at: datetime | None = field(default=None, init=False)
    version:        int             = field(default=1, init=False)

    # Attributes
    subject:         AccountSubject
    status:          AccountStatus
    is_2fa_enforced: bool           = field(default=False, init=False)

    # Relations
    profile:     Profile | None    = field(default=None, init=False, repr=False)
    password:    Password | None   = field(default=None, init=False, repr=False)

    sessions:         list[Session]         = field(default_factory=list, init=False, repr=False)
    identifiers:      list[Identifier]      = field(default_factory=list, init=False, repr=False)
    second_factors:   list[SecondFactor]    = field(default_factory=list, init=False, repr=False)
    recovery_codes:   list[RecoveryCode]    = field(default_factory=list, init=False, repr=False)

    def touch(self) -> None:
        self.last_active_at = utc_now()

    def enforce_2fa(self) -> None:
        self.is_2fa_enforced = True
        self.updated_at = utc_now()

    def relax_2fa(self) -> None:
        self.is_2fa_enforced = False
        self.updated_at = utc_now()

    def assign_relations(self, *, password: Password | None, profile: Profile | None) -> None:
        self.password = password
        self.profile = profile

    def activate(self) -> None:
        if self.status is not AccountStatus.PENDING:
            self._raise_invariant("ALREADY_ACTIVATED")

        self._change_status(AccountStatus.ACTIVE)

    def deactivate(self) -> None:
        if self.status is not AccountStatus.ACTIVE:
            self._raise_invariant("DEACTIVATION_NOT_ALLOWED")

        self._change_status(AccountStatus.DEACTIVATED)

    def restore(self) -> None:
        if self.status is not AccountStatus.DEACTIVATED:
            self._raise_invariant("RESTORE_NOT_ALLOWED")

        self._change_status(AccountStatus.ACTIVE)

    def suspend(self) -> None:
        if self.status is AccountStatus.SUSPENDED:
            self._raise_invariant("ALREADY_SUSPENDED")

        self._change_status(AccountStatus.SUSPENDED)

    def unsuspend(self) -> None:
        if self.status is not AccountStatus.SUSPENDED:
            self._raise_invariant("NOT_SUSPENDED")

        self._change_status(AccountStatus.ACTIVE)

    def _change_status(self, status: AccountStatus) -> None:
        self.status = status
        self.updated_at = utc_now()

    def _raise_invariant(self, message_key: str) -> None:
        raise InvariantViolationError(message_key=f"{self._dictionary_path}.{message_key}")
