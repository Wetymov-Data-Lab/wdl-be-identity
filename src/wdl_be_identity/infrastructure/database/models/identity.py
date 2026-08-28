from enum import Enum as PythonEnum

from sqlalchemy import (
    Boolean,
    CheckConstraint,
    Column,
    DateTime,
    Enum,
    ForeignKey,
    Index,
    Integer,
    String,
    Table,
    Text,
    UniqueConstraint,
    Uuid,
    false,
    inspect,
    text,
)
from sqlalchemy.orm import relationship

from wdl_be_identity.domain.entities import (
    Account,
    Identifier,
    MasterCode,
    Password,
    PasswordHistory,
    Profile,
    RecoveryCode,
    SecondFactor,
    Session,
)
from wdl_be_identity.domain.enums import AccountStatus, AccountSubject
from wdl_be_identity.infrastructure.database.base import Base


def _enum_values(enum: type[PythonEnum]) -> list[str]:
    return [str(member.value) for member in enum]


def _next_version(version: int | None) -> int:
    return (version or 0) + 1


account_subject_type = Enum(
    AccountSubject,
    values_callable=_enum_values,
    native_enum=False,
    length=32,
    name="account_subject",
)
account_status_type = Enum(
    AccountStatus,
    values_callable=_enum_values,
    native_enum=False,
    length=32,
    name="account_status",
)


accounts = Table(
    "accounts",
    Base.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("subject", account_subject_type, nullable=False),
    Column("status", account_status_type, nullable=False),
    Column("is_2fa_enforced", Boolean, nullable=False, server_default=false()),
    Column("last_active_at", DateTime(timezone=True), nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("version", Integer, nullable=False, server_default=text("1")),
    CheckConstraint("subject IN ('user', 'service')", name="ck_accounts_subject"),
    CheckConstraint(
        "status IN ('pending', 'active', 'deactivated', 'suspended')",
        name="ck_accounts_status",
    ),
    CheckConstraint("version >= 1", name="ck_accounts_version_positive"),
)

profiles = Table(
    "profiles",
    Base.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("account_id", Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("display_name", Text, nullable=False),
    Column("locale", Text, nullable=True),
    Column("time_zone", Text, nullable=True),
    Column("picture_url", Text, nullable=True),
    Column("updated_at", DateTime(timezone=True), nullable=True),
    UniqueConstraint("account_id", name="uq_profiles_account_id"),
)

passwords = Table(
    "passwords",
    Base.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("account_id", Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("hash", Text, nullable=False),
    Column("set_at", DateTime(timezone=True), nullable=False),
    Column("version", Integer, nullable=False, server_default=text("1")),
    CheckConstraint("version >= 1", name="ck_passwords_version_positive"),
    UniqueConstraint("account_id", name="uq_passwords_account_id"),
)

master_codes = Table(
    "master_codes",
    Base.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("account_id", Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("hash", Text, nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint("account_id", name="uq_master_codes_account_id"),
)

second_factors = Table(
    "second_factors",
    Base.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("account_id", Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("type", String(64), nullable=False),
    Column("secret", Text, nullable=False),
    Column("name", Text, nullable=True),
    Column("confirmed_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)
Index("ix_second_factors_account_id", second_factors.c.account_id)

recovery_codes = Table(
    "recovery_codes",
    Base.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("account_id", Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("hash", Text, nullable=False),
    Column("used_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
    UniqueConstraint("hash", name="uq_recovery_codes_hash"),
)
Index("ix_recovery_codes_account_id", recovery_codes.c.account_id)

password_history = Table(
    "password_history",
    Base.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("account_id", Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("hash", Text, nullable=False),
    Column("set_at", DateTime(timezone=True), nullable=False),
    Column("version", Integer, nullable=False),
    CheckConstraint("version >= 1", name="ck_password_history_version_positive"),
    UniqueConstraint("account_id", "version", name="uq_password_history_account_id_version"),
)
Index("ix_password_history_account_id", password_history.c.account_id)

identifiers = Table(
    "identifiers",
    Base.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("account_id", Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("type", String(64), nullable=False),
    Column("value", Text, nullable=False),
    Column("provider", String(128), nullable=True),
    Column("provider_user_id", Text, nullable=True),
    Column("is_verified", Boolean, nullable=False, server_default=false()),
    Column("is_public_contact", Boolean, nullable=False, server_default=false()),
    Column("receive_notifications", Boolean, nullable=False, server_default=false()),
    Column("verified_at", DateTime(timezone=True), nullable=True),
    Column("last_used_at", DateTime(timezone=True), nullable=True),
    Column("created_at", DateTime(timezone=True), nullable=False),
)
Index("ix_identifiers_account_id", identifiers.c.account_id)
Index(
    "uq_identifiers_local_type_value",
    identifiers.c.type,
    identifiers.c.value,
    unique=True,
    postgresql_where=identifiers.c.provider.is_(None),
)
Index(
    "uq_identifiers_provider_user",
    identifiers.c.provider,
    identifiers.c.provider_user_id,
    unique=True,
    postgresql_where=identifiers.c.provider.is_not(None) & identifiers.c.provider_user_id.is_not(None),
)

sessions = Table(
    "sessions",
    Base.metadata,
    Column("id", Uuid(as_uuid=True), primary_key=True),
    Column("account_id", Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE"), nullable=False),
    Column("ip", Text, nullable=False),
    Column("refresh_token_hash", Text, nullable=False),
    Column("user_agent", Text, nullable=False),
    Column("expires_at", DateTime(timezone=True), nullable=False),
    Column("created_at", DateTime(timezone=True), nullable=False),
    Column("last_refreshed_at", DateTime(timezone=True), nullable=False),
    CheckConstraint("expires_at > created_at", name="ck_sessions_expiration_after_creation"),
    UniqueConstraint("refresh_token_hash", name="uq_sessions_refresh_token_hash"),
)
Index("ix_sessions_account_id", sessions.c.account_id)
Index("ix_sessions_expires_at", sessions.c.expires_at)

def start_mappers() -> None:
    """Map persistence-ignorant domain entities to their database tables."""

    if inspect(Account, raiseerr=False) is not None:
        return

    Base.registry.map_imperatively(Profile, profiles)
    Base.registry.map_imperatively(Password, passwords)
    Base.registry.map_imperatively(MasterCode, master_codes)
    Base.registry.map_imperatively(SecondFactor, second_factors)
    Base.registry.map_imperatively(RecoveryCode, recovery_codes)
    Base.registry.map_imperatively(PasswordHistory, password_history)
    Base.registry.map_imperatively(Identifier, identifiers)
    Base.registry.map_imperatively(Session, sessions)
    Base.registry.map_imperatively(
        Account,
        accounts,
        properties={
            "profile": relationship(
                Profile,
                cascade="all, delete-orphan",
                lazy="joined",
                passive_deletes=True,
                single_parent=True,
                uselist=False,
            ),
            "password": relationship(
                Password,
                cascade="all, delete-orphan",
                lazy="joined",
                passive_deletes=True,
                single_parent=True,
                uselist=False,
            ),
            "master_code": relationship(
                MasterCode,
                cascade="all, delete-orphan",
                lazy="joined",
                passive_deletes=True,
                single_parent=True,
                uselist=False,
            ),
            "sessions": relationship(
                Session,
                cascade="all, delete-orphan",
                lazy="selectin",
                passive_deletes=True,
            ),
            "identifiers": relationship(
                Identifier,
                cascade="all, delete-orphan",
                lazy="selectin",
                passive_deletes=True,
            ),
            "second_factors": relationship(
                SecondFactor,
                cascade="all, delete-orphan",
                lazy="selectin",
                passive_deletes=True,
            ),
            "recovery_codes": relationship(
                RecoveryCode,
                cascade="all, delete-orphan",
                lazy="selectin",
                passive_deletes=True,
            ),
            "password_history": relationship(
                PasswordHistory,
                cascade="all, delete-orphan",
                lazy="selectin",
                passive_deletes=True,
                order_by=password_history.c.version.desc(),
            ),
        },
        version_id_col=accounts.c.version,
        version_id_generator=_next_version,
    )


start_mappers()
