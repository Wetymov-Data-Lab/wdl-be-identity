from typing import cast
from unittest.mock import AsyncMock, Mock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession, async_sessionmaker

from wdl_be_identity.infrastructure.database.unit_of_work import SQLAlchemyUnitOfWork


@pytest.mark.asyncio
async def test_successful_unit_of_work_does_not_expire_loaded_entities() -> None:
    session = AsyncMock(spec=AsyncSession)
    factory = Mock(return_value=session)
    unit_of_work = SQLAlchemyUnitOfWork(
        cast(async_sessionmaker[AsyncSession], factory),
    )

    async with unit_of_work:
        pass

    session.rollback.assert_not_awaited()
    session.close.assert_awaited_once()


@pytest.mark.asyncio
async def test_failed_unit_of_work_rolls_back() -> None:
    session = AsyncMock(spec=AsyncSession)
    factory = Mock(return_value=session)
    unit_of_work = SQLAlchemyUnitOfWork(
        cast(async_sessionmaker[AsyncSession], factory),
    )

    with pytest.raises(RuntimeError, match="boom"):
        async with unit_of_work:
            raise RuntimeError("boom")

    session.rollback.assert_awaited_once()
    session.close.assert_awaited_once()
