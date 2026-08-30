from uuid import UUID

from fastapi import APIRouter, Response, status
from wdl_shared.schemas.identity import SessionCreateModel, SessionRefreshModel, SessionResponseModel

from app.application.services.sessions import SessionService
from app.presentation.api.presenters import to_session_response
from app.presentation.api.routers._dependencies import AccountUow

router = APIRouter(prefix="/sessions")


@router.post(
    "/{account_id}",
    tags=["Sessions"],
    response_model=SessionResponseModel,
    status_code=status.HTTP_201_CREATED,
)
async def add_session(
    account_id: UUID,
    body: SessionCreateModel,
    uow: AccountUow,
) -> SessionResponseModel:
    session = await SessionService(uow).add(
        account_id,
        ip=body.ip,
        refresh_token_hash=body.refresh_token_hash,
        user_agent=body.user_agent,
        expires_at=body.expires_at,
    )
    return to_session_response(session)


@router.post(
    "/{account_id}/{session_id}/refresh",
    tags=["Sessions"],
    response_model=SessionResponseModel,
)
async def refresh_session(
    account_id: UUID,
    session_id: UUID,
    body: SessionRefreshModel,
    uow: AccountUow,
) -> SessionResponseModel:
    session = await SessionService(uow).refresh(
        account_id,
        session_id,
        refresh_token_hash=body.refresh_token_hash,
        expires_at=body.expires_at,
    )
    return to_session_response(session)


@router.delete(
    "/{account_id}/{session_id}",
    tags=["Sessions"],
    status_code=status.HTTP_204_NO_CONTENT,
)
async def delete_session(account_id: UUID, session_id: UUID, uow: AccountUow) -> Response:
    await SessionService(uow).delete(account_id, session_id)
    return Response(status_code=status.HTTP_204_NO_CONTENT)
