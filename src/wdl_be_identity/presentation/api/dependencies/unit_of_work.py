from wdl_be_identity.application.unit_of_work import UnitOfWork
from wdl_be_identity.infrastructure.database.session import async_session_factory
from wdl_be_identity.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


def get_account_uow() -> UnitOfWork:
    return SQLAlchemyUnitOfWork(async_session_factory)
