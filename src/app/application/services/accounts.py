from uuid import UUID

from app.application.services._account_entities import get_account
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import Account


class AccountService:
    """Application operations that only affect the account itself."""

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._uow = unit_of_work

    async def list_accounts(self, *, limit: int, offset: int) -> list[Account]:
        async with self._uow:
            return await self._uow.accounts.list(limit=limit, offset=offset)

    async def get(self, account_id: UUID) -> Account:
        async with self._uow:
            return await get_account(self._uow, account_id)

    async def delete(self, account_id: UUID) -> None:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            await self._uow.accounts.remove(account)
            await self._uow.commit()

    async def transition(self, account_id: UUID, *, action: str) -> Account:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            transitions = {
                "activate": account.activate,
                "deactivate": account.deactivate,
                "restore": account.restore,
                "suspend": account.suspend,
                "unsuspend": account.unsuspend,
            }
            try:
                transition = transitions[action]
            except KeyError as error:
                raise ValueError(f"Unsupported account transition: {action}") from error
            transition()
            await self._uow.commit()
            return account

    async def touch(self, account_id: UUID) -> Account:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            account.touch()
            await self._uow.commit()
            return account
