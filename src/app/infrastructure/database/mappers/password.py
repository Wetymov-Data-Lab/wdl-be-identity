from app.domain.entities import Password
from app.infrastructure.database.models import PasswordModel


class PasswordMapper:
    @staticmethod
    def to_model(password: Password) -> PasswordModel:
        return PasswordModel(
            id=password.id,
            account_id=password.account_id,
            hash=password.hash,
            set_at=password.set_at,
            version=password.version,
        )

    @staticmethod
    def to_domain(model: PasswordModel) -> Password:
        password = Password(account_id=model.account_id, hash=model.hash)
        password.id = model.id
        password.set_at = model.set_at
        password.version = model.version
        return password
