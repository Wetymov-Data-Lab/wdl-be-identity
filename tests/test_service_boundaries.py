from wdl_be_identity.application.services import (
    AccountService,
    IdentifierService,
    PasswordService,
    ProfileService,
    RecoveryCodeService,
    RegistrationService,
    SecondFactorService,
    SessionService,
)
from wdl_be_identity.presentation.api.routers import (
    identifiers_router,
    passwords_router,
    profiles_router,
    recovery_codes_router,
    registrations_router,
    second_factors_router,
    sessions_router,
)


def test_each_identity_entity_has_a_dedicated_service_module() -> None:
    services = {
        "accounts": AccountService,
        "identifiers": IdentifierService,
        "passwords": PasswordService,
        "profiles": ProfileService,
        "recovery_codes": RecoveryCodeService,
        "registrations": RegistrationService,
        "second_factors": SecondFactorService,
        "sessions": SessionService,
    }

    for module_name, service in services.items():
        assert service.__module__.endswith(f".services.{module_name}")


def test_entity_endpoints_are_owned_by_dedicated_router_modules() -> None:
    routers = {
        "identifiers": identifiers_router,
        "passwords": passwords_router,
        "profiles": profiles_router,
        "recovery_codes": recovery_codes_router,
        "registrations": registrations_router,
        "second_factors": second_factors_router,
        "sessions": sessions_router,
    }

    for module_name, router in routers.items():
        assert router.routes
        assert all(route.endpoint.__module__.endswith(f".routers.{module_name}") for route in router.routes)
