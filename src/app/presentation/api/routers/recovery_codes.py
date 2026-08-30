from uuid import UUID

from fastapi import APIRouter, Response, status
from wdl_shared.schemas.identity import RecoveryCodeCreateModel, RecoveryCodeResponseModel

from app.application.services.recovery_codes import RecoveryCodeService
from app.presentation.api.presenters import to_recovery_code_response
from app.presentation.api.routers._dependencies import AccountUow

router = APIRouter(prefix="/recovery-codes")


@router.post(
    "/{account_id}",
    tags=["Recovery Codes"],
    response_model=RecoveryCodeResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_recovery_code(
    account_id: UUID,
    body: RecoveryCodeCreateModel,
    uow: AccountUow,
) -> RecoveryCodeResponseModel:
    code = await RecoveryCodeService(uow).add(account_id, hash=body.hash)
    return to_recovery_code_response(code)


@router.post(
    "/{account_id}/{code_id}/use",
    tags=["Recovery Codes"],
    response_model=RecoveryCodeResponseModel,
)
async def use_recovery_code(
    account_id: UUID,
    code_id: UUID,
    uow: AccountUow,
) -> RecoveryCodeResponseModel:
    code = await RecoveryCodeService(uow).use(account_id, code_id)
    return to_recovery_code_response(code)


@router.delete(
    "/{account_id}/{code_id}",
    tags=["Recovery Codes"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_recovery_code(account_id: UUID, code_id: UUID, uow: AccountUow) -> Response:
    await RecoveryCodeService(uow).delete(account_id, code_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
