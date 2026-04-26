from __future__ import annotations

from typing import Literal, NotRequired, TypedDict


class AgentGraphState(TypedDict, total=False):
    """LangGraph state for the RAG agent."""

    question: str
    search_results: list[dict[str, object]]  # SearchResultItem.model_dump() per item
    relevant_items: list[dict[str, object]]
    no_relevant: bool
    answer: str
    confidence: Literal["high", "medium", "low", "none"]
    source_notes: list[dict[str, object]]  # SourceNoteRef-like dicts
    is_grounded: bool

    # per-chunk LLM grade (for tests / inspection)
    chunk_relevance: NotRequired[list[bool]]
