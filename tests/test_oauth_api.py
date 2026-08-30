from collections.abc import Iterator
from datetime import datetime, timedelta
from uuid import UUID

import pytest
from fastapi.testclient import TestClient
from httpx import Response

from app.application.repositories import AccountRepository
from app.application.revocations import SessionRevocationStore
from app.application.unit_of_work import UnitOfWork
from app.domain.entities import Account
from app.infrastructure.tokens import JWTTokenCodec
from app.main import create_app
from app.presentation.api.dependencies.passwords import get_password_hasher
from app.presentation.api.dependencies.revocations import get_session_revocation_store
from app.presentation.api.dependencies.tokens import get_token_codec
from app.presentation.api.dependencies.unit_of_work import get_account_uow


class FakeAccountRepository(AccountRepository):
    def __init__(self) -> None:
        self.items: dict[UUID, Account] = {}

    async def list(self, *, limit: int, offset: int) -> list[Account]:
        return list(self.items.values())[offset : offset + limit]

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
                if identifier.type == type and identifier.value == value and identifier.provider == provider
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
        return f"test:{password}"

    async def verify(self, password: str, password_hash: str) -> bool:
        return password_hash == await self.hash(password)

    async def needs_rehash(self, password_hash: str) -> bool:
        return False


class FakeSessionRevocationStore(SessionRevocationStore):
    def __init__(self) -> None:
        self.revoked: set[UUID] = set()

    async def is_revoked(self, session_id: UUID) -> bool:
        return session_id in self.revoked

    async def revoke(self, session_id: UUID, *, expires_at: datetime) -> None:
        del expires_at
        self.revoked.add(session_id)


@pytest.fixture
def api() -> Iterator[TestClient]:
    unit_of_work = FakeUnitOfWork()
    token_codec = JWTTokenCodec(
        secret_key="test-secret-key-that-is-long-enough",
        issuer="test-identity",
        audience="test-api",
        access_token_ttl=timedelta(minutes=5),
        refresh_token_ttl=timedelta(days=1),
    )
    app = create_app()
    app.dependency_overrides[get_account_uow] = lambda: unit_of_work
    app.dependency_overrides[get_password_hasher] = FakePasswordHasher
    app.dependency_overrides[get_token_codec] = lambda: token_codec
    app.dependency_overrides[get_session_revocation_store] = FakeSessionRevocationStore
    client = TestClient(app)
    yield client
    client.close()


def _register_and_activate(api: TestClient) -> str:
    registered = api.post(
        "/accounts/",
        json={
            "email": "user@example.com",
            "password": "correct horse battery staple",
            "profile": {"display_name": "Test User", "given_name": "Test"},
        },
    )
    account_id = registered.json()["id"]
    assert api.post(f"/accounts/{account_id}/activate").status_code == 200
    return account_id


def _login(api: TestClient, *, password: str = "correct horse battery staple") -> Response:
    return api.post(
        "/oauth/token",
        data={
            "grant_type": "password",
            "username": "USER@example.com",
            "password": password,
        },
    )


def test_password_login_requires_active_account_and_valid_credentials(api: TestClient) -> None:
    registered = api.post(
        "/accounts/",
        json={
            "email": "user@example.com",
            "password": "correct horse battery staple",
            "profile": {"display_name": "Test User"},
        },
    )

    assert _login(api).status_code == 403
    api.post(f"/accounts/{registered.json()['id']}/activate")
    response = _login(api, password="wrong password")

    assert response.status_code == 401
    assert response.headers["www-authenticate"] == "Bearer"


def test_login_userinfo_refresh_rotation_and_logout(api: TestClient) -> None:
    account_id = _register_and_activate(api)
    login = _login(api)

    assert login.status_code == 200
    initial_tokens = login.json()
    assert initial_tokens["token_type"] == "bearer"
    assert initial_tokens["expires_in"] == 300
    assert login.headers["cache-control"] == "no-store"
    assert login.headers["pragma"] == "no-cache"

    assert api.get("/oauth/userinfo").status_code == 401
    assert (
        api.get(
            "/oauth/userinfo",
            headers={"Authorization": f"Bearer {initial_tokens['refresh_token']}"},
        ).status_code
        == 401
    )

    userinfo = api.get(
        "/oauth/userinfo",
        headers={"Authorization": f"Bearer {initial_tokens['access_token']}"},
    )
    assert userinfo.status_code == 200
    assert userinfo.json() == {
        "sub": account_id,
        "email": "user@example.com",
        "name": "Test User",
        "given_name": "Test",
        "family_name": None,
        "picture": None,
        "locale": None,
    }

    refreshed = api.post(
        "/oauth/token",
        data={"grant_type": "refresh_token", "refresh_token": initial_tokens["refresh_token"]},
    )
    assert refreshed.status_code == 200
    rotated_tokens = refreshed.json()
    assert rotated_tokens["refresh_token"] != initial_tokens["refresh_token"]

    replay = api.post(
        "/oauth/token",
        data={"grant_type": "refresh_token", "refresh_token": initial_tokens["refresh_token"]},
    )
    assert replay.status_code == 401
    assert (
        api.get(
            "/oauth/userinfo",
            headers={"Authorization": f"Bearer {rotated_tokens['access_token']}"},
        ).status_code
        == 401
    )

    new_login = _login(api).json()

    logout = api.post(
        "/oauth/logout",
        headers={"Authorization": f"Bearer {new_login['access_token']}"},
    )
    assert logout.status_code == 204
    assert (
        api.get(
            "/oauth/userinfo",
            headers={"Authorization": f"Bearer {new_login['access_token']}"},
        ).status_code
        == 401
    )


def test_revoke_is_idempotent_for_invalid_tokens(api: TestClient) -> None:
    response = api.post("/oauth/revoke", data={"token": "not-a-token"})

    assert response.status_code == 200
    assert response.content == b""


def test_account_list_and_profiles_require_authentication(api: TestClient) -> None:
    account_id = _register_and_activate(api)
    assert api.get("/accounts/").status_code == 401
    assert api.get(f"/profiles/{account_id}").status_code == 401
    assert api.put(f"/profiles/{account_id}", json={"display_name": "Test"}).status_code == 401
    assert api.delete(f"/profiles/{account_id}").status_code == 401

    login = _login(api)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}
    assert api.get("/accounts/", headers=headers).status_code == 200
    profile = api.get(f"/profiles/{account_id}", headers=headers)
    assert profile.status_code == 200
    assert profile.json()["account_id"] == account_id


def test_profile_and_password_management_do_not_expose_hashes(api: TestClient) -> None:
    account_id = _register_and_activate(api)
    login = _login(api)
    assert login.status_code == 200
    headers = {"Authorization": f"Bearer {login.json()['access_token']}"}

    profile = api.put(
        f"/profiles/{account_id}",
        headers=headers,
        json={
            "display_name": "Denis",
            "locale": "ru-RU",
            "time_zone": "Europe/Moscow",
            "picture_url": None,
        },
    )
    password = api.put(
        f"/passwords/{account_id}",
        headers=headers,
        json={"password": "another correct horse battery staple"},
    )
    account = api.get(f"/accounts/{account_id}", headers=headers)

    assert profile.status_code == 200
    assert profile.json()["display_name"] == "Denis"
    assert password.status_code == 200
    assert "hash" not in password.json()
    assert "password" not in password.json()
    assert "hash" not in account.json()["password"]
