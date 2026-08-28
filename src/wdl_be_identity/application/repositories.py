from abc import ABC, abstractmethod
from typing import Any
from uuid import UUID

from wdl_be_identity.domain.entities.account import Account
from wdl_be_identity.domain.entities.base import Entity


class Repository[EntityT: Entity[Any], EntityId](ABC):
    """Persistence contract used by application use cases."""

    @abstractmethod
    async def get(self, entity_id: EntityId) -> EntityT | None:
        """Return an entity by identity or None."""

    @abstractmethod
    async def add(self, entity: EntityT) -> None:
        """Add an entity to the current unit of work."""

    @abstractmethod
    async def remove(self, entity: EntityT) -> None:
        """Remove an entity from the current unit of work."""


class AccountRepository(Repository[Account, UUID], ABC):
    """Persistence contract for the account aggregate."""

    @abstractmethod
    async def get_by_identifier(
        self,
        *,
        type: str,
        value: str,
        provider: str | None = None,
    ) -> Account | None:
        """Return the account owning an identifier, if one exists."""
