from app.domain.entities import RecoveryCode
from app.infrastructure.database.models import RecoveryCodeModel


class RecoveryCodeMapper:
    @staticmethod
    def to_model(code: RecoveryCode) -> RecoveryCodeModel:
        return RecoveryCodeModel(
            id=code.id,
            account_id=code.account_id,
            hash=code.hash,
            used_at=code.used_at,
            created_at=code.created_at,
        )

    @staticmethod
    def to_domain(model: RecoveryCodeModel) -> RecoveryCode:
        code = RecoveryCode(account_id=model.account_id, hash=model.hash)
        code.id = model.id
        code.used_at = model.used_at
        code.created_at = model.created_at
        return code
