from app.domain.entities import SecondFactor
from app.infrastructure.database.models import SecondFactorModel


class SecondFactorMapper:
    @staticmethod
    def to_model(factor: SecondFactor) -> SecondFactorModel:
        return SecondFactorModel(
            id=factor.id,
            account_id=factor.account_id,
            type=factor.type,
            secret=factor.secret,
            name=factor.name,
            confirmed_at=factor.confirmed_at,
            created_at=factor.created_at,
        )

    @staticmethod
    def to_domain(model: SecondFactorModel) -> SecondFactor:
        factor = SecondFactor(
            account_id=model.account_id,
            type=model.type,
            secret=model.secret,
            name=model.name,
        )
        factor.id = model.id
        factor.confirmed_at = model.confirmed_at
        factor.created_at = model.created_at
        return factor
