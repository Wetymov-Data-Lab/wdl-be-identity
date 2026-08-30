from uuid import UUID

from fastapi import APIRouter, Response, status
from wdl_shared.schemas.identity import PasswordResponseModel, PasswordSetModel

from wdl_be_identity.application.services.passwords import PasswordService
from wdl_be_identity.presentation.api.presenters import to_password_response
from wdl_be_identity.presentation.api.routers._dependencies import AccountUow, PasswordHasherDep

router = APIRouter(prefix="/passwords")


@router.put("/{account_id}", tags=["Passwords"], response_model=PasswordResponseModel)
async def set_password(
    account_id: UUID,
    body: PasswordSetModel,
    uow: AccountUow,
    password_hasher: PasswordHasherDep,
) -> PasswordResponseModel:
    password = await PasswordService(uow).set(
        account_id,
        password=body.password.get_secret_value(),
        password_hasher=password_hasher,
    )
    return to_password_response(password)


@router.delete(
    "/{account_id}",
    tags=["Passwords"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_password(account_id: UUID, uow: AccountUow) -> Response:
    await PasswordService(uow).delete(account_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
