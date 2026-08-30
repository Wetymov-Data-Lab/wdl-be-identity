from app.domain.entities import Account
from app.infrastructure.database.mappers.identifier import IdentifierMapper
from app.infrastructure.database.mappers.password import PasswordMapper
from app.infrastructure.database.mappers.profile import ProfileMapper
from app.infrastructure.database.mappers.recovery_code import RecoveryCodeMapper
from app.infrastructure.database.mappers.second_factor import SecondFactorMapper
from app.infrastructure.database.mappers.session import SessionMapper
from app.infrastructure.database.models import AccountModel


class AccountMapper:
    @staticmethod
    def to_model(account: Account) -> AccountModel:
        return AccountModel(
            id=account.id,
            subject=account.subject,
            status=account.status,
            is_2fa_enforced=account.is_2fa_enforced,
            last_active_at=account.last_active_at,
            updated_at=account.updated_at,
            created_at=account.created_at,
            version=account.version,
            profile=None if account.profile is None else ProfileMapper.to_model(account.profile),
            password=None if account.password is None else PasswordMapper.to_model(account.password),
            sessions=[SessionMapper.to_model(item) for item in account.sessions],
            identifiers=[IdentifierMapper.to_model(item) for item in account.identifiers],
            second_factors=[SecondFactorMapper.to_model(item) for item in account.second_factors],
            recovery_codes=[RecoveryCodeMapper.to_model(item) for item in account.recovery_codes],
        )

    @staticmethod
    def to_domain(model: AccountModel) -> Account:
        account = Account(subject=model.subject, status=model.status)
        account.id = model.id
        account.created_at = model.created_at
        account.updated_at = model.updated_at
        account.last_active_at = model.last_active_at
        account.version = model.version
        account.is_2fa_enforced = model.is_2fa_enforced
        account.profile = None if model.profile is None else ProfileMapper.to_domain(model.profile)
        account.password = None if model.password is None else PasswordMapper.to_domain(model.password)
        account.sessions = [SessionMapper.to_domain(item) for item in model.sessions]
        account.identifiers = [IdentifierMapper.to_domain(item) for item in model.identifiers]
        account.second_factors = [SecondFactorMapper.to_domain(item) for item in model.second_factors]
        account.recovery_codes = [RecoveryCodeMapper.to_domain(item) for item in model.recovery_codes]
        return account
