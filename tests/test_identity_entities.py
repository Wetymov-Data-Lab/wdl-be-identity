from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest

from app.domain.entities import (
    Identifier,
    Password,
    PasswordHistory,
    Profile,
    RecoveryCode,
    SecondFactor,
    Session,
)
from app.domain.exceptions import InvariantViolationError


def new_id() -> UUID:
    return UUID("12345678-1234-4234-9234-123456789abc")


def assert_uuid4(value: UUID) -> None:
    assert value.version == 4


def test_simple_entities_are_created_from_their_table_fields() -> None:
    account_id = new_id()
    set_at = datetime.now(UTC)

    password_history = PasswordHistory(
        account_id=account_id,
        hash="old-hash",
        set_at=set_at,
        version=1,
    )

    assert_uuid4(password_history.id)
    assert password_history.set_at is set_at


def test_second_factor_can_only_be_confirmed_once() -> None:
    factor = SecondFactor(
        account_id=new_id(),
        type="totp",
        secret="encrypted-secret",
        name="Authenticator",
    )

    factor.confirm()

    assert_uuid4(factor.id)
    assert factor.confirmed_at is not None
    with pytest.raises(InvariantViolationError) as error:
        factor.confirm()
    assert error.value.message_key == "entities.second_factor.ALREADY_CONFIRMED"


def test_recovery_code_can_only_be_used_once() -> None:
    code = RecoveryCode(account_id=new_id(), hash="recovery-hash")

    code.use()

    assert code.used_at is not None
    with pytest.raises(InvariantViolationError) as error:
        code.use()
    assert error.value.message_key == "entities.recovery_code.ALREADY_USED"


def test_profile_update_replaces_public_fields() -> None:
    profile = Profile(account_id=new_id(), display_name="Old name")

    profile.update(
        display_name="New name",
        given_name="Denis",
        family_name="Vasin",
        bio="Designing databases",
        job_title="Software Engineer",
        organization="WDL",
        locale="ru-RU",
        time_zone="Europe/Moscow",
        picture_url="https://example.test/avatar.png",
        website_url="https://example.test",
    )

    assert profile.display_name == "New name"
    assert profile.given_name == "Denis"
    assert profile.family_name == "Vasin"
    assert profile.bio == "Designing databases"
    assert profile.job_title == "Software Engineer"
    assert profile.organization == "WDL"
    assert profile.locale == "ru-RU"
    assert profile.time_zone == "Europe/Moscow"
    assert profile.picture_url == "https://example.test/avatar.png"
    assert profile.website_url == "https://example.test"
    assert profile.created_at.tzinfo is UTC
    assert profile.updated_at is not None


def test_password_change_replaces_hash_without_exposing_history() -> None:
    password = Password(account_id=new_id(), hash="old-hash")
    original_set_at = password.set_at

    result = password.change(new_hash="new-hash")

    assert password.hash == "new-hash"
    assert password.version == 2
    assert password.set_at >= original_set_at
    assert result is None


def test_identifier_can_be_verified_and_used() -> None:
    identifier = Identifier(
        account_id=new_id(),
        type="email",
        value="user@example.test",
        receive_notifications=True,
    )

    identifier.verify()
    identifier.touch()

    assert identifier.is_verified is True
    assert identifier.verified_at is not None
    assert identifier.last_used_at is not None
    with pytest.raises(InvariantViolationError) as error:
        identifier.verify()
    assert error.value.message_key == "entities.identifier.ALREADY_VERIFIED"


def test_session_refreshes_while_active() -> None:
    now = datetime.now(UTC)
    session = Session(
        account_id=new_id(),
        ip="127.0.0.1",
        refresh_token_hash="old-token",
        user_agent="pytest",
        expires_at=now + timedelta(hours=1),
    )
    new_expiration = now + timedelta(hours=2)

    session.refresh(refresh_token_hash="new-token", expires_at=new_expiration)

    assert session.refresh_token_hash == "new-token"
    assert session.expires_at == new_expiration
    assert session.last_refreshed_at >= session.created_at


def test_expired_session_cannot_be_refreshed() -> None:
    session = Session(
        account_id=new_id(),
        ip="127.0.0.1",
        refresh_token_hash="old-token",
        user_agent="pytest",
        expires_at=datetime.now(UTC) - timedelta(seconds=1),
    )

    with pytest.raises(InvariantViolationError) as error:
        session.refresh(
            refresh_token_hash="new-token",
            expires_at=datetime.now(UTC) + timedelta(hours=1),
        )

    assert error.value.message_key == "entities.session.EXPIRED"
