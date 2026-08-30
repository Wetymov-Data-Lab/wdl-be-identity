from fastapi import APIRouter, status
from wdl_shared.schemas.identity import AccountRegistrationModel, AccountResponseModel

from app.application.services.registrations import ProfileCreateData, RegistrationService
from app.presentation.api.presenters import to_account_response
from app.presentation.api.routers._dependencies import AccountUow, PasswordHasherDep

router = APIRouter(prefix="/accounts")


@router.post(
    "/",
    tags=["Registration"],
    response_model=AccountResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def register_account(
    body: AccountRegistrationModel,
    uow: AccountUow,
    password_hasher: PasswordHasherDep,
) -> AccountResponseModel:
    profile = ProfileCreateData(
        display_name=body.profile.display_name,
        given_name=body.profile.given_name,
        family_name=body.profile.family_name,
        bio=body.profile.bio,
        job_title=body.profile.job_title,
        organization=body.profile.organization,
        locale=body.profile.locale,
        time_zone=body.profile.time_zone,
        picture_url=body.profile.picture_url,
        website_url=body.profile.website_url,
    )
    account = await RegistrationService(uow).register(
        email=str(body.email),
        password=body.password.get_secret_value(),
        profile=profile,
        password_hasher=password_hasher,
    )
    return to_account_response(account)
