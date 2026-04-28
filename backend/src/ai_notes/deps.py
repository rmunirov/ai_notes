from __future__ import annotations

from collections.abc import AsyncIterator
from typing import Any

from fastapi import Request
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import AppSettings
from ai_notes.infrastructure.db.session import get_session_maker


async def get_db() -> AsyncIterator[AsyncSession]:
    sm = get_session_maker()
    async with sm() as session:
        try:
            yield session
        finally:
            await session.close()


def get_app_settings(request: Request) -> AppSettings:
    return request.app.state.settings  # type: ignore[no-any-return]


def get_agent_checkpointer(request: Request) -> BaseCheckpointSaver[Any] | None:
    return getattr(request.app.state, "agent_checkpointer", None)


def get_agent(request: Request) -> CompiledStateGraph[Any, Any, Any, Any] | None:
    return getattr(request.app.state, "agent", None)
