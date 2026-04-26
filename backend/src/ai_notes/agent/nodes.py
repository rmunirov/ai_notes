from __future__ import annotations

import uuid
from typing import TypedDict

from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import AppSettings
from ai_notes.domain.search import SearchRequest, SearchResultItem
from ai_notes.services.search_service import SearchService


class RetrieveState(TypedDict, total=False):
    question: str
    results: list[SearchResultItem]


async def retrieve_chunks(
    session: AsyncSession, settings: AppSettings, question: str, limit: int = 5
) -> list[SearchResultItem]:
    return (
        await SearchService(settings.llm).search(
            session, SearchRequest(query=question, limit=limit)
        )
    ).results


def aggregate_sources(
    results: list[SearchResultItem],
) -> tuple[list[str], list[dict[str, str | uuid.UUID]]]:
    lines: list[str] = []
    out: list[dict[str, str | uuid.UUID]] = []
    seen: set[uuid.UUID] = set()
    for r in results:
        if r.note_id in seen:
            continue
        seen.add(r.note_id)
        lines.append(f"[note_id={r.note_id}] {r.note_title}\nФрагмент: {r.chunk_text}\n")
        out.append(
            {
                "note_id": r.note_id,
                "note_title": r.note_title,
                "snip": r.chunk_text[:200],
            }
        )
    return lines, out
