from datetime import datetime
from uuid import UUID

from sqlalchemy import CheckConstraint, DateTime, ForeignKey, Integer, Text, UniqueConstraint, Uuid, text
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class PasswordModel(Base):
    __tablename__ = "passwords"
    __table_args__ = (
        CheckConstraint("version >= 1", name="ck_passwords_version_positive"),
        UniqueConstraint("account_id", name="uq_passwords_account_id"),
    )

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE")
    )
    hash: Mapped[str] = mapped_column(Text)
    set_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    version: Mapped[int] = mapped_column(Integer, default=1, server_default=text("1"))


passwords = PasswordModel.__table__
