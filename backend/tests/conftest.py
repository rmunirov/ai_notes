from __future__ import annotations

import os
from collections.abc import AsyncIterator

import pytest_asyncio
from asgi_lifespan import LifespanManager
from httpx import ASGITransport, AsyncClient
from sqlalchemy import text
from sqlalchemy.ext.asyncio import create_async_engine
from sqlalchemy.pool import NullPool

from ai_notes.infrastructure.db import models  # noqa: F401
from ai_notes.infrastructure.db.base import Base
from ai_notes.infrastructure.db.session import close_engine
from ai_notes.main import create_app

TEST_DB_URL = os.environ.get(
    "TEST_DB_URL", "postgresql+asyncpg://ai_notes:ai_notes@127.0.0.1:5432/ai_notes"
)


async def reset_schema(url: str) -> None:
    await close_engine()
    e = create_async_engine(url, poolclass=NullPool)
    async with e.begin() as conn:
        await conn.execute(text("CREATE EXTENSION IF NOT EXISTS vector"))
        await conn.run_sync(Base.metadata.drop_all)
        await conn.run_sync(Base.metadata.create_all)
    await e.dispose()


@pytest_asyncio.fixture
async def client() -> AsyncIterator[AsyncClient]:
    os.environ["DB_URL"] = TEST_DB_URL
    await reset_schema(TEST_DB_URL)
    app = create_app()
    async with LifespanManager(app):
        async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as ac:
            yield ac
    await close_engine()
