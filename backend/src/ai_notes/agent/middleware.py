from __future__ import annotations

import json
from typing import Any, cast

from langchain.agents.middleware import wrap_tool_call
from langchain.agents.middleware.types import ToolCallRequest
from langchain_core.messages import ToolMessage

from ai_notes.agent import nodes
from ai_notes.agent.context import AgentContext
from ai_notes.domain.search import SearchResultItem
from ai_notes.infrastructure.llm.factory import LLMProviderFactory


def _parse_chunks(content: Any) -> list[SearchResultItem]:
    if isinstance(content, list):
        items = content
    else:
        try:
            items = json.loads(content) if isinstance(content, str) else []
        except (TypeError, ValueError):
            return []
    if not isinstance(items, list):
        return []
    parsed: list[SearchResultItem] = []
    for raw in items:
        if isinstance(raw, dict):
            try:
                parsed.append(SearchResultItem.model_validate(raw))
            except Exception:  # noqa: BLE001
                continue
    return parsed


async def _grade_relevance_async(
    request: ToolCallRequest,
    handler: Any,
) -> ToolMessage:
    """Filter `search_notes` results through an LLM relevance grader.

    Wraps the `search_notes` tool: after retrieval, asks the chat model to mark
    each chunk as relevant/irrelevant to the user question. Irrelevant chunks
    are dropped before the result is fed back to the agent.
    """
    response = await handler(request)
    if request.tool_call.get("name") != "search_notes":
        return cast(ToolMessage, response)
    if not isinstance(response, ToolMessage):
        return cast(ToolMessage, response)

    chunks = _parse_chunks(response.content)
    if not chunks:
        return response

    runtime = request.runtime
    ctx_obj = getattr(runtime, "context", None)
    if not isinstance(ctx_obj, AgentContext):
        return response

    question = _last_user_question(request.state)
    if not question:
        return response

    chat = LLMProviderFactory.chat_model(ctx_obj.settings.llm)
    relevant, _flags = await nodes.grade_relevance_of_chunks(chat, question, chunks)
    filtered = [r.model_dump(mode="json") for r in relevant]

    return ToolMessage(
        content=json.dumps(filtered, ensure_ascii=False),
        tool_call_id=response.tool_call_id,
        name=response.name,
        status=response.status,
    )


def _last_user_question(state: Any) -> str:
    """Best-effort extraction of the most recent user question from agent state."""
    messages = state.get("messages") if isinstance(state, dict) else None
    if not messages:
        return ""
    for msg in reversed(messages):
        msg_type = getattr(msg, "type", None)
        if msg_type == "human":
            content = getattr(msg, "content", "")
            return content if isinstance(content, str) else str(content)
    return ""


# `wrap_tool_call`'s Protocol is typed as a sync callable but the runtime accepts
# `async def` implementations as well; mypy can't infer that overload, so we apply
# the decorator after-the-fact with a typed cast.
grade_relevance_middleware = wrap_tool_call(cast(Any, _grade_relevance_async))
