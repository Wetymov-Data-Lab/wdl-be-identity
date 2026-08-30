from datetime import UTC
from uuid import UUID

import pytest

from app.domain.entities.account import Account
from app.domain.entities.identifier import Identifier
from app.domain.entities.password import Password
from app.domain.entities.profile import Profile
from app.domain.enums import AccountStatus, AccountSubject
from app.domain.exceptions import InvariantViolationError


def make_account(*, status: AccountStatus = AccountStatus.PENDING) -> Account:
    return Account(subject=AccountSubject.USER, status=status)


def test_account_is_created_with_domain_defaults() -> None:
    account = make_account()

    assert isinstance(account.id, UUID)
    assert account.id.version == 4
    assert account.created_at.tzinfo is UTC
    assert account.updated_at is None
    assert account.last_active_at is None
    assert account.version == 1
    assert account.is_2fa_enforced is False


def test_account_collections_are_not_shared() -> None:
    first = make_account()
    second = make_account()

    first.identifiers.append(
        Identifier(account_id=first.id, type="email", value="first@example.test")
    )

    assert len(first.identifiers) == 1
    assert second.identifiers == []


def test_touch_updates_last_activity_time() -> None:
    account = make_account()

    account.touch()

    assert account.last_active_at is not None
    assert account.last_active_at.tzinfo is UTC


def test_assign_relations() -> None:
    account = make_account()
    password = Password(account_id=account.id, hash="password-hash")
    profile = Profile(account_id=account.id, display_name="Test user")

    account.assign_relations(password=password, profile=profile)

    assert account.password is password
    assert account.profile is profile


@pytest.mark.parametrize(
    ("initial_status", "operation", "result_status"),
    [
        (AccountStatus.PENDING, "activate", AccountStatus.ACTIVE),
        (AccountStatus.ACTIVE, "deactivate", AccountStatus.DEACTIVATED),
        (AccountStatus.DEACTIVATED, "restore", AccountStatus.ACTIVE),
        (AccountStatus.PENDING, "suspend", AccountStatus.SUSPENDED),
        (AccountStatus.SUSPENDED, "unsuspend", AccountStatus.ACTIVE),
    ],
)
def test_allowed_status_transitions(
    initial_status: AccountStatus,
    operation: str,
    result_status: AccountStatus,
) -> None:
    account = make_account(status=initial_status)

    getattr(account, operation)()

    assert account.status is result_status
    assert account.updated_at is not None
    assert account.updated_at.tzinfo is UTC


@pytest.mark.parametrize(
    ("initial_status", "operation", "message_key"),
    [
        (AccountStatus.ACTIVE, "activate", "entities.account.ALREADY_ACTIVATED"),
        (
            AccountStatus.DEACTIVATED,
            "deactivate",
            "entities.account.DEACTIVATION_NOT_ALLOWED",
        ),
        (AccountStatus.PENDING, "restore", "entities.account.RESTORE_NOT_ALLOWED"),
        (AccountStatus.SUSPENDED, "suspend", "entities.account.ALREADY_SUSPENDED"),
        (AccountStatus.ACTIVE, "unsuspend", "entities.account.NOT_SUSPENDED"),
    ],
)
def test_disallowed_status_transitions(
    initial_status: AccountStatus,
    operation: str,
    message_key: str,
) -> None:
    account = make_account(status=initial_status)

    with pytest.raises(InvariantViolationError) as error:
        getattr(account, operation)()

    assert error.value.message_key == message_key
    assert account.status is initial_status
    assert account.updated_at is None
