from datetime import UTC, datetime
from uuid import UUID

from app.application.services._account_entities import find_account_entity, get_account
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import Session
from app.domain.exceptions import InvariantViolationError


class SessionService:
    """Application operations over account sessions."""

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._uow = unit_of_work

    async def add(
        self,
        account_id: UUID,
        *,
        ip: str,
        refresh_token_hash: str,
        user_agent: str,
        expires_at: datetime,
    ) -> Session:
        if expires_at <= datetime.now(UTC):
            raise InvariantViolationError(message_key="entities.session.INVALID_EXPIRATION")
        async with self._uow:
            account = await get_account(self._uow, account_id)
            session = Session(
                account_id=account.id,
                ip=ip,
                refresh_token_hash=refresh_token_hash,
                user_agent=user_agent,
                expires_at=expires_at,
            )
            account.sessions.append(session)
            await self._uow.commit()
            return session

    async def refresh(
        self,
        account_id: UUID,
        session_id: UUID,
        *,
        refresh_token_hash: str,
        expires_at: datetime,
    ) -> Session:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            session = find_account_entity(account.sessions, session_id, "Session")
            session.refresh(refresh_token_hash=refresh_token_hash, expires_at=expires_at)
            await self._uow.commit()
            return session

    async def delete(self, account_id: UUID, session_id: UUID) -> None:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            session = find_account_entity(account.sessions, session_id, "Session")
            account.sessions.remove(session)
            await self._uow.commit()
