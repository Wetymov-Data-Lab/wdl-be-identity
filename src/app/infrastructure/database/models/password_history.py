from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Index, Integer, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class PasswordHistoryModel(Base):
    __tablename__ = "password_history"
    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_password_history_version_positive"),
        UniqueConstraint("account_id", "version", name="uq_password_history_account_id_version"),
        Index("ix_password_history_account_id", "account_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE")
    )
    hash: Mapped[str] = mapped_column(Text)
    set_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer)


password_history = PasswordHistoryModel.__table__
