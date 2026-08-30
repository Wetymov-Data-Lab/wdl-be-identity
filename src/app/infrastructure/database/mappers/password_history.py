from app.domain.entities import PasswordHistory
from app.infrastructure.database.models import PasswordHistoryModel


class PasswordHistoryMapper:
    @staticmethod
    def to_model(password: PasswordHistory) -> PasswordHistoryModel:
        return PasswordHistoryModel(
            id=password.id,
            account_id=password.account_id,
            hash=password.hash,
            set_at=password.set_at,
            version=password.version,
        )

    @staticmethod
    def to_domain(model: PasswordHistoryModel) -> PasswordHistory:
        password = PasswordHistory(
            account_id=model.account_id,
            hash=model.hash,
            set_at=model.set_at,
            version=model.version,
        )
        password.id = model.id
        return password
