from fastapi import APIRouter
from wdl_shared.schemas.common import HealthResponse

from wdl_be_identity.presentation.api.routers import accounts_router

api_router = APIRouter()
api_router.include_router(accounts_router)


@api_router.get("/health", tags=["System"], response_model=HealthResponse)
async def health() -> HealthResponse:
    return HealthResponse(status="ok")
