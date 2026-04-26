from __future__ import annotations

from collections.abc import AsyncIterator

from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

_engine: AsyncEngine | None = None
_session_maker: async_sessionmaker[AsyncSession] | None = None


def create_engine_from_url(url: str) -> AsyncEngine:
    return create_async_engine(url, echo=False, future=True, pool_pre_ping=True)


def init_engine(url: str) -> None:
    global _engine, _session_maker
    if _engine is not None:
        return
    _engine = create_engine_from_url(url)
    _session_maker = async_sessionmaker(_engine, expire_on_commit=False, autoflush=False)


def get_engine() -> AsyncEngine:
    if _engine is None:
        raise RuntimeError("Database engine not initialized")
    return _engine


def get_session_maker() -> async_sessionmaker[AsyncSession]:
    if _session_maker is None:
        raise RuntimeError("Session maker not initialized")
    return _session_maker


async def get_session() -> AsyncIterator[AsyncSession]:
    sm = get_session_maker()
    async with sm() as session:
        try:
            yield session
        finally:
            await session.close()


async def close_engine() -> None:
    global _engine, _session_maker
    if _engine is not None:
        await _engine.dispose()
    _engine = None
    _session_maker = None
