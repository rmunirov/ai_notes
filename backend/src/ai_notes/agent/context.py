from __future__ import annotations

from dataclasses import dataclass

from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import AppSettings


@dataclass
class AgentContext:
    """Per-request runtime context injected into the LangChain v1 agent.

    Passed via `agent.ainvoke({...}, context=AgentContext(session=..., settings=...))`
    so the search tool can access the current SQLAlchemy session and settings without
    rebuilding the agent for every request.
    """

    session: AsyncSession
    settings: AppSettings
