from .accounts import router as accounts_router
from .identifiers import router as identifiers_router
from .passwords import router as passwords_router
from .profiles import router as profiles_router
from .recovery_codes import router as recovery_codes_router
from .registrations import router as registrations_router
from .second_factors import router as second_factors_router
from .sessions import router as sessions_router

__all__ = [
    "accounts_router",
    "identifiers_router",
    "passwords_router",
    "profiles_router",
    "recovery_codes_router",
    "registrations_router",
    "second_factors_router",
    "sessions_router",
]
