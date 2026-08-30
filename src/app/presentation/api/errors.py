from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse
from redis.exceptions import RedisError

from app.domain.exceptions import (
    AuthenticationError,
    AuthorizationError,
    DomainError,
    EntityAlreadyExistsError,
    EntityNotFoundError,
)


def setup_exception_handlers(app: FastAPI) -> None:
    @app.exception_handler(RedisError)
    async def redis_unavailable(_: Request, __: RedisError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_503_SERVICE_UNAVAILABLE,
            content={"detail": "Authentication state storage is unavailable"},
        )

    @app.exception_handler(AuthenticationError)
    async def unauthorized(_: Request, error: AuthenticationError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_401_UNAUTHORIZED,
            content={"detail": str(error)},
            headers={"WWW-Authenticate": "Bearer"},
        )

    @app.exception_handler(AuthorizationError)
    async def forbidden(_: Request, error: AuthorizationError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_403_FORBIDDEN, content={"detail": str(error)})

    @app.exception_handler(EntityNotFoundError)
    async def not_found(_: Request, error: EntityNotFoundError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_404_NOT_FOUND, content={"detail": str(error)})

    @app.exception_handler(EntityAlreadyExistsError)
    async def conflict(_: Request, error: EntityAlreadyExistsError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_409_CONFLICT, content={"detail": str(error)})

    @app.exception_handler(DomainError)
    async def domain_error(_: Request, error: DomainError) -> JSONResponse:
        return JSONResponse(status_code=status.HTTP_400_BAD_REQUEST, content={"detail": str(error)})
