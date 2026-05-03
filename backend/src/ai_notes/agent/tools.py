from __future__ import annotations

import logging
from typing import Any

from langchain.tools import ToolRuntime, tool

from ai_notes.agent.context import AgentContext
from ai_notes.domain.search import SearchRequest
from ai_notes.services.search_service import SearchService, SearchUnavailableError

_log = logging.getLogger(__name__)


@tool
async def search_notes(
    query: str, runtime: ToolRuntime[AgentContext, Any]
) -> list[dict[str, Any]]:
    """Search the user's personal notes by semantic similarity.

    Returns up to 5 most relevant note chunks for the given natural-language query.
    Use this tool to fetch evidence before answering. The tool does not invent facts;
    if it returns an empty list, the notes do not contain relevant information.

    Args:
        query: Free-form search query in any language (Russian or English).

    Returns:
        A list of note chunks; each item has `note_id`, `note_title`, `chunk_text`,
        and `similarity_score`.
    """
    if runtime.context is None:
        _log.warning("search_notes tool: missing ToolRuntime.context")
        return []
    ctx: AgentContext = runtime.context
    try:
        resp = await SearchService(ctx.settings.llm).search(
            ctx.session, SearchRequest(query=query, limit=5)
        )
    except SearchUnavailableError as exc:
        _log.warning("search_notes tool: search failed: %s", exc)
        return []
    n = len(resp.results)
    _log.debug("search_notes tool: query_len=%d results=%d", len(query), n)
    return [r.model_dump(mode="json") for r in resp.results]
