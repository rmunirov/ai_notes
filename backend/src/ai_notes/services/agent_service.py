from __future__ import annotations

import uuid
from typing import Any, Literal, cast

from langchain_core.runnables import RunnableConfig
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.agent.context import AgentContext
from ai_notes.agent.graph import build_agent, memory_checkpointer
from ai_notes.config import AppSettings
from ai_notes.domain.agent import (
    AgentAnswer,
    AgentMessageView,
    AgentQueryRequest,
    AgentQueryResponse,
    ThreadMessagesResponse,
)
from ai_notes.infrastructure.db.models import AgentMessageModel, AgentThreadModel
from ai_notes.infrastructure.llm.factory import LLMProviderFactory
from ai_notes.services.search_service import SearchUnavailableError

_INSUFFICIENT = "В ваших заметках нет достаточно информации, чтобы ответить на этот вопрос."


class AgentService:
    def __init__(
        self,
        settings: AppSettings,
        *,
        agent: CompiledStateGraph[Any, Any, Any, Any] | None = None,
    ) -> None:
        self._settings = settings
        self._agent = agent

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

        agent = self._agent or build_agent(self._settings, memory_checkpointer())
        ctx = AgentContext(session=session, settings=self._settings)
        cfg: RunnableConfig = {"configurable": {"thread_id": str(thread_id)}}
        agent_input: dict[str, Any] = {
            "messages": [{"role": "user", "content": req.question}],
        }
        raw_out = await agent.ainvoke(agent_input, config=cfg, context=ctx)

        answer_obj = self._extract_answer(raw_out)
        conf = _coerce_confidence(answer_obj.confidence)
        is_grounded = bool(answer_obj.is_grounded)
        source_refs = list(answer_obj.source_notes) if is_grounded else []

        session.add(
            AgentMessageModel(
                id=uuid.uuid4(),
                thread_id=thread_id,
                role="assistant",
                content=answer_obj.answer,
                source_note_ids=[r.note_id for r in source_refs],
                confidence_level=conf,
            )
        )
        await session.commit()
        return AgentQueryResponse(
            answer=answer_obj.answer,
            confidence=conf,
            source_notes=source_refs,
            thread_id=thread_id,
            is_grounded=is_grounded,
        )

    @staticmethod
    def _extract_answer(raw_out: Any) -> AgentAnswer:
        out: dict[str, Any] = raw_out if isinstance(raw_out, dict) else {}
        structured = out.get("structured_response")
        if isinstance(structured, AgentAnswer):
            return structured
        if isinstance(structured, dict):
            try:
                return AgentAnswer.model_validate(structured)
            except Exception:  # noqa: BLE001
                pass
        last_text = _last_ai_text(out.get("messages"))
        if last_text:
            return AgentAnswer(
                answer=last_text,
                confidence="none",
                is_grounded=False,
                source_notes=[],
            )
        return AgentAnswer(
            answer=_INSUFFICIENT,
            confidence="none",
            is_grounded=False,
            source_notes=[],
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
        agent: CompiledStateGraph[Any, Any, Any, Any] | None = None,
    ) -> AgentService:
        return AgentService(settings, agent=agent)


def _coerce_confidence(value: Any) -> Literal["high", "medium", "low", "none"]:
    if value in ("high", "medium", "low", "none"):
        return cast(Literal["high", "medium", "low", "none"], value)
    return "none"


def _last_ai_text(messages: Any) -> str:
    if not isinstance(messages, list):
        return ""
    for msg in reversed(messages):
        if getattr(msg, "type", None) == "ai":
            content = getattr(msg, "content", "")
            if isinstance(content, str):
                return content
            if isinstance(content, list):
                parts: list[str] = []
                for block in content:
                    if isinstance(block, dict) and block.get("type") == "text":
                        text = block.get("text", "")
                        if isinstance(text, str):
                            parts.append(text)
                if parts:
                    return "".join(parts)
    return ""
