from __future__ import annotations

import logging
import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import AppSettings
from ai_notes.deps import get_agent, get_app_settings, get_db
from ai_notes.domain.agent import AgentQueryRequest, AgentQueryResponse, ThreadMessagesResponse
from ai_notes.services.agent_service import AgentService
from ai_notes.services.search_service import SearchUnavailableError

_log = logging.getLogger(__name__)

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/query", response_model=AgentQueryResponse)
async def agent_query(
    body: AgentQueryRequest,
    session: AsyncSession = Depends(get_db),
    settings: AppSettings = Depends(get_app_settings),
    agent: CompiledStateGraph[Any, Any, Any, Any] | None = Depends(get_agent),
) -> AgentQueryResponse:
    try:
        return await AgentService(settings, agent=agent).query(session, body)
    except SearchUnavailableError as e:
        _log.warning("agent /query unavailable: %s", e)
        raise HTTPException(
            status_code=503,
            detail={
                "type": "https://ai-notes.local/problems/llm-unavailable",
                "title": "Агент временно недоступен",
                "detail": str(e),
                "status": 503,
            },
        ) from e
    except ValueError as e:
        _log.warning("agent /query not found / bad thread: %s", e)
        raise HTTPException(
            status_code=404,
            detail={
                "type": "https://ai-notes.local/problems/thread-not-found",
                "title": "Диалог не найден",
                "detail": str(e),
                "status": 404,
            },
        ) from e


@router.get("/threads/{thread_id}/messages", response_model=ThreadMessagesResponse)
async def list_thread(
    thread_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    settings: AppSettings = Depends(get_app_settings),
) -> ThreadMessagesResponse:
    r = await AgentService(settings).list_messages(session, thread_id)
    if r is None:
        _log.warning("agent thread messages: thread_id=%s not found", thread_id)
        raise HTTPException(
            status_code=404,
            detail={
                "type": "https://ai-notes.local/problems/thread-not-found",
                "title": "Диалог не найден",
                "detail": "Указанный thread_id не существует.",
                "status": 404,
            },
        )
    return r
