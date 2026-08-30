import hmac
from dataclasses import dataclass
from uuid import uuid4

from app.application.passwords import PasswordHasher
from app.application.revocations import SessionRevocationStore
from app.application.tokens import TokenCodec, TokenPair
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import Account, Session
from app.domain.enums import AccountStatus
from app.domain.exceptions import AuthenticationError, AuthorizationError


@dataclass(frozen=True, slots=True)
class LoginContext:
    ip: str
    user_agent: str


class OAuthService:
    """Password authentication, refresh rotation, and bearer-token validation."""

    def __init__(
        self,
        unit_of_work: UnitOfWork,
        token_codec: TokenCodec,
        revocations: SessionRevocationStore,
    ) -> None:
        self._uow = unit_of_work
        self._tokens = token_codec
        self._revocations = revocations

    async def login(
        self,
        *,
        username: str,
        password: str,
        context: LoginContext,
        password_hasher: PasswordHasher,
    ) -> TokenPair:
        normalized_username = username.strip().lower()
        async with self._uow:
            account = await self._uow.accounts.get_by_identifier(
                type="email",
                value=normalized_username,
                provider=None,
            )
            if account is None or account.password is None:
                raise AuthenticationError("Invalid username or password")
            if not await password_hasher.verify(password, account.password.hash):
                raise AuthenticationError("Invalid username or password")

            self._ensure_account_can_authenticate(account)
            session_id = uuid4()
            pair = self._tokens.issue_pair(account_id=account.id, session_id=session_id)
            session = Session(
                account_id=account.id,
                ip=context.ip,
                user_agent=context.user_agent,
                refresh_token_hash=self._tokens.hash_refresh_token(pair.refresh_token),
                expires_at=pair.refresh_expires_at,
            )
            session.id = session_id
            account.sessions.append(session)
            account.touch()
            await self._uow.commit()
            return pair

    async def refresh(self, refresh_token: str) -> TokenPair:
        claims = self._tokens.decode(refresh_token, expected_kind="refresh")
        if await self._revocations.is_revoked(claims.session_id):
            raise AuthenticationError("Invalid refresh token")
        async with self._uow:
            account = await self._uow.accounts.get(claims.account_id)
            if account is None:
                raise AuthenticationError("Invalid refresh token")
            self._ensure_account_can_authenticate(account)
            session = self._find_session(account, claims.session_id)
            if session is None or session.is_expired():
                raise AuthenticationError("Invalid refresh token")
            if not hmac.compare_digest(
                session.refresh_token_hash,
                self._tokens.hash_refresh_token(refresh_token),
            ):
                # A previously valid refresh token was replayed after rotation.
                # End the whole session so the newer token cannot be used by an attacker.
                await self._revocations.revoke(session.id, expires_at=session.expires_at)
                account.sessions.remove(session)
                await self._uow.commit()
                raise AuthenticationError("Invalid refresh token")

            pair = self._tokens.issue_pair(account_id=account.id, session_id=session.id)
            session.refresh(
                refresh_token_hash=self._tokens.hash_refresh_token(pair.refresh_token),
                expires_at=pair.refresh_expires_at,
            )
            account.touch()
            await self._uow.commit()
            return pair

    async def authenticate_access_token(self, access_token: str) -> Account:
        claims = self._tokens.decode(access_token, expected_kind="access")
        if await self._revocations.is_revoked(claims.session_id):
            raise AuthenticationError("Invalid access token")
        async with self._uow:
            account = await self._uow.accounts.get(claims.account_id)
            if account is None:
                raise AuthenticationError("Invalid access token")
            self._ensure_account_can_authenticate(account)
            session = self._find_session(account, claims.session_id)
            if session is None or session.is_expired():
                raise AuthenticationError("Invalid access token")
            return account

    async def revoke(self, token: str) -> None:
        try:
            claims = self._tokens.decode(token)
        except AuthenticationError:
            return

        async with self._uow:
            account = await self._uow.accounts.get(claims.account_id)
            if account is None:
                return
            session = self._find_session(account, claims.session_id)
            if session is None:
                return
            await self._revocations.revoke(session.id, expires_at=session.expires_at)
            account.sessions.remove(session)
            await self._uow.commit()

    @staticmethod
    def _find_session(account: Account, session_id: object) -> Session | None:
        return next((session for session in account.sessions if session.id == session_id), None)

    @staticmethod
    def _ensure_account_can_authenticate(account: Account) -> None:
        if account.status is not AccountStatus.ACTIVE:
            raise AuthorizationError("Account is not active")
        if account.is_2fa_enforced:
            raise AuthorizationError("Second factor is required")
