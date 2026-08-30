from uuid import UUID

from app.application.services._account_entities import find_account_entity, get_account
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import Account, Identifier
from app.domain.exceptions import EntityAlreadyExistsError, EntityNotFoundError


class IdentifierService:
    """Application operations over account identifiers."""

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._uow = unit_of_work

    async def get_account(
        self,
        *,
        type: str,
        value: str,
        provider: str | None,
    ) -> Account:
        async with self._uow:
            account = await self._uow.accounts.get_by_identifier(
                type=type,
                value=value,
                provider=provider,
            )
            if account is None:
                raise EntityNotFoundError("Account was not found")
            return account

    async def add(
        self,
        account_id: UUID,
        *,
        type: str,
        value: str,
        provider: str | None,
        provider_user_id: str | None,
        is_public_contact: bool,
        receive_notifications: bool,
    ) -> Identifier:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            existing = await self._uow.accounts.get_by_identifier(
                type=type,
                value=value,
                provider=provider,
            )
            if existing is not None:
                raise EntityAlreadyExistsError("Identifier already exists")
            identifier = Identifier(
                account_id=account.id,
                type=type,
                value=value,
                provider=provider,
                provider_user_id=provider_user_id,
                is_public_contact=is_public_contact,
                receive_notifications=receive_notifications,
            )
            account.identifiers.append(identifier)
            await self._uow.commit()
            return identifier

    async def verify(self, account_id: UUID, identifier_id: UUID) -> Identifier:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            identifier = find_account_entity(account.identifiers, identifier_id, "Identifier")
            identifier.verify()
            await self._uow.commit()
            return identifier

    async def touch(self, account_id: UUID, identifier_id: UUID) -> Identifier:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            identifier = find_account_entity(account.identifiers, identifier_id, "Identifier")
            identifier.touch()
            await self._uow.commit()
            return identifier

    async def update_preferences(
        self,
        account_id: UUID,
        identifier_id: UUID,
        *,
        is_public_contact: bool,
        receive_notifications: bool,
    ) -> Identifier:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            identifier = find_account_entity(account.identifiers, identifier_id, "Identifier")
            identifier.set_contact_preferences(
                is_public_contact=is_public_contact,
                receive_notifications=receive_notifications,
            )
            await self._uow.commit()
            return identifier

    async def delete(self, account_id: UUID, identifier_id: UUID) -> None:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            identifier = find_account_entity(account.identifiers, identifier_id, "Identifier")
            account.identifiers.remove(identifier)
            await self._uow.commit()
