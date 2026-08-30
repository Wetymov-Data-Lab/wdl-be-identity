from sqlalchemy import create_engine, select
from sqlalchemy.orm import Session as OrmSession

from app.domain.entities import Account, Identifier, Password, Profile
from app.domain.enums import AccountStatus, AccountSubject
from app.infrastructure.database.base import Base
from app.infrastructure.database.mappers import (
    AccountMapper,
    IdentifierMapper,
    PasswordHistoryMapper,
    PasswordMapper,
    ProfileMapper,
    RecoveryCodeMapper,
    SecondFactorMapper,
    SessionMapper,
)
from app.infrastructure.database.models import AccountModel


def make_account() -> Account:
    account = Account(subject=AccountSubject.USER, status=AccountStatus.PENDING)
    account.profile = Profile(account_id=account.id, display_name="Test user")
    account.password = Password(account_id=account.id, hash="password-hash")
    account.identifiers.append(Identifier(account_id=account.id, type="email", value="user@example.test"))
    return account


def test_each_mapper_class_exposes_only_two_conversion_methods() -> None:
    mapper_classes = {
        "account": AccountMapper,
        "identifier": IdentifierMapper,
        "password_history": PasswordHistoryMapper,
        "password": PasswordMapper,
        "profile": ProfileMapper,
        "recovery_code": RecoveryCodeMapper,
        "second_factor": SecondFactorMapper,
        "session": SessionMapper,
    }

    for module_name, mapper in mapper_classes.items():
        public_methods = {name for name in vars(mapper) if not name.startswith("_")}
        assert public_methods == {"to_model", "to_domain"}
        assert mapper.__module__.endswith(f".mappers.{module_name}")


def test_account_round_trips_between_domain_and_declarative_models() -> None:
    account = make_account()

    restored = AccountMapper.to_domain(AccountMapper.to_model(account))

    assert restored == account
    assert restored.profile is not None
    assert restored.profile.display_name == "Test user"
    assert restored.password is not None
    assert restored.password.hash == "password-hash"
    assert restored.identifiers[0].value == "user@example.test"


def test_account_mapper_captures_domain_changes() -> None:
    account = make_account()

    account.activate()
    assert account.profile is not None
    account.profile.update(
        display_name="Updated user",
        given_name=None,
        family_name=None,
        bio=None,
        job_title=None,
        organization=None,
        locale=None,
        time_zone=None,
        picture_url=None,
        website_url=None,
    )
    account.identifiers.clear()
    model = AccountMapper.to_model(account)

    assert model.status is AccountStatus.ACTIVE
    assert model.profile is not None
    assert model.profile.display_name == "Updated user"
    assert model.identifiers == []


def test_declarative_model_persists_and_restores_domain_aggregate() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    account = make_account()
    model = AccountMapper.to_model(account)

    with OrmSession(engine) as session:
        session.add(model)
        session.commit()

    with OrmSession(engine) as session:
        stored = session.scalar(select(AccountModel).where(AccountModel.id == account.id))

        assert stored is not None
        restored = AccountMapper.to_domain(stored)
        assert restored == account
        assert restored.profile is not None
        assert restored.profile.display_name == "Test user"
        assert restored.identifiers[0].value == "user@example.test"


def test_merge_synchronizes_updated_domain_aggregate() -> None:
    engine = create_engine("sqlite://")
    Base.metadata.create_all(engine)
    account = make_account()

    with OrmSession(engine) as session:
        session.add(AccountMapper.to_model(account))
        session.commit()

    account.activate()
    account.identifiers.clear()
    with OrmSession(engine) as session:
        session.merge(AccountMapper.to_model(account))
        session.commit()

    with OrmSession(engine) as session:
        stored = session.scalar(select(AccountModel).where(AccountModel.id == account.id))

        assert stored is not None
        assert stored.status is AccountStatus.ACTIVE
        assert stored.identifiers == []
