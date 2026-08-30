from typing import Annotated
from uuid import UUID

from fastapi import APIRouter, Query, Response, status
from wdl_shared.schemas.identity import AccountResponseModel

from app.application.services.accounts import AccountService
from app.application.unit_of_work import UnitOfWork
from app.presentation.api.presenters import to_account_response
from app.presentation.api.routers._dependencies import AccountUow

router = APIRouter(prefix="/accounts")


@router.get("/", tags=["Accounts"], response_model=list[AccountResponseModel])
async def list_accounts(
    uow: AccountUow,
    limit: Annotated[int, Query(ge=1, le=100)] = 50,
    offset: Annotated[int, Query(ge=0)] = 0,
) -> list[AccountResponseModel]:
    accounts = await AccountService(uow).list_accounts(limit=limit, offset=offset)
    return [to_account_response(account) for account in accounts]


@router.get("/{account_id}", tags=["Accounts"], response_model=AccountResponseModel)
async def get_account(account_id: UUID, uow: AccountUow) -> AccountResponseModel:
    return to_account_response(await AccountService(uow).get(account_id))


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
