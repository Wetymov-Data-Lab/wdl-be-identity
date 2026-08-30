from collections.abc import Iterator
from datetime import UTC, datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient

from app.application.repositories import AccountRepository
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import Account
from app.main import create_app
from app.presentation.api.dependencies.passwords import get_password_hasher
from app.presentation.api.dependencies.unit_of_work import get_account_uow


class FakeAccountRepository(AccountRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Account] = {}

    async def list(self, *, limit: int, offset: int) -> list[Account]:
        accounts = sorted(self.items.values(), key=lambda item: (item.created_at, item.id))
        return accounts[offset : offset + limit]

    async def get(self, entity_id: UUID) -> Account | None:
        return self.items.get(entity_id)

    async def get_by_identifier(
        self,
        *,
        type: str,
        value: str,
        provider: str | None = None,
    ) -> Account | None:
        return next(
            (
                account
                for account in self.items.values()
                for identifier in account.identifiers
                if identifier.type == type
                and identifier.value == value
                and identifier.provider == provider
            ),
            None,
        )

    async def add(self, entity: Account) -> None:
        self.items[entity.id] = entity

    async def remove(self, entity: Account) -> None:
        self.items.pop(entity.id, None)


class FakeUnitOfWork(UnitOfWork):
    def __init__(self) -> None:
        self._accounts = FakeAccountRepository()

    @property
    def accounts(self) -> FakeAccountRepository:
        return self._accounts

    async def commit(self) -> None:
        return None

    async def rollback(self) -> None:
        return None


class FakePasswordHasher:
    async def hash(self, password: str) -> str:
        return f"$argon2id$test${password}"

    async def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == await self.hash(password)

    async def needs_rehash(self, password_hash: str) -> bool:
        return False


@pytest.fixture
def api() -> Iterator[TestClient]:
    unit_of_work = FakeUnitOfWork()
    app = create_app()
    app.dependency_overrides[get_account_uow] = lambda: unit_of_work
    app.dependency_overrides[get_password_hasher] = FakePasswordHasher
    client = TestClient(app)
    yield client
    client.close()


def create_account(api: TestClient) -> dict[str, object]:
    response = api.post(
        "/accounts/",
        json={
            "email": "user@example.com",
            "password": "correct horse battery staple",
            "profile": {"display_name": "Test user"},
        },
    )
    assert response.status_code == 201
    return response.json()


def test_create_get_and_activate_account(api: TestClient) -> None:
    created = create_account(api)
    account_id = created["id"]

    fetched = api.get(f"/accounts/{account_id}")
    activated = api.post(f"/accounts/{account_id}/activate")

    assert fetched.status_code == 200
    assert fetched.json()["status"] == "pending"
    assert activated.status_code == 200
    assert activated.json()["status"] == "active"


def test_create_account_with_profile_and_identifier(api: TestClient) -> None:
    response = api.post(
        "/accounts/",
        json={
            "email": "denis@example.com",
            "password": "correct horse battery staple",
            "profile": {
                "display_name": "Denis",
                "given_name": "Denis",
                "family_name": "Vasin",
                "bio": "Designing databases",
                "job_title": "Software Engineer",
                "organization": "WDL",
                "locale": "ru-RU",
                "time_zone": "Europe/Moscow",
                "picture_url": "https://example.test/avatar.png",
                "website_url": "https://example.test",
            },
        },
    )

    assert response.status_code == 201
    body = response.json()
    assert body["profile"]["display_name"] == "Denis"
    assert body["profile"]["organization"] == "WDL"
    assert body["profile"]["created_at"] is not None
    assert body["identifiers"][0]["value"] == "denis@example.com"


def test_profile_and_password_management_do_not_expose_hashes(api: TestClient) -> None:
    account_id = create_account(api)["id"]

    profile = api.put(
        f"/profiles/{account_id}",
        json={
            "display_name": "Denis",
            "locale": "ru-RU",
            "time_zone": "Europe/Moscow",
            "picture_url": None,
        },
    )
    password = api.put(
        f"/passwords/{account_id}",
        json={"password": "another correct horse battery staple"},
    )
    account = api.get(f"/accounts/{account_id}")

    assert profile.status_code == 200
    assert profile.json()["display_name"] == "Denis"
    assert password.status_code == 200
    assert "hash" not in password.json()
    assert "password" not in password.json()
    assert "hash" not in account.json()["password"]


def test_identifier_management_and_lookup(api: TestClient) -> None:
    account_id = create_account(api)["id"]

    created = api.post(
        f"/identifiers/{account_id}",
        json={
            "type": "email",
            "value": "user@example.test",
            "is_public_contact": False,
            "receive_notifications": True,
        },
    )
    identifier_id = created.json()["id"]
    verified = api.post(f"/identifiers/{account_id}/{identifier_id}/verify")
    lookup = api.get(
        "/identifiers/by-identifier",
        params={"type": "email", "value": "user@example.test"},
    )

    assert created.status_code == 201
    assert verified.status_code == 200
    assert verified.json()["is_verified"] is True
    assert lookup.status_code == 200
    assert lookup.json()["id"] == account_id


def test_session_management_does_not_expose_refresh_hash(api: TestClient) -> None:
    account_id = create_account(api)["id"]
    expires_at = datetime.now(UTC) + timedelta(hours=1)

    response = api.post(
        f"/sessions/{account_id}",
        json={
            "ip": "127.0.0.1",
            "refresh_token_hash": "already-hashed-token",
            "user_agent": "pytest",
            "expires_at": expires_at.isoformat(),
        },
    )

    assert response.status_code == 201
    assert "refresh_token_hash" not in response.json()


def test_missing_account_returns_404(api: TestClient) -> None:
    response = api.get("/accounts/00000000-0000-4000-8000-000000000000")

    assert response.status_code == 404


def test_openapi_contains_management_api_but_not_auth_flows(api: TestClient) -> None:
    openapi = api.get("/openapi.json").json()
    paths = openapi["paths"]

    assert "/accounts/" in paths
    assert "/profiles/{account_id}" in paths
    assert "/passwords/{account_id}" in paths
    assert "/identifiers/{account_id}" in paths
    assert "/second-factors/{account_id}" in paths
    assert "/recovery-codes/{account_id}" in paths
    assert "/sessions/{account_id}" in paths
    assert "/accounts/{account_id}/master-code" not in paths
    assert all("login" not in path and "refresh-token" not in path for path in paths)
    assert "password_history" not in openapi["components"]["schemas"]["AccountResponseModel"]["properties"]
    assert paths["/profiles/{account_id}"]["put"]["tags"] == ["Profiles"]
    assert paths["/identifiers/{account_id}"]["post"]["tags"] == ["Identifiers"]
    assert paths["/sessions/{account_id}"]["post"]["tags"] == ["Sessions"]
    assert all(
        not path.startswith(f"/accounts/{{account_id}}/{resource}")
        for path in paths
        for resource in (
            "profile",
            "password",
            "identifiers",
            "second-factors",
            "recovery-codes",
            "sessions",
        )
    )
