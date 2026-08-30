from sqlalchemy import Table, create_mock_engine, inspect

from app.domain.entities import Account, Profile
from app.domain.enums import AccountStatus, AccountSubject
from app.infrastructure.database.base import Base
from app.infrastructure.database.models import (
    AccountModel,
    IdentifierModel,
    PasswordHistoryModel,
    PasswordModel,
    ProfileModel,
    RecoveryCodeModel,
    SecondFactorModel,
    SessionModel,
    accounts,
)
from app.infrastructure.database.repositories import SQLAlchemyAccountRepository

EXPECTED_TABLES = {
    "accounts",
    "identifiers",
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
    assert accounts is AccountModel.__table__
    assert Base.metadata.tables["profiles"] is ProfileModel.__table__
    assert {
        "given_name",
        "family_name",
        "bio",
        "job_title",
        "organization",
        "website_url",
        "created_at",
    }.issubset(Base.metadata.tables["profiles"].c.keys())


def test_orm_models_are_split_by_entity_and_repository_by_aggregate() -> None:
    models = {
        "account": AccountModel,
        "identifier": IdentifierModel,
        "password_history": PasswordHistoryModel,
        "password": PasswordModel,
        "profile": ProfileModel,
        "recovery_code": RecoveryCodeModel,
        "second_factor": SecondFactorModel,
        "session": SessionModel,
    }

    for module_name, model in models.items():
        assert model.__module__.endswith(f".models.{module_name}")
    assert SQLAlchemyAccountRepository.__module__.endswith(".repositories.accounts")


def test_account_is_mapped_as_an_aggregate() -> None:
    mapper = inspect(AccountModel)

    assert mapper.local_table is accounts
    assert mapper.version_id_col is accounts.c.version
    assert set(mapper.relationships.keys()) == {
        "profile",
        "password",
        "sessions",
        "identifiers",
        "second_factors",
        "recovery_codes",
    }
    assert inspect(Account, raiseerr=False) is None


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
