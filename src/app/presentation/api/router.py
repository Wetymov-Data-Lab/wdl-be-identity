from fastapi import APIRouter, Depends
from wdl_shared.schemas.common import HealthResponse

from app.presentation.api.dependencies.authentication import get_current_account
from app.presentation.api.routers import (
    accounts_router,
    identifiers_router,
    oauth_router,
    passwords_router,
    profiles_router,
    recovery_codes_router,
    registrations_router,
    second_factors_router,
    sessions_router,
)

api_router = APIRouter()
authenticated_router = APIRouter(dependencies=[Depends(get_current_account)])

authenticated_router.include_router(identifiers_router)
authenticated_router.include_router(accounts_router)
authenticated_router.include_router(profiles_router)
authenticated_router.include_router(passwords_router)
authenticated_router.include_router(second_factors_router)
authenticated_router.include_router(recovery_codes_router)
authenticated_router.include_router(sessions_router)

api_router.include_router(registrations_router)
api_router.include_router(authenticated_router)
api_router.include_router(oauth_router)


@api_router.get("/health", tags=["System"], response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
