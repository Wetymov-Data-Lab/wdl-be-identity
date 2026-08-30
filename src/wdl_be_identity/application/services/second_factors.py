from uuid import UUID

from wdl_be_identity.application.services._account_entities import find_account_entity, get_account
from wdl_be_identity.application.unit_of_work import UnitOfWork
from wdl_be_identity.domain.entities import Account, SecondFactor


class SecondFactorService:
    """Application operations over account second factors."""

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._uow = unit_of_work

    async def set_policy(self, account_id: UUID, *, enforced: bool) -> Account:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            if enforced:
                account.enforce_2fa()
            else:
                account.relax_2fa()
            await self._uow.commit()
            return account

    async def add(
        self,
        account_id: UUID,
        *,
        type: str,
        secret: str,
        name: str | None,
    ) -> SecondFactor:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            factor = SecondFactor(
                account_id=account.id,
                type=type,
                secret=secret,
                name=name,
            )
            account.second_factors.append(factor)
            await self._uow.commit()
            return factor

    async def confirm(self, account_id: UUID, factor_id: UUID) -> SecondFactor:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            factor = find_account_entity(account.second_factors, factor_id, "Second factor")
            factor.confirm()
            await self._uow.commit()
            return factor

    async def delete(self, account_id: UUID, factor_id: UUID) -> None:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            factor = find_account_entity(account.second_factors, factor_id, "Second factor")
            account.second_factors.remove(factor)
            await self._uow.commit()
