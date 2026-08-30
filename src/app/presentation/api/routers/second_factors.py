from uuid import UUID

from fastapi import APIRouter, Response, status
from wdl_shared.schemas.identity import (
    AccountResponseModel,
    SecondFactorCreateModel,
    SecondFactorResponseModel,
    TwoFactorPolicyUpdateModel,
)

from app.application.services.second_factors import SecondFactorService
from app.presentation.api.presenters import to_account_response, to_second_factor_response
from app.presentation.api.routers._dependencies import AccountUow

router = APIRouter(prefix="/second-factors")


@router.put(
    "/{account_id}/policy",
    tags=["Second Factors"],
    response_model=AccountResponseModel,
)
async def update_2fa_policy(
    account_id: UUID,
    body: TwoFactorPolicyUpdateModel,
    uow: AccountUow,
) -> AccountResponseModel:
    account = await SecondFactorService(uow).set_policy(account_id, enforced=body.enforced)
    return to_account_response(account)


@router.post(
    "/{account_id}",
    tags=["Second Factors"],
    response_model=SecondFactorResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_second_factor(
    account_id: UUID,
    body: SecondFactorCreateModel,
    uow: AccountUow,
) -> SecondFactorResponseModel:
    factor = await SecondFactorService(uow).add(
        account_id,
        type=body.type,
        secret=body.secret,
        name=body.name,
    )
    return to_second_factor_response(factor)


@router.post(
    "/{account_id}/{factor_id}/confirm",
    tags=["Second Factors"],
    response_model=SecondFactorResponseModel,
)
async def confirm_second_factor(
    account_id: UUID,
    factor_id: UUID,
    uow: AccountUow,
) -> SecondFactorResponseModel:
    factor = await SecondFactorService(uow).confirm(account_id, factor_id)
    return to_second_factor_response(factor)


@router.delete(
    "/{account_id}/{factor_id}",
    tags=["Second Factors"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_second_factor(account_id: UUID, factor_id: UUID, uow: AccountUow) -> Response:
    await SecondFactorService(uow).delete(account_id, factor_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
