from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Depends, Query, Response, status
from wdl_shared.schemas.identity import (
    AccountResponseModel,
    IdentifierCreateModel,
    IdentifierPreferencesUpdateModel,
    IdentifierResponseModel,
)

from app.application.services.identifiers import IdentifierService
from app.domain.entities import Account
from app.domain.exceptions import EntityNotFoundError
from app.presentation.api.dependencies.authentication import (
    get_current_account,
    require_self_account,
)
from app.presentation.api.presenters import to_account_response, to_identifier_response
from app.presentation.api.routers._dependencies import AccountUow

router = APIRouter(prefix="/identifiers")


@router.get("/by-identifier", tags=["Identifiers"], response_model=AccountResponseModel)
async def get_account_by_identifier(
    uow: AccountUow,
    current_account: Annotated[Account, Depends(get_current_account)],
    type: Annotated[str, Query(min_length=1, max_length=64)],
    value: Annotated[str, Query(min_length=1, max_length=2_048)],
    provider: Annotated[str | None, Query(max_length=128)] = None,
) -> AccountResponseModel:
    del uow
    matches_current_account = any(
        identifier.type == type
        and identifier.value == value
        and identifier.provider == provider
        for identifier in current_account.identifiers
    )
    if not matches_current_account:
        raise EntityNotFoundError("Identifier was not found")
    return to_account_response(current_account)


@router.post(
    "/{account_id}",
    tags=["Identifiers"],
    response_model=IdentifierResponseModel,
    status_code=status.HTTP_201_CREATED,
    dependencies=[Depends(require_self_account)],
)
async def add_identifier(
    account_id: UUID,
    body: IdentifierCreateModel,
    uow: AccountUow,
) -> IdentifierResponseModel:
    identifier = await IdentifierService(uow).add(
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
    "/{account_id}/{identifier_id}/verify",
    tags=["Identifiers"],
    response_model=IdentifierResponseModel,
    dependencies=[Depends(require_self_account)],
)
async def verify_identifier(
    account_id: UUID,
    identifier_id: UUID,
    uow: AccountUow,
) -> IdentifierResponseModel:
    identifier = await IdentifierService(uow).verify(account_id, identifier_id)
    return to_identifier_response(identifier)


@router.post(
    "/{account_id}/{identifier_id}/touch",
    tags=["Identifiers"],
    response_model=IdentifierResponseModel,
    dependencies=[Depends(require_self_account)],
)
async def touch_identifier(
    account_id: UUID,
    identifier_id: UUID,
    uow: AccountUow,
) -> IdentifierResponseModel:
    identifier = await IdentifierService(uow).touch(account_id, identifier_id)
    return to_identifier_response(identifier)


@router.patch(
    "/{account_id}/{identifier_id}/preferences",
    tags=["Identifiers"],
    response_model=IdentifierResponseModel,
    dependencies=[Depends(require_self_account)],
)
async def update_identifier_preferences(
    account_id: UUID,
    identifier_id: UUID,
    body: IdentifierPreferencesUpdateModel,
    uow: AccountUow,
) -> IdentifierResponseModel:
    identifier = await IdentifierService(uow).update_preferences(
        account_id,
        identifier_id,
        is_public_contact=body.is_public_contact,
        receive_notifications=body.receive_notifications,
    )
    return to_identifier_response(identifier)


@router.delete(
    "/{account_id}/{identifier_id}",
    tags=["Identifiers"],
    status_code=status.HTTP_204_NO_CONTENT,
    dependencies=[Depends(require_self_account)],
)
async def delete_identifier(account_id: UUID, identifier_id: UUID, uow: AccountUow) -> Response:
    await IdentifierService(uow).delete(account_id, identifier_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
