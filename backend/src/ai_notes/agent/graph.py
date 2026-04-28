from __future__ import annotations

from typing import Any

from langchain.agents import create_agent
from langchain.agents.structured_output import ToolStrategy
from langchain_core.language_models import BaseChatModel
from langgraph.checkpoint.base import BaseCheckpointSaver
from langgraph.graph.state import CompiledStateGraph

from ai_notes.agent.context import AgentContext
from ai_notes.agent.middleware import grade_relevance_middleware
from ai_notes.agent.tools import search_notes
from ai_notes.config import AppSettings
from ai_notes.domain.agent import AgentAnswer
from ai_notes.infrastructure.llm.factory import LLMProviderFactory

SYSTEM_PROMPT = (
    "Ты — ассистент по личным заметкам пользователя. Отвечай ТОЛЬКО на основе фрагментов "
    "заметок, полученных через инструмент `search_notes`. Не выдумывай факты и не используй "
    "общие знания.\n\n"
    "Алгоритм работы:\n"
    "1. Вызови `search_notes` с переформулированным под суть вопроса запросом.\n"
    "2. Если инструмент вернул пустой список или фрагменты не отвечают на вопрос — верни "
    "ответ вида «В ваших заметках нет достаточно информации, чтобы ответить на этот вопрос», "
    "поставь confidence='none' и is_grounded=false, source_notes оставь пустым.\n"
    "3. Если фрагменты релевантны — синтезируй краткий ответ на русском языке, поставь "
    "confidence='high' (или 'medium'/'low' при частичном покрытии), is_grounded=true, и "
    "перечисли использованные заметки в source_notes.\n\n"
    "Всегда возвращай результат строго в формате структуры AgentAnswer."
)


def build_agent(
    settings: AppSettings,
    checkpointer: BaseCheckpointSaver[Any] | None,
) -> CompiledStateGraph[Any, Any, Any, Any]:
    """Compile the LangChain v1 RAG agent.

    Per-request data (`AsyncSession`, `AppSettings`) is injected at invocation time
    via the `context=AgentContext(...)` argument, so this function is called once
    at app startup.
    """
    chat: BaseChatModel = LLMProviderFactory.chat_model(settings.llm)
    return create_agent(
        model=chat,
        tools=[search_notes],
        system_prompt=SYSTEM_PROMPT,
        response_format=ToolStrategy(AgentAnswer),
        middleware=[grade_relevance_middleware],
        checkpointer=checkpointer,
        context_schema=AgentContext,
    )


def memory_checkpointer() -> BaseCheckpointSaver[Any]:
    from langgraph.checkpoint.memory import MemorySaver

    return MemorySaver()
