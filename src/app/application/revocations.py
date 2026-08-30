from datetime import datetime
from typing import Protocol
from uuid import UUID


class SessionRevocationStore(Protocol):
    """Fast revocation state shared by every identity-service instance."""

    async def is_revoked(self, session_id: UUID) -> bool: ...

    async def revoke(self, session_id: UUID, *, expires_at: datetime) -> None: ...
