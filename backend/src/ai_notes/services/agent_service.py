from __future__ import annotations

import uuid
from typing import Any, Literal, cast

from langchain_core.runnables import RunnableConfig
from langgraph.checkpoint.base import BaseCheckpointSaver
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.agent.graph import build_agent_graph, memory_checkpointer
from ai_notes.config import AppSettings
from ai_notes.domain.agent import (
    AgentMessageView,
    AgentQueryRequest,
    AgentQueryResponse,
    SourceNoteRef,
    ThreadMessagesResponse,
)
from ai_notes.infrastructure.db.models import AgentMessageModel, AgentThreadModel
from ai_notes.infrastructure.llm.factory import LLMProviderFactory
from ai_notes.services.search_service import SearchUnavailableError


class AgentService:
    def __init__(
        self,
        settings: AppSettings,
        *,
        checkpointer: BaseCheckpointSaver[Any] | None = None,
    ) -> None:
        self._settings = settings
        self._checkpointer = checkpointer

    async def query(self, session: AsyncSession, req: AgentQueryRequest) -> AgentQueryResponse:
        if not LLMProviderFactory.is_configured_for_remote(self._settings.llm):
            raise SearchUnavailableError(
                "Настройте LLM-провайдер (ключ и base URL), чтобы использовать агента."
            )

        if req.thread_id is not None:
            thread_id = req.thread_id
            if await session.get(AgentThreadModel, thread_id) is None:
                msg = "Диалог не найден"
                raise ValueError(msg)
        else:
            thread_id = uuid.uuid4()
            session.add(AgentThreadModel(id=thread_id))
            await session.flush()

        session.add(
            AgentMessageModel(
                id=uuid.uuid4(),
                thread_id=thread_id,
                role="user",
                content=req.question,
                source_note_ids=[],
                confidence_level=None,
            )
        )
        await session.flush()

        cp = self._checkpointer or memory_checkpointer()
        graph = build_agent_graph(session, self._settings, cp)
        cfg: RunnableConfig = {
            "configurable": {"thread_id": str(thread_id)},
        }
        raw_out = await graph.ainvoke({"question": req.question}, config=cfg)
        out: dict[str, Any] = raw_out if isinstance(raw_out, dict) else {}

        answer = str(out.get("answer", ""))
        c_raw = out.get("confidence", "none")
        conf: Literal["high", "medium", "low", "none"] = (
            cast(Literal["high", "medium", "low", "none"], c_raw)
            if c_raw in ("high", "medium", "low", "none")
            else "none"
        )
        is_grounded = bool(out.get("is_grounded", False))
        sn_raw = out.get("source_notes") or []
        source_refs: list[SourceNoteRef] = []
        for d in sn_raw:
            if isinstance(d, dict):
                source_refs.append(SourceNoteRef.model_validate(d))

        session.add(
            AgentMessageModel(
                id=uuid.uuid4(),
                thread_id=thread_id,
                role="assistant",
                content=answer,
                source_note_ids=[r.note_id for r in source_refs],
                confidence_level=conf,
            )
        )
        await session.commit()
        return AgentQueryResponse(
            answer=answer,
            confidence=conf,
            source_notes=source_refs,
            thread_id=thread_id,
            is_grounded=is_grounded,
        )

    async def list_messages(
        self, session: AsyncSession, thread_id: uuid.UUID
    ) -> ThreadMessagesResponse | None:
        if await session.get(AgentThreadModel, thread_id) is None:
            return None
        r = await session.execute(
            select(AgentMessageModel)
            .where(AgentMessageModel.thread_id == thread_id)
            .order_by(AgentMessageModel.created_at)
        )
        rows = r.scalars().all()
        msgs: list[AgentMessageView] = []
        for m in rows:
            msgs.append(
                AgentMessageView(
                    id=m.id,
                    role=m.role if m.role in ("user", "assistant") else "user",
                    content=m.content,
                    source_note_ids=list(m.source_note_ids),
                    confidence_level=m.confidence_level
                    if m.confidence_level in ("high", "medium", "low", "none")
                    else None,
                    created_at=m.created_at,
                )
            )
        return ThreadMessagesResponse(thread_id=thread_id, messages=msgs)

    @staticmethod
    def from_settings(
        settings: AppSettings,
        *,
        checkpointer: BaseCheckpointSaver[Any] | None = None,
    ) -> AgentService:
        return AgentService(settings, checkpointer=checkpointer)
