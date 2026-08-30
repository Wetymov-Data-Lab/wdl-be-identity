from abc import ABC, abstractmethod
from types import TracebackType

from app.application.repositories import AccountRepository


class UnitOfWork(ABC):
    """Transaction boundary for an application use case."""

    async def __aenter__(self) -> "UnitOfWork":
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_value: BaseException | None,
        traceback: TracebackType | None,
    ) -> None:
        await self.rollback()

    @property
    @abstractmethod
    def accounts(self) -> AccountRepository:
        """Account repository bound to the current transaction."""

    @abstractmethod
    async def commit(self) -> None:
        """Commit all changes made by the use case."""

    @abstractmethod
    async def rollback(self) -> None:
        """Roll back all uncommitted changes."""
