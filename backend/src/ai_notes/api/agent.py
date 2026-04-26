from __future__ import annotations

import uuid
from typing import Any

from fastapi import APIRouter, Depends, HTTPException
from langgraph.checkpoint.base import BaseCheckpointSaver
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import AppSettings
from ai_notes.deps import get_agent_checkpointer, get_app_settings, get_db
from ai_notes.domain.agent import AgentQueryRequest, AgentQueryResponse, ThreadMessagesResponse
from ai_notes.services.agent_service import AgentService
from ai_notes.services.search_service import SearchUnavailableError

router = APIRouter(prefix="/agent", tags=["agent"])


@router.post("/query", response_model=AgentQueryResponse)
async def agent_query(
    body: AgentQueryRequest,
    session: AsyncSession = Depends(get_db),
    settings: AppSettings = Depends(get_app_settings),
    checkpointer: BaseCheckpointSaver[Any] | None = Depends(get_agent_checkpointer),
) -> AgentQueryResponse:
    try:
        return await AgentService(settings, checkpointer=checkpointer).query(session, body)
    except SearchUnavailableError as e:
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
