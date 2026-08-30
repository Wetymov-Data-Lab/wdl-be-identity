from uuid import UUID

from fastapi import APIRouter, Depends, Response, status
from wdl_shared.schemas.identity import ProfileResponseModel, ProfileUpdateModel

from app.application.services.profiles import ProfileService
from app.presentation.api.dependencies.authentication import get_current_account
from app.presentation.api.presenters import to_profile_response
from app.presentation.api.routers._dependencies import AccountUow

router = APIRouter(prefix="/profiles", dependencies=[Depends(get_current_account)])


@router.get("/{account_id}", tags=["Profiles"], response_model=ProfileResponseModel)
async def get_profile(account_id: UUID, uow: AccountUow) -> ProfileResponseModel:
    return to_profile_response(await ProfileService(uow).get(account_id))


@router.put("/{account_id}", tags=["Profiles"], response_model=ProfileResponseModel)
async def upsert_profile(
    account_id: UUID,
    body: ProfileUpdateModel,
    uow: AccountUow,
) -> ProfileResponseModel:
    profile = await ProfileService(uow).upsert(
        account_id,
        display_name=body.display_name,
        given_name=body.given_name,
        family_name=body.family_name,
        bio=body.bio,
        job_title=body.job_title,
        organization=body.organization,
        locale=body.locale,
        time_zone=body.time_zone,
        picture_url=body.picture_url,
        website_url=body.website_url,
    )
    return to_profile_response(profile)


@router.delete(
    "/{account_id}",
    tags=["Profiles"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_profile(account_id: UUID, uow: AccountUow) -> Response:
    await ProfileService(uow).delete(account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
