from sqlalchemy import Table, create_mock_engine, inspect

from wdl_be_identity.domain.entities import Account, Profile
from wdl_be_identity.domain.enums import AccountStatus, AccountSubject
from wdl_be_identity.infrastructure.database.base import Base
from wdl_be_identity.infrastructure.database.models import accounts

EXPECTED_TABLES = {
    "accounts",
    "identifiers",
    "master_codes",
    "password_history",
    "passwords",
    "profiles",
    "recovery_codes",
    "second_factors",
    "sessions",
}


def test_identity_metadata_contains_all_tables() -> None:
    assert set(Base.metadata.tables) == EXPECTED_TABLES
    assert isinstance(accounts, Table)


def test_account_is_mapped_as_an_aggregate() -> None:
    mapper = inspect(Account)

    assert mapper.local_table is accounts
    assert mapper.version_id_col is accounts.c.version
    assert set(mapper.relationships.keys()) == {
        "profile",
        "password",
        "master_code",
        "sessions",
        "identifiers",
        "second_factors",
        "recovery_codes",
        "password_history",
    }


def test_domain_defaults_survive_sqlalchemy_instrumentation() -> None:
    account = Account(subject=AccountSubject.USER, status=AccountStatus.PENDING)

    assert account.id.version == 4
    assert account.version == 1
    assert account.is_2fa_enforced is False
    assert account.updated_at is None
    assert account.sessions == []


def test_relationships_accept_domain_entities() -> None:
    account = Account(subject=AccountSubject.USER, status=AccountStatus.PENDING)
    profile = Profile(account_id=account.id, display_name="Test user")

    account.profile = profile

    assert account.profile is profile
    assert profile.account_id == account.id


def test_metadata_compiles_for_postgresql() -> None:
    statements: list[str] = []

    def capture(sql: object, *_: object, **__: object) -> None:
        statements.append(str(sql.compile(dialect=engine.dialect)))  # type: ignore[attr-defined]

    engine = create_mock_engine("postgresql://", capture)
    Base.metadata.create_all(engine)

    ddl = "\n".join(statements)
    assert "CREATE TABLE accounts" in ddl
    assert "UUID NOT NULL" in ddl
