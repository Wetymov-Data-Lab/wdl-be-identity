from uuid import UUID

from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from app.application.repositories import AccountRepository
from app.domain.entities import Account
from app.infrastructure.database.mappers import AccountMapper
from app.infrastructure.database.models import AccountModel, IdentifierModel


class SQLAlchemyAccountRepository(AccountRepository):
    """SQLAlchemy adapter between declarative rows and domain aggregates."""

    def __init__(self, session: AsyncSession) -> None:
        self._session = session
        self._tracked: dict[UUID, tuple[Account, AccountModel | None]] = {}

    async def list(self, *, limit: int, offset: int) -> list[Account]:
        result = await self._session.scalars(
            select(AccountModel).order_by(AccountModel.created_at, AccountModel.id).limit(limit).offset(offset)
        )
        return [self._track(model) for model in result.all()]

    async def get(self, entity_id: UUID) -> Account | None:
        tracked = self._tracked.get(entity_id)
        if tracked is not None:
            return tracked[0]

        model = await self._session.get(AccountModel, entity_id)
        return None if model is None else self._track(model)

    async def get_by_identifier(
        self,
        *,
        type: str,
        value: str,
        provider: str | None = None,
    ) -> Account | None:
        query = (
            select(AccountModel)
            .join(IdentifierModel, AccountModel.id == IdentifierModel.account_id)
            .where(
                IdentifierModel.type == type,
                IdentifierModel.value == value,
            )
        )
        if provider is None:
            query = query.where(IdentifierModel.provider.is_(None))
        else:
            query = query.where(IdentifierModel.provider == provider)

        model = await self._session.scalar(query)
        return None if model is None else self._track(model)

    async def add(self, entity: Account) -> None:
        self._tracked[entity.id] = (entity, None)

    async def remove(self, entity: Account) -> None:
        tracked = self._tracked.pop(entity.id, None)
        model = tracked[1] if tracked is not None else await self._session.get(AccountModel, entity.id)
        if model is not None:
            await self._session.delete(model)

    async def flush(self) -> None:
        """Merge tracked domain aggregates into the ORM identity map."""
        for account_id, (account, model) in list(self._tracked.items()):
            mapped = AccountMapper.to_model(account)
            if model is None:
                self._session.add(mapped)
                model = mapped
            else:
                model = await self._session.merge(mapped)
            self._tracked[account_id] = (account, model)
        await self._session.flush()

    def accept_changes(self) -> None:
        """Copy database-managed aggregate values back after a commit."""
        for account, model in self._tracked.values():
            if model is None:
                raise RuntimeError("Tracked account was not flushed")
            account.version = model.version

    def _track(self, model: AccountModel) -> Account:
        tracked = self._tracked.get(model.id)
        if tracked is not None:
            return tracked[0]

        account = AccountMapper.to_domain(model)
        self._tracked[model.id] = (account, model)
        return account
