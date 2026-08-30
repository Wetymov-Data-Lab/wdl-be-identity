from __future__ import annotations

from datetime import datetime
from typing import Any
from uuid import UUID

from sqlalchemy import Boolean, CheckConstraint, DateTime, Integer, Uuid, false, text
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.domain.enums import AccountStatus, AccountSubject
from app.infrastructure.database.base import Base
from app.infrastructure.database.models._common import (
    account_status_type,
    account_subject_type,
)
from app.infrastructure.database.models.identifier import IdentifierModel
from app.infrastructure.database.models.password import PasswordModel
from app.infrastructure.database.models.profile import ProfileModel
from app.infrastructure.database.models.recovery_code import RecoveryCodeModel
from app.infrastructure.database.models.second_factor import SecondFactorModel
from app.infrastructure.database.models.session import SessionModel


def _next_version(version: int | None) -> int:
    return (version or 0) + 1


class AccountModel(Base):
    __tablename__ = "accounts"
    __table_args__ = (
        CheckConstraint("subject IN ('user', 'service')", name="ck_accounts_subject"),
        CheckConstraint(
            "status IN ('pending', 'active', 'deactivated', 'suspended')",
            name="ck_accounts_status",
        ),
        CheckConstraint("version >= 1", name="ck_accounts_version_positive"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    subject: Mapped[AccountSubject] = mapped_column(account_subject_type)
    status: Mapped[AccountStatus] = mapped_column(account_status_type)
    is_2fa_enforced: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    last_active_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"))

    profile: Mapped[ProfileModel | None] = relationship(
        cascade="all, delete-orphan",
        lazy="joined",
        passive_deletes=True,
        single_parent=True,
    )
    password: Mapped[PasswordModel | None] = relationship(
        cascade="all, delete-orphan",
        lazy="joined",
        passive_deletes=True,
        single_parent=True,
    )
    sessions: Mapped[list[SessionModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )
    identifiers: Mapped[list[IdentifierModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )
    second_factors: Mapped[list[SecondFactorModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )
    recovery_codes: Mapped[list[RecoveryCodeModel]] = relationship(
        cascade="all, delete-orphan",
        lazy="selectin",
        passive_deletes=True,
    )

    __mapper_args__: dict[str, Any] = {
        "version_id_col": version,
        "version_id_generator": _next_version,
    }


accounts = AccountModel.__table__
