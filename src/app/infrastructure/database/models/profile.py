from datetime import datetime
from uuid import UUID

from sqlalchemy import DateTime, ForeignKey, Text, UniqueConstraint, Uuid
from sqlalchemy.orm import Mapped, mapped_column

from app.infrastructure.database.base import Base


class ProfileModel(Base):
    __tablename__ = "profiles"
    __table_args__ = (UniqueConstraint("account_id", name="uq_profiles_account_id"),)

    id: Mapped[UUID] = mapped_column(Uuid(as_uuid=True), primary_key=True)
    account_id: Mapped[UUID] = mapped_column(
        Uuid(as_uuid=True), ForeignKey("accounts.id", ondelete="CASCADE")
    )
    display_name: Mapped[str] = mapped_column(Text)
    given_name: Mapped[str | None] = mapped_column(Text, default=None)
    family_name: Mapped[str | None] = mapped_column(Text, default=None)
    bio: Mapped[str | None] = mapped_column(Text, default=None)
    job_title: Mapped[str | None] = mapped_column(Text, default=None)
    organization: Mapped[str | None] = mapped_column(Text, default=None)
    locale: Mapped[str | None] = mapped_column(Text, default=None)
    time_zone: Mapped[str | None] = mapped_column(Text, default=None)
    picture_url: Mapped[str | None] = mapped_column(Text, default=None)
    website_url: Mapped[str | None] = mapped_column(Text, default=None)
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True))
    updated_at: Mapped[datetime | None] = mapped_column(DateTime(timezone=True), default=None)


profiles = ProfileModel.__table__
