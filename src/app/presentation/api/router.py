from fastapi import APIRouter
from wdl_shared.schemas.common import HealthResponse

from app.presentation.api.routers import (
    accounts_router,
    identifiers_router,
    passwords_router,
    profiles_router,
    recovery_codes_router,
    registrations_router,
    second_factors_router,
    sessions_router,
)

api_router = APIRouter()
api_router.include_router(identifiers_router)
api_router.include_router(registrations_router)
api_router.include_router(accounts_router)
api_router.include_router(profiles_router)
api_router.include_router(passwords_router)
api_router.include_router(second_factors_router)
api_router.include_router(recovery_codes_router)
api_router.include_router(sessions_router)


@api_router.get("/health", tags=["System"], response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
