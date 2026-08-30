from datetime import datetime
from uuid import UUID

from sqlalchemy import Boolean, DateTime, ForeignKey, Index, String, Text, Uuid, false, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class IdentifierModel(Base):
    __tablename__ = "identifiers"
    __table_args__ = (
        Index("ix_identifiers_account_id", "account_id"),
        Index(
            "uq_identifiers_local_type_value",
            "type",
            "value",
            unique=True,
            postgresql_where=text("provider IS NULL"),
        ),
        Index(
            "uq_identifiers_provider_user",
            "provider",
            "provider_user_id",
            unique=True,
            postgresql_where=text("provider IS NOT NULL AND provider_user_id IS NOT NULL"),
        ),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE")
    )
    type: Mapped[str] = mapped_column(String(64))
    value: Mapped[str] = mapped_column(Text)
    provider: Mapped[str | None] = mapped_column(String(128), default=None)
    provider_user_id: Mapped[str | None] = mapped_column(Text, default=None)
    is_verified: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    is_public_contact: Mapped[bool] = mapped_column(Boolean, default=False, server_default=false())
    receive_notifications: Mapped[bool] = mapped_column(
        Boolean, default=False, server_default=false()
    )
    verified_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    last_used_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


identifiers = IdentifierModel.__table__
