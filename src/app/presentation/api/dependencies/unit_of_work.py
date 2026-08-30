from app.application.unit_of_work import UnitOfWork
from app.infrastructure.database.session import async_session_factory
from app.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


def get_account_uow() -> UnitOfWork:
    return SQLAlchemyUnitOfWork(async_session_factory)
