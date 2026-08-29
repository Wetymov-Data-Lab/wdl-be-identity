from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from wdl_shared.schemas.identity import (
    AccountRegistrationModel,
    AccountResponseModel,
    IdentifierCreateModel,
    IdentifierPreferencesUpdateModel,
    IdentifierResponseModel,
    PasswordResponseModel,
    PasswordSetModel,
    ProfileResponseModel,
    ProfileUpdateModel,
    RecoveryCodeCreateModel,
    RecoveryCodeResponseModel,
    SecondFactorCreateModel,
    SecondFactorResponseModel,
    SessionCreateModel,
    SessionRefreshModel,
    SessionResponseModel,
    TwoFactorPolicyUpdateModel,
)

from wdl_be_identity.application.passwords import PasswordHasher
from wdl_be_identity.application.services.accounts import AccountService, ProfileCreateData
from wdl_be_identity.application.unit_of_work import UnitOfWork
from wdl_be_identity.presentation.api.dependencies.passwords import get_password_hasher
from wdl_be_identity.presentation.api.dependencies.unit_of_work import get_account_uow
from wdl_be_identity.presentation.api.presenters import (
    to_account_response,
    to_identifier_response,
    to_password_response,
    to_profile_response,
    to_recovery_code_response,
    to_second_factor_response,
    to_session_response,
)

router = APIRouter(prefix="/accounts")
AccountUow = Annotated[UnitOfWork, Depends(get_account_uow)]
PasswordHasherDep = Annotated[PasswordHasher, Depends(get_password_hasher)]


@router.get("/", tags=["Accounts"], response_model=list[AccountResponseModel])
async def list_accounts(
    uow: AccountUow,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[AccountResponseModel]:
    accounts = await AccountService(uow).list_accounts(limit=limit, offset=offset)
    return [to_account_response(account) for account in accounts]


@router.get("/by-identifier", tags=["Identifiers"], response_model=AccountResponseModel)
async def get_account_by_identifier(
    uow: AccountUow,
    type: Annotated[str, Query(min_length=1, max_length=64)],
    value: Annotated[str, Query(min_length=1, max_length=2_048)],
    provider: Annotated[str | None, Query(max_length=128)] = None,
) -> AccountResponseModel:
    account = await AccountService(uow).get_by_identifier(
        type=type,
        value=value,
        provider=provider,
    )
    return to_account_response(account)


@router.get("/{account_id}", tags=["Accounts"], response_model=AccountResponseModel)
async def get_account(account_id: UUID, uow: AccountUow) -> AccountResponseModel:
    return to_account_response(await AccountService(uow).get(account_id))


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
    account = await AccountService(uow).register(
        email=str(body.email),
        password=body.password.get_secret_value(),
        profile=profile,
        password_hasher=password_hasher,
    )
    return to_account_response(account)


@router.delete("/{account_id}", tags=["Accounts"], status_code=status.HTTP_204_NO_CONTENT)
async def delete_account(account_id: UUID, uow: AccountUow) -> Response:
    await AccountService(uow).delete(account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


async def transition_account(account_id: UUID, action: str, uow: UnitOfWork) -> AccountResponseModel:
    account = await AccountService(uow).transition(account_id, action=action)
    return to_account_response(account)


@router.post("/{account_id}/activate", tags=["Accounts"], response_model=AccountResponseModel)
async def activate_account(account_id: UUID, uow: AccountUow) -> AccountResponseModel:
    return await transition_account(account_id, "activate", uow)


@router.post("/{account_id}/deactivate", tags=["Accounts"], response_model=AccountResponseModel)
async def deactivate_account(account_id: UUID, uow: AccountUow) -> AccountResponseModel:
    return await transition_account(account_id, "deactivate", uow)


@router.post("/{account_id}/restore", tags=["Accounts"], response_model=AccountResponseModel)
async def restore_account(account_id: UUID, uow: AccountUow) -> AccountResponseModel:
    return await transition_account(account_id, "restore", uow)


@router.post("/{account_id}/suspend", tags=["Accounts"], response_model=AccountResponseModel)
async def suspend_account(account_id: UUID, uow: AccountUow) -> AccountResponseModel:
    return await transition_account(account_id, "suspend", uow)


@router.post("/{account_id}/unsuspend", tags=["Accounts"], response_model=AccountResponseModel)
async def unsuspend_account(account_id: UUID, uow: AccountUow) -> AccountResponseModel:
    return await transition_account(account_id, "unsuspend", uow)


@router.post("/{account_id}/touch", tags=["Accounts"], response_model=AccountResponseModel)
async def touch_account(account_id: UUID, uow: AccountUow) -> AccountResponseModel:
    return to_account_response(await AccountService(uow).touch(account_id))


@router.put(
    "/{account_id}/2fa-policy",
    tags=["Second Factors"],
    response_model=AccountResponseModel,
)
async def update_2fa_policy(
    account_id: UUID,
    body: TwoFactorPolicyUpdateModel,
    uow: AccountUow,
) -> AccountResponseModel:
    account = await AccountService(uow).set_2fa_policy(account_id, enforced=body.enforced)
    return to_account_response(account)


@router.get("/{account_id}/profile", tags=["Profiles"], response_model=ProfileResponseModel)
async def get_profile(
    account_id: UUID,
    uow: AccountUow,
) -> ProfileResponseModel:
    account = await AccountService(uow).get(account_id=account_id)
    return to_profile_response(account.profile)


@router.put("/{account_id}/profile", tags=["Profiles"], response_model=ProfileResponseModel)
async def upsert_profile(
    account_id: UUID,
    body: ProfileUpdateModel,
    uow: AccountUow,
) -> ProfileResponseModel:
    profile = await AccountService(uow).upsert_profile(
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
    "/{account_id}/profile",
    tags=["Profiles"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_profile(account_id: UUID, uow: AccountUow) -> Response:
    await AccountService(uow).delete_profile(account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.put("/{account_id}/password", tags=["Passwords"], response_model=PasswordResponseModel)
async def set_password(
    account_id: UUID,
    body: PasswordSetModel,
    uow: AccountUow,
    password_hasher: PasswordHasherDep,
) -> PasswordResponseModel:
    password = await AccountService(uow).set_password(
        account_id,
        password=body.password.get_secret_value(),
        password_hasher=password_hasher,
    )
    return to_password_response(password)


@router.delete(
    "/{account_id}/password",
    tags=["Passwords"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_password(account_id: UUID, uow: AccountUow) -> Response:
    await AccountService(uow).delete_password(account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{account_id}/identifiers",
    tags=["Identifiers"],
    response_model=IdentifierResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_identifier(
    account_id: UUID,
    body: IdentifierCreateModel,
    uow: AccountUow,
) -> IdentifierResponseModel:
    identifier = await AccountService(uow).add_identifier(
        account_id,
        type=body.type,
        value=body.value,
        provider=body.provider,
        provider_user_id=body.provider_user_id,
        is_public_contact=body.is_public_contact,
        receive_notifications=body.receive_notifications,
    )
    return to_identifier_response(identifier)


@router.post(
    "/{account_id}/identifiers/{identifier_id}/verify",
    tags=["Identifiers"],
    response_model=IdentifierResponseModel,
)
async def verify_identifier(
    account_id: UUID,
    identifier_id: UUID,
    uow: AccountUow,
) -> IdentifierResponseModel:
    identifier = await AccountService(uow).verify_identifier(account_id, identifier_id)
    return to_identifier_response(identifier)


@router.post(
    "/{account_id}/identifiers/{identifier_id}/touch",
    tags=["Identifiers"],
    response_model=IdentifierResponseModel,
)
async def touch_identifier(
    account_id: UUID,
    identifier_id: UUID,
    uow: AccountUow,
) -> IdentifierResponseModel:
    identifier = await AccountService(uow).touch_identifier(account_id, identifier_id)
    return to_identifier_response(identifier)


@router.patch(
    "/{account_id}/identifiers/{identifier_id}/preferences",
    tags=["Identifiers"],
    response_model=IdentifierResponseModel,
)
async def update_identifier_preferences(
    account_id: UUID,
    identifier_id: UUID,
    body: IdentifierPreferencesUpdateModel,
    uow: AccountUow,
) -> IdentifierResponseModel:
    identifier = await AccountService(uow).update_identifier_preferences(
        account_id,
        identifier_id,
        is_public_contact=body.is_public_contact,
        receive_notifications=body.receive_notifications,
    )
    return to_identifier_response(identifier)


@router.delete(
    "/{account_id}/identifiers/{identifier_id}",
    tags=["Identifiers"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_identifier(account_id: UUID, identifier_id: UUID, uow: AccountUow) -> Response:
    await AccountService(uow).delete_identifier(account_id, identifier_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{account_id}/second-factors",
    tags=["Second Factors"],
    response_model=SecondFactorResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_second_factor(
    account_id: UUID,
    body: SecondFactorCreateModel,
    uow: AccountUow,
) -> SecondFactorResponseModel:
    factor = await AccountService(uow).add_second_factor(
        account_id,
        type=body.type,
        secret=body.secret,
        name=body.name,
    )
    return to_second_factor_response(factor)


@router.post(
    "/{account_id}/second-factors/{factor_id}/confirm",
    tags=["Second Factors"],
    response_model=SecondFactorResponseModel,
)
async def confirm_second_factor(
    account_id: UUID,
    factor_id: UUID,
    uow: AccountUow,
) -> SecondFactorResponseModel:
    factor = await AccountService(uow).confirm_second_factor(account_id, factor_id)
    return to_second_factor_response(factor)


@router.delete(
    "/{account_id}/second-factors/{factor_id}",
    tags=["Second Factors"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_second_factor(account_id: UUID, factor_id: UUID, uow: AccountUow) -> Response:
    await AccountService(uow).delete_second_factor(account_id, factor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{account_id}/recovery-codes",
    tags=["Recovery Codes"],
    response_model=RecoveryCodeResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_recovery_code(
    account_id: UUID,
    body: RecoveryCodeCreateModel,
    uow: AccountUow,
) -> RecoveryCodeResponseModel:
    code = await AccountService(uow).add_recovery_code(account_id, hash=body.hash)
    return to_recovery_code_response(code)


@router.post(
    "/{account_id}/recovery-codes/{code_id}/use",
    tags=["Recovery Codes"],
    response_model=RecoveryCodeResponseModel,
)
async def use_recovery_code(
    account_id: UUID,
    code_id: UUID,
    uow: AccountUow,
) -> RecoveryCodeResponseModel:
    code = await AccountService(uow).use_recovery_code(account_id, code_id)
    return to_recovery_code_response(code)


@router.delete(
    "/{account_id}/recovery-codes/{code_id}",
    tags=["Recovery Codes"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recovery_code(account_id: UUID, code_id: UUID, uow: AccountUow) -> Response:
    await AccountService(uow).delete_recovery_code(account_id, code_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)


@router.post(
    "/{account_id}/sessions",
    tags=["Sessions"],
    response_model=SessionResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_session(
    account_id: UUID,
    body: SessionCreateModel,
    uow: AccountUow,
) -> SessionResponseModel:
    session = await AccountService(uow).add_session(
        account_id,
        ip=body.ip,
        refresh_token_hash=body.refresh_token_hash,
        user_agent=body.user_agent,
        expires_at=body.expires_at,
    )
    return to_session_response(session)


@router.post(
    "/{account_id}/sessions/{session_id}/refresh",
    tags=["Sessions"],
    response_model=SessionResponseModel,
)
async def refresh_session(
    account_id: UUID,
    session_id: UUID,
    body: SessionRefreshModel,
    uow: AccountUow,
) -> SessionResponseModel:
    session = await AccountService(uow).refresh_session(
        account_id,
        session_id,
        refresh_token_hash=body.refresh_token_hash,
        expires_at=body.expires_at,
    )
    return to_session_response(session)


@router.delete(
    "/{account_id}/sessions/{session_id}",
    tags=["Sessions"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_session(account_id: UUID, session_id: UUID, uow: AccountUow) -> Response:
    await AccountService(uow).delete_session(account_id, session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
