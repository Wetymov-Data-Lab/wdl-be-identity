from collections.abc import AsyncIterator

from fastapi import Request

from app.application.unit_of_work import UnitOfWork
from app.infrastructure.database.session import async_session_factory
from app.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork
from app.presentation.api.dependencies.transactions import request_audit_entry
from common.transaction_manager import TransactionManager


async def get_account_uow(request: Request) -> AsyncIterator[UnitOfWork]:
    manager = TransactionManager(async_session_factory, service_name="wdl-be-identity")
    async with manager.transaction(audit=lambda: request_audit_entry(request)) as session:
        yield SQLAlchemyUnitOfWork(async_session_factory, managed_session=session)
