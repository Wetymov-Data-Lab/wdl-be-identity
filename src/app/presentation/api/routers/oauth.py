from typing import Annotated, Literal

from fastapi import APIRouter, Form, Request, Response, status
from wdl_shared.schemas.identity import OAuthTokenResponseModel, UserInfoResponseModel

from app.application.services.oauth import LoginContext, OAuthService
from app.application.tokens import TokenPair
from app.domain.entities import Account
from app.domain.exceptions import AuthenticationError
from app.presentation.api.routers._dependencies import (
    AccessToken,
    AccountUow,
    CurrentAccount,
    PasswordHasherDep,
    SessionRevocationStoreDep,
    TokenCodecDep,
)

router = APIRouter(prefix="/oauth", tags=["OAuth"])
NO_STORE_HEADERS = {"Cache-Control": "no-store", "Pragma": "no-cache"}


def _token_response(pair: TokenPair) -> OAuthTokenResponseModel:
    return OAuthTokenResponseModel(
        access_token=pair.access_token,
        refresh_token=pair.refresh_token,
        expires_in=pair.access_expires_in,
    )


@router.post(
    "/token",
    response_model=OAuthTokenResponseModel,
    summary="Issue or refresh OAuth bearer tokens",
)
async def token(
    request: Request,
    response: Response,
    uow: AccountUow,
    password_hasher: PasswordHasherDep,
    token_codec: TokenCodecDep,
    revocations: SessionRevocationStoreDep,
    grant_type: Annotated[Literal["password", "refresh_token"], Form()],
    username: Annotated[str | None, Form()] = None,
    password: Annotated[str | None, Form()] = None,
    refresh_token: Annotated[str | None, Form()] = None,
    scope: Annotated[str, Form()] = "",
    client_id: Annotated[str | None, Form()] = None,
    client_secret: Annotated[str | None, Form()] = None,
) -> OAuthTokenResponseModel:
    del scope, client_id, client_secret
    response.headers.update(NO_STORE_HEADERS)
    service = OAuthService(uow, token_codec, revocations)
    if grant_type == "password":
        if not username or not password:
            raise AuthenticationError("Username and password are required")
        pair = await service.login(
            username=username,
            password=password,
            context=LoginContext(
                ip=request.client.host if request.client else "unknown",
                user_agent=request.headers.get("user-agent", "unknown"),
            ),
            password_hasher=password_hasher,
        )
        return _token_response(pair)

    if not refresh_token:
        raise AuthenticationError("Refresh token is required")
    return _token_response(await service.refresh(refresh_token))


@router.post(
    "/revoke",
    status_code=status.HTTP_200_OK,
    summary="Revoke an access or refresh token session",
)
async def revoke(
    token: Annotated[str, Form()],
    uow: AccountUow,
    token_codec: TokenCodecDep,
    revocations: SessionRevocationStoreDep,
    token_type_hint: Annotated[str | None, Form()] = None,
) -> Response:
    del token_type_hint
    await OAuthService(uow, token_codec, revocations).revoke(token)
    return Response(status_code=status.HTTP_200_OK, headers=NO_STORE_HEADERS)


@router.post(
    "/logout",
    status_code=status.HTTP_204_NO_CONTENT,
    summary="End the current bearer-token session",
)
async def logout(
    uow: AccountUow,
    token_codec: TokenCodecDep,
    revocations: SessionRevocationStoreDep,
    access_token: AccessToken,
) -> Response:
    await OAuthService(uow, token_codec, revocations).revoke(access_token)
    return Response(status_code=status.HTTP_204_NO_CONTENT, headers=NO_STORE_HEADERS)


@router.get(
    "/userinfo",
    response_model=UserInfoResponseModel,
    summary="Return claims for the authenticated account",
)
async def userinfo(
    response: Response,
    account: CurrentAccount,
) -> UserInfoResponseModel:
    response.headers.update(NO_STORE_HEADERS)
    return _to_user_info(account)


def _to_user_info(account: Account) -> UserInfoResponseModel:
    email = next(
        (item.value for item in account.identifiers if item.type == "email" and item.provider is None),
        None,
    )
    profile = account.profile
    return UserInfoResponseModel(
        sub=account.id,
        email=email,
        name=None if profile is None else profile.display_name,
        given_name=None if profile is None else profile.given_name,
        family_name=None if profile is None else profile.family_name,
        picture=None if profile is None else profile.picture_url,
        locale=None if profile is None else profile.locale,
    )
