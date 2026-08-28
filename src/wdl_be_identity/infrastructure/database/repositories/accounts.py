from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from wdl_be_identity.application.repositories import AccountRepository
from wdl_be_identity.domain.entities.account import Account
from wdl_be_identity.infrastructure.database.models.identity import accounts, identifiers


class SQLAlchemyAccountRepository(AccountRepository):
    """SQLAlchemy adapter for the account aggregate."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def list(self, *, limit: int, offset: int) -> list[Account]:
        result = await self._session.scalars(
            select(Account).order_by(accounts.c.created_at, accounts.c.id).limit(limit).offset(offset)
        )
        return list(result.all())

    async def get(self, entity_id: UUID) -> Account | None:
        account = await self._session.scalar(select(Account).where(accounts.c.id == entity_id))
        return account

    async def get_by_identifier(
        self,
        *,
        type: str,
        value: str,
        provider: str | None = None,
    ) -> Account | None:
        query = (
            select(Account)
            .join(identifiers, accounts.c.id == identifiers.c.account_id)
            .where(
                identifiers.c.type == type,
                identifiers.c.value == value,
            )
        )
        if provider is None:
            query = query.where(identifiers.c.provider.is_(None))
        else:
            query = query.where(identifiers.c.provider == provider)

        account = await self._session.scalar(query)
        return account

    async def add(self, entity: Account) -> None:
        self._session.add(entity)

    async def remove(self, entity: Account) -> None:
        await self._session.delete(entity)
