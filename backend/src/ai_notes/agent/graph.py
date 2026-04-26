from __future__ import annotations

from typing import Any, cast

from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph import END, START, StateGraph
from langgraph.graph.state import CompiledStateGraph
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.agent import nodes
from ai_notes.agent.state import AgentGraphState
from ai_notes.config import AppSettings
from ai_notes.infrastructure.llm.factory import LLMProviderFactory


def _dump_results(items: list[Any]) -> list[dict[str, object]]:
    return [r.model_dump(mode="json") for r in items]


def build_agent_graph(
    session: AsyncSession,
    settings: AppSettings,
    checkpointer: BaseCheckpointSaver[Any],
) -> CompiledStateGraph[Any, Any, Any]:
    """RAG: retrieve → grade_relevance → generate. Checkpoints use LangGraph thread_id."""
    chat: BaseChatModel = LLMProviderFactory.chat_model(settings.llm)

    async def retrieve(s: AgentGraphState) -> dict[str, object]:
        q = s.get("question", "")
        if not q:
            return {"search_results": []}
        raw = await nodes.retrieve_chunks(session, settings, q, limit=5)
        d = _dump_results(raw)
        return {
            "search_results": d,
        }

    async def grade_relevance(s: AgentGraphState) -> dict[str, object]:
        q = s.get("question", "")
        items_data = s.get("search_results") or []
        if not items_data:
            return {
                "relevant_items": [],
                "no_relevant": True,
                "chunk_relevance": [],
            }
        items = nodes.item_dicts_to_results(
            [cast(dict[str, object], dict(x)) for x in items_data]
        )
        rel, flags = await nodes.grade_relevance_of_chunks(chat, q, items)
        return {
            "relevant_items": _dump_results(rel),
            "no_relevant": len(rel) == 0,
            "chunk_relevance": flags,
        }

    async def generate(s: AgentGraphState) -> dict[str, object]:
        q = s.get("question", "")
        if s.get("no_relevant", True) or not s.get("relevant_items"):
            answer = "В ваших заметках нет достаточно информации, чтобы ответить на этот вопрос."
            return {
                "answer": answer,
                "confidence": "none",
                "source_notes": [],
                "is_grounded": False,
            }
        rel = nodes.item_dicts_to_results(
            [cast(dict[str, object], dict(x)) for x in (s.get("relevant_items") or [])]
        )
        return await nodes.run_generate_llm(settings, q, rel)

    g = StateGraph(AgentGraphState)
    g.add_node("retrieve", retrieve)  # type: ignore[call-overload]
    g.add_node("grade_relevance", grade_relevance)  # type: ignore[call-overload]
    g.add_node("generate", generate)  # type: ignore[call-overload]
    g.add_edge(START, "retrieve")
    g.add_edge("retrieve", "grade_relevance")
    g.add_edge("grade_relevance", "generate")
    g.add_edge("generate", END)
    return g.compile(checkpointer=checkpointer)


def memory_checkpointer() -> BaseCheckpointSaver[Any]:
    from langgraph.checkpoint.memory import MemorySaver

    return MemorySaver()
