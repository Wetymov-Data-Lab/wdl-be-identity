from uuid import UUID

from wdl_be_identity.application.passwords import PasswordHasher
from wdl_be_identity.application.services._account_entities import get_account
from wdl_be_identity.application.unit_of_work import UnitOfWork
from wdl_be_identity.domain.entities import Password
from wdl_be_identity.domain.exceptions import EntityNotFoundError


class PasswordService:
    """Application operations over account passwords."""

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._uow = unit_of_work

    async def set(
        self,
        account_id: UUID,
        *,
        password: str,
        password_hasher: PasswordHasher,
    ) -> Password:
        password_hash = await password_hasher.hash(password)

        async with self._uow:
            account = await get_account(self._uow, account_id)
            if account.password is None:
                account.password = Password(account_id=account.id, hash=password_hash)
            else:
                account.password.change(new_hash=password_hash)
            await self._uow.commit()
            return account.password

    async def delete(self, account_id: UUID) -> None:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            if account.password is None:
                raise EntityNotFoundError("Password was not found")
            account.password = None
            await self._uow.commit()
