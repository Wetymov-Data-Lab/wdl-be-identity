from dataclasses import asdict, dataclass

from app.application.passwords import PasswordHasher
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import Account, Identifier, Password, Profile
from app.domain.enums import AccountStatus, AccountSubject
from app.domain.exceptions import EntityAlreadyExistsError


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


class RegistrationService:
    """Atomically creates an account and its initial identity entities."""

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._uow = unit_of_work

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
