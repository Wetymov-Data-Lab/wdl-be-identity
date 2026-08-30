from uuid import UUID

from app.application.services._account_entities import find_account_entity, get_account
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import RecoveryCode


class RecoveryCodeService:
    """Application operations over account recovery codes."""

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._uow = unit_of_work

    async def add(self, account_id: UUID, *, hash: str) -> RecoveryCode:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            code = RecoveryCode(account_id=account.id, hash=hash)
            account.recovery_codes.append(code)
            await self._uow.commit()
            return code

    async def use(self, account_id: UUID, code_id: UUID) -> RecoveryCode:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            code = find_account_entity(account.recovery_codes, code_id, "Recovery code")
            code.use()
            await self._uow.commit()
            return code

    async def delete(self, account_id: UUID, code_id: UUID) -> None:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            code = find_account_entity(account.recovery_codes, code_id, "Recovery code")
            account.recovery_codes.remove(code)
            await self._uow.commit()
