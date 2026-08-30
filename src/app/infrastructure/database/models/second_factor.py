from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Index, String, Text, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class SecondFactorModel(Base):
    __tablename__ = "second_factors"
    __table_args__ = (Index("ix_second_factors_account_id", "account_id"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE")
    )
    type: Mapped[str] = mapped_column(String(64))
    secret: Mapped[str] = mapped_column(Text)
    name: Mapped[str | None] = mapped_column(Text, default=None)
    confirmed_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))


second_factors = SecondFactorModel.__table__
