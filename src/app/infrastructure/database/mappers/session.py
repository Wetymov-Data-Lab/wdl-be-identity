from app.domain.entities import Session
from app.infrastructure.database.models import SessionModel


class SessionMapper:
    @staticmethod
    def to_model(session: Session) -> SessionModel:
        return SessionModel(
            id=session.id,
            account_id=session.account_id,
            ip=session.ip,
            refresh_token_hash=session.refresh_token_hash,
            user_agent=session.user_agent,
            expires_at=session.expires_at,
            created_at=session.created_at,
            last_refreshed_at=session.last_refreshed_at,
        )

    @staticmethod
    def to_domain(model: SessionModel) -> Session:
        session = Session(
            account_id=model.account_id,
            ip=model.ip,
            refresh_token_hash=model.refresh_token_hash,
            user_agent=model.user_agent,
            expires_at=model.expires_at,
        )
        session.id = model.id
        session.created_at = model.created_at
        session.last_refreshed_at = model.last_refreshed_at
        return session
