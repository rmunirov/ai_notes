from __future__ import annotations

import uuid
from typing import Literal

from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import AppSettings
from ai_notes.domain.agent import (
    AgentMessageView,
    AgentQueryRequest,
    AgentQueryResponse,
    SourceNoteRef,
    ThreadMessagesResponse,
)
from ai_notes.domain.search import SearchRequest
from ai_notes.infrastructure.db.models import AgentMessageModel, AgentThreadModel
from ai_notes.infrastructure.llm.factory import LLMProviderFactory
from ai_notes.services.search_service import SearchService, SearchUnavailableError


class AgentService:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

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

        search = await SearchService(self._settings.llm).search(
            session, SearchRequest(query=req.question, limit=5)
        )
        if not search.results:
            answer = "В ваших заметках нет достаточно информации, чтобы ответить на этот вопрос."
            session.add(
                AgentMessageModel(
                    id=uuid.uuid4(),
                    thread_id=thread_id,
                    role="assistant",
                    content=answer,
                    source_note_ids=[],
                    confidence_level="none",
                )
            )
            await session.commit()
            return AgentQueryResponse(
                answer=answer,
                confidence="none",
                source_notes=[],
                thread_id=thread_id,
                is_grounded=False,
            )

        lines: list[str] = []
        source_refs: list[SourceNoteRef] = []
        seen: set[uuid.UUID] = set()
        for r in search.results:
            if r.note_id in seen:
                continue
            seen.add(r.note_id)
            lines.append(f"[note_id={r.note_id}] {r.note_title}\nФрагмент: {r.chunk_text}\n")
            source_refs.append(
                SourceNoteRef(
                    note_id=r.note_id,
                    note_title=r.note_title,
                    relevance_snippet=r.chunk_text[:200],
                )
            )
        context = "\n".join(lines)
        llm = LLMProviderFactory.chat_model(self._settings.llm)
        sys = SystemMessage(
            content=(
                "You answer ONLY using the provided note excerpts. "
                "If the excerpts are insufficient, say in Russian that the notes do not "
                "contain enough information. Do not invent facts. Answer in Russian."
            )
        )
        hum = HumanMessage(
            content=(f"Контекст из заметок пользователя:\n{context}\n\nВопрос: {req.question}")
        )
        res = await llm.ainvoke([sys, hum])
        answer = str(res.content)
        is_grounded = _infer_grounded(answer)
        conf: Literal["high", "medium", "low", "none"] = "high" if is_grounded else "none"
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


def _infer_grounded(answer: str) -> bool:
    a = answer.lower()
    if "недостаточно" in a or "недостаточно информации" in a:
        return False
    return not ("не содержат" in a and "информац" in a)
