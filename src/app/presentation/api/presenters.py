from wdl_shared.schemas.identity import (
    AccountResponseModel,
    AccountStatus,
    AccountSubject,
    IdentifierResponseModel,
    PasswordResponseModel,
    ProfileResponseModel,
    RecoveryCodeResponseModel,
    SecondFactorResponseModel,
    SessionResponseModel,
)

from app.domain.entities import (
    Account,
    Identifier,
    Password,
    Profile,
    RecoveryCode,
    SecondFactor,
    Session,
)


def to_profile_response(profile: Profile) -> ProfileResponseModel:
    return ProfileResponseModel(
        id=profile.id,
        account_id=profile.account_id,
        display_name=profile.display_name,
        given_name=profile.given_name,
        family_name=profile.family_name,
        bio=profile.bio,
        job_title=profile.job_title,
        organization=profile.organization,
        locale=profile.locale,
        time_zone=profile.time_zone,
        picture_url=profile.picture_url,
        website_url=profile.website_url,
        created_at=profile.created_at,
        updated_at=profile.updated_at,
    )


def to_password_response(password: Password) -> PasswordResponseModel:
    return PasswordResponseModel(
        id=password.id,
        account_id=password.account_id,
        set_at=password.set_at,
        version=password.version,
    )


def to_identifier_response(identifier: Identifier) -> IdentifierResponseModel:
    return IdentifierResponseModel(
        id=identifier.id,
        account_id=identifier.account_id,
        type=identifier.type,
        value=identifier.value,
        provider=identifier.provider,
        provider_user_id=identifier.provider_user_id,
        is_verified=identifier.is_verified,
        is_public_contact=identifier.is_public_contact,
        receive_notifications=identifier.receive_notifications,
        verified_at=identifier.verified_at,
        last_used_at=identifier.last_used_at,
        created_at=identifier.created_at,
    )


def to_second_factor_response(factor: SecondFactor) -> SecondFactorResponseModel:
    return SecondFactorResponseModel(
        id=factor.id,
        account_id=factor.account_id,
        type=factor.type,
        name=factor.name,
        confirmed_at=factor.confirmed_at,
        created_at=factor.created_at,
    )


def to_recovery_code_response(code: RecoveryCode) -> RecoveryCodeResponseModel:
    return RecoveryCodeResponseModel(
        id=code.id,
        account_id=code.account_id,
        used_at=code.used_at,
        created_at=code.created_at,
    )


def to_session_response(session: Session) -> SessionResponseModel:
    return SessionResponseModel(
        id=session.id,
        account_id=session.account_id,
        ip=session.ip,
        user_agent=session.user_agent,
        expires_at=session.expires_at,
        created_at=session.created_at,
        last_refreshed_at=session.last_refreshed_at,
    )


def to_account_response(account: Account) -> AccountResponseModel:
    return AccountResponseModel(
        id=account.id,
        subject=AccountSubject(account.subject.value),
        status=AccountStatus(account.status.value),
        is_2fa_enforced=account.is_2fa_enforced,
        created_at=account.created_at,
        updated_at=account.updated_at,
        last_active_at=account.last_active_at,
        version=account.version,
        profile=None if account.profile is None else to_profile_response(account.profile),
        password=None if account.password is None else to_password_response(account.password),
        identifiers=[to_identifier_response(item) for item in account.identifiers],
        second_factors=[to_second_factor_response(item) for item in account.second_factors],
        recovery_codes=[to_recovery_code_response(item) for item in account.recovery_codes],
        sessions=[to_session_response(item) for item in account.sessions],
    )
