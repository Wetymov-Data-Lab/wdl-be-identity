from app.domain.entities import Identifier
from app.infrastructure.database.models import IdentifierModel


class IdentifierMapper:
    @staticmethod
    def to_model(identifier: Identifier) -> IdentifierModel:
        return IdentifierModel(
            id=identifier.id,
            account_id=identifier.account_id,
            type=identifier.type,
            value=identifier.value,
            provider=identifier.provider,
            provider_user_id=identifier.provider_user_id,
            is_verified=identifier.is_verified,
            is_public_contact=identifier.is_public_contact,
            receive_notifications=identifier.receive_notifications,
            verified_at=identifier.verified_at,
            last_used_at=identifier.last_used_at,
            created_at=identifier.created_at,
        )

    @staticmethod
    def to_domain(model: IdentifierModel) -> Identifier:
        identifier = Identifier(
            account_id=model.account_id,
            type=model.type,
            value=model.value,
            provider=model.provider,
            provider_user_id=model.provider_user_id,
            is_public_contact=model.is_public_contact,
            receive_notifications=model.receive_notifications,
        )
        identifier.id = model.id
        identifier.is_verified = model.is_verified
        identifier.verified_at = model.verified_at
        identifier.last_used_at = model.last_used_at
        identifier.created_at = model.created_at
        return identifier
