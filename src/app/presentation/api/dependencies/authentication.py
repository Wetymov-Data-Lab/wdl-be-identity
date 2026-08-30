from typing import Annotated

from fastapi import Depends
from fastapi.security import OAuth2PasswordBearer

from app.application.revocations import SessionRevocationStore
from app.application.services.oauth import OAuthService
from app.application.tokens import TokenCodec
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import Account
from app.domain.exceptions import AuthenticationError
from app.presentation.api.dependencies.revocations import get_session_revocation_store
from app.presentation.api.dependencies.tokens import get_token_codec
from app.presentation.api.dependencies.unit_of_work import get_account_uow

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/oauth/token", auto_error=False)


async def get_access_token(
    bearer_token: Annotated[str | None, Depends(oauth2_scheme)],
) -> str:
    """Extract a required Bearer token while preserving the OAuth2 OpenAPI scheme."""
    if not bearer_token:
        raise AuthenticationError("Bearer token is required")
    return bearer_token


async def get_current_account(
    access_token: Annotated[str, Depends(get_access_token)],
    uow: Annotated[UnitOfWork, Depends(get_account_uow)],
    token_codec: Annotated[TokenCodec, Depends(get_token_codec)],
    revocations: Annotated[SessionRevocationStore, Depends(get_session_revocation_store)],
) -> Account:
    """Authenticate the request and provide its active account to an endpoint."""
    return await OAuthService(uow, token_codec, revocations).authenticate_access_token(access_token)
