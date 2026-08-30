from collections.abc import Iterable
from uuid import UUID

from wdl_be_identity.application.unit_of_work import UnitOfWork
from wdl_be_identity.domain.entities import Account
from wdl_be_identity.domain.entities.base import Entity
from wdl_be_identity.domain.exceptions import EntityNotFoundError


async def get_account(unit_of_work: UnitOfWork, account_id: UUID) -> Account:
    account = await unit_of_work.accounts.get(account_id)
    if account is None:
        raise EntityNotFoundError(f"Account {account_id} was not found")
    return account


def find_account_entity[EntityT: Entity[UUID]](
    entities: Iterable[EntityT],
    entity_id: UUID,
    entity_name: str,
) -> EntityT:
    entity = next((item for item in entities if item.id == entity_id), None)
    if entity is None:
        raise EntityNotFoundError(f"{entity_name} {entity_id} was not found")
    return entity
