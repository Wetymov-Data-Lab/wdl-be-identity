from uuid import UUID

from app.application.services._account_entities import get_account
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import Profile
from app.domain.exceptions import EntityNotFoundError


class ProfileService:
    """Application operations over account profiles."""

    def __init__(self, unit_of_work: UnitOfWork) -> None:
        self._uow = unit_of_work

    async def get(self, account_id: UUID) -> Profile:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            if account.profile is None:
                raise EntityNotFoundError("Profile was not found")
            return account.profile

    async def upsert(
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
            account = await get_account(self._uow, account_id)
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

    async def delete(self, account_id: UUID) -> None:
        async with self._uow:
            account = await get_account(self._uow, account_id)
            if account.profile is None:
                raise EntityNotFoundError("Profile was not found")
            account.profile = None
            await self._uow.commit()
