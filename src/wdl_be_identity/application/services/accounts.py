from dataclasses import asdict, dataclass
from datetime import UTC, datetime
from uuid import UUID

from wdl_be_identity.application.passwords import PasswordHasher
from wdl_be_identity.application.unit_of_work import UnitOfWork
from wdl_be_identity.domain.entities import (
    Account,
    Identifier,
    Password,
    Profile,
    RecoveryCode,
    SecondFactor,
    Session,
)
from wdl_be_identity.domain.entities.base import Entity
from wdl_be_identity.domain.enums import AccountStatus, AccountSubject
from wdl_be_identity.domain.exceptions import (
    EntityAlreadyExistsError,
    EntityNotFoundError,
    InvariantViolationError,
)


@dataclass(frozen=True, slots=True)
class ProfileCreateData:
    display_name: str
    given_name: str | None = None
    family_name: str | None = None
    bio: str | None = None
    job_title: str | None = None
    organization: str | None = None
    locale: str | None = None
    time_zone: str | None = None
    picture_url: str | None = None
    website_url: str | None = None


class AccountService:
    """Application operations over the Account aggregate."""

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._uow = unit_of_work

    async def list_accounts(self, *, limit: int, offset: int) -> list[Account]:
        async with self._uow:
            return await self._uow.accounts.list(limit=limit, offset=offset)

    async def get(self, account_id: UUID) -> Account:
        async with self._uow:
            return await self._get_account(account_id)

    async def get_by_identifier(
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

    async def register(
        self,
        *,
        email: str,
        password: str,
        profile: ProfileCreateData,
        password_hasher: PasswordHasher,
    ) -> Account:
        normalized_email = email.strip().lower()
        password_hash = await password_hasher.hash(password)

        async with self._uow:
            existing = await self._uow.accounts.get_by_identifier(
                type="email",
                value=normalized_email,
                provider=None,
            )
            if existing is not None:
                raise EntityAlreadyExistsError("Email is already registered")

            account = Account(subject=AccountSubject.USER, status=AccountStatus.PENDING)
            account.profile = Profile(account_id=account.id, **asdict(profile))
            account.identifiers.append(
                Identifier(
                    account_id=account.id,
                    type="email",
                    value=normalized_email,
                    receive_notifications=True,
                )
            )
            account.password = Password(account_id=account.id, hash=password_hash)
            await self._uow.accounts.add(account)
            await self._uow.commit()
            return account

    async def delete(self, account_id: UUID) -> None:
        async with self._uow:
            account = await self._get_account(account_id)
            await self._uow.accounts.remove(account)
            await self._uow.commit()

    async def transition(self, account_id: UUID, *, action: str) -> Account:
        async with self._uow:
            account = await self._get_account(account_id)
            transitions = {
                "activate": account.activate,
                "deactivate": account.deactivate,
                "restore": account.restore,
                "suspend": account.suspend,
                "unsuspend": account.unsuspend,
            }
            try:
                transition = transitions[action]
            except KeyError as error:
                raise ValueError(f"Unsupported account transition: {action}") from error
            transition()
            await self._uow.commit()
            return account

    async def touch(self, account_id: UUID) -> Account:
        async with self._uow:
            account = await self._get_account(account_id)
            account.touch()
            await self._uow.commit()
            return account

    async def set_2fa_policy(self, account_id: UUID, *, enforced: bool) -> Account:
        async with self._uow:
            account = await self._get_account(account_id)
            if enforced:
                account.enforce_2fa()
            else:
                account.relax_2fa()
            await self._uow.commit()
            return account

    async def upsert_profile(
        self,
        account_id: UUID,
        *,
        display_name: str,
        given_name: str | None,
        family_name: str | None,
        bio: str | None,
        job_title: str | None,
        organization: str | None,
        locale: str | None,
        time_zone: str | None,
        picture_url: str | None,
        website_url: str | None,
    ) -> Profile:
        async with self._uow:
            account = await self._get_account(account_id)
            if account.profile is None:
                account.profile = Profile(
                    account_id=account.id,
                    display_name=display_name,
                    given_name=given_name,
                    family_name=family_name,
                    bio=bio,
                    job_title=job_title,
                    organization=organization,
                    locale=locale,
                    time_zone=time_zone,
                    picture_url=picture_url,
                    website_url=website_url,
                )
            else:
                account.profile.update(
                    display_name=display_name,
                    given_name=given_name,
                    family_name=family_name,
                    bio=bio,
                    job_title=job_title,
                    organization=organization,
                    locale=locale,
                    time_zone=time_zone,
                    picture_url=picture_url,
                    website_url=website_url,
                )
            await self._uow.commit()
            return account.profile

    async def delete_profile(self, account_id: UUID) -> None:
        async with self._uow:
            account = await self._get_account(account_id)
            if account.profile is None:
                raise EntityNotFoundError("Profile was not found")
            account.profile = None
            await self._uow.commit()

    async def set_password(
        self,
        account_id: UUID,
        *,
        password: str,
        password_hasher: PasswordHasher,
    ) -> Password:
        password_hash = await password_hasher.hash(password)

        async with self._uow:
            account = await self._get_account(account_id)
            if account.password is None:
                account.password = Password(account_id=account.id, hash=password_hash)
            else:
                account.password.change(new_hash=password_hash)
            await self._uow.commit()
            return account.password

    async def delete_password(self, account_id: UUID) -> None:
        async with self._uow:
            account = await self._get_account(account_id)
            if account.password is None:
                raise EntityNotFoundError("Password was not found")
            account.password = None
            await self._uow.commit()

    async def add_identifier(
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
            account = await self._get_account(account_id)
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

    async def verify_identifier(self, account_id: UUID, identifier_id: UUID) -> Identifier:
        async with self._uow:
            account = await self._get_account(account_id)
            identifier = self._find(account.identifiers, identifier_id, "Identifier")
            identifier.verify()
            await self._uow.commit()
            return identifier

    async def touch_identifier(self, account_id: UUID, identifier_id: UUID) -> Identifier:
        async with self._uow:
            account = await self._get_account(account_id)
            identifier = self._find(account.identifiers, identifier_id, "Identifier")
            identifier.touch()
            await self._uow.commit()
            return identifier

    async def update_identifier_preferences(
        self,
        account_id: UUID,
        identifier_id: UUID,
        *,
        is_public_contact: bool,
        receive_notifications: bool,
    ) -> Identifier:
        async with self._uow:
            account = await self._get_account(account_id)
            identifier = self._find(account.identifiers, identifier_id, "Identifier")
            identifier.set_contact_preferences(
                is_public_contact=is_public_contact,
                receive_notifications=receive_notifications,
            )
            await self._uow.commit()
            return identifier

    async def delete_identifier(self, account_id: UUID, identifier_id: UUID) -> None:
        async with self._uow:
            account = await self._get_account(account_id)
            identifier = self._find(account.identifiers, identifier_id, "Identifier")
            account.identifiers.remove(identifier)
            await self._uow.commit()

    async def add_second_factor(
        self,
        account_id: UUID,
        *,
        type: str,
        secret: str,
        name: str | None,
    ) -> SecondFactor:
        async with self._uow:
            account = await self._get_account(account_id)
            factor = SecondFactor(
                account_id=account.id,
                type=type,
                secret=secret,
                name=name,
            )
            account.second_factors.append(factor)
            await self._uow.commit()
            return factor

    async def confirm_second_factor(self, account_id: UUID, factor_id: UUID) -> SecondFactor:
        async with self._uow:
            account = await self._get_account(account_id)
            factor = self._find(account.second_factors, factor_id, "Second factor")
            factor.confirm()
            await self._uow.commit()
            return factor

    async def delete_second_factor(self, account_id: UUID, factor_id: UUID) -> None:
        async with self._uow:
            account = await self._get_account(account_id)
            factor = self._find(account.second_factors, factor_id, "Second factor")
            account.second_factors.remove(factor)
            await self._uow.commit()

    async def add_recovery_code(self, account_id: UUID, *, hash: str) -> RecoveryCode:
        async with self._uow:
            account = await self._get_account(account_id)
            code = RecoveryCode(account_id=account.id, hash=hash)
            account.recovery_codes.append(code)
            await self._uow.commit()
            return code

    async def use_recovery_code(self, account_id: UUID, code_id: UUID) -> RecoveryCode:
        async with self._uow:
            account = await self._get_account(account_id)
            code = self._find(account.recovery_codes, code_id, "Recovery code")
            code.use()
            await self._uow.commit()
            return code

    async def delete_recovery_code(self, account_id: UUID, code_id: UUID) -> None:
        async with self._uow:
            account = await self._get_account(account_id)
            code = self._find(account.recovery_codes, code_id, "Recovery code")
            account.recovery_codes.remove(code)
            await self._uow.commit()

    async def add_session(
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
            account = await self._get_account(account_id)
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

    async def refresh_session(
        self,
        account_id: UUID,
        session_id: UUID,
        *,
        refresh_token_hash: str,
        expires_at: datetime,
    ) -> Session:
        async with self._uow:
            account = await self._get_account(account_id)
            session = self._find(account.sessions, session_id, "Session")
            session.refresh(refresh_token_hash=refresh_token_hash, expires_at=expires_at)
            await self._uow.commit()
            return session

    async def delete_session(self, account_id: UUID, session_id: UUID) -> None:
        async with self._uow:
            account = await self._get_account(account_id)
            session = self._find(account.sessions, session_id, "Session")
            account.sessions.remove(session)
            await self._uow.commit()

    async def _get_account(self, account_id: UUID) -> Account:
        account = await self._uow.accounts.get(account_id)
        if account is None:
            raise EntityNotFoundError(f"Account {account_id} was not found")
        return account

    @staticmethod
    def _find[EntityT: Entity[UUID]](
        entities: list[EntityT],
        entity_id: UUID,
        entity_name: str,
    ) -> EntityT:
        entity = next((item for item in entities if item.id == entity_id), None)
        if entity is None:
            raise EntityNotFoundError(f"{entity_name} {entity_id} was not found")
        return entity
