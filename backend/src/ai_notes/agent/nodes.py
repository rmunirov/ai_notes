from __future__ import annotations

import uuid
from typing import Any

from langchain_core.language_models import BaseChatModel
from langchain_core.messages import HumanMessage, SystemMessage
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import AppSettings
from ai_notes.domain.search import SearchRequest, SearchResultItem
from ai_notes.infrastructure.llm.factory import LLMProviderFactory
from ai_notes.services.search_service import SearchService

__all__ = [
    "aggregate_sources",
    "grade_relevance_of_chunks",
    "infer_grounded",
    "retrieve_chunks",
    "run_generate_llm",
]


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


def _ser_results(items: list[SearchResultItem]) -> list[dict[str, object]]:
    return [r.model_dump(mode="json") for r in items]


def _deser_results(data: list[dict[str, object]]) -> list[SearchResultItem]:
    return [SearchResultItem.model_validate(d) for d in data]


async def grade_relevance_of_chunks(
    chat: BaseChatModel, question: str, results: list[SearchResultItem]
) -> tuple[list[SearchResultItem], list[bool]]:
    """LLM: mark each chunk as relevant to the user question (yes/no)."""
    if not results:
        return [], []
    flags: list[bool] = []
    relevant: list[SearchResultItem] = []
    for r in results:
        msg = await chat.ainvoke(
            [
                SystemMessage(
                    content=(
                        "You classify whether a note excerpt answers or relates to the user "
                        "question. Reply with exactly 'yes' or 'no' in English, nothing else."
                    )
                ),
                HumanMessage(
                    content=(
                        f"Question: {question}\n\n"
                        f"Note title: {r.note_title}\n"
                        f"Excerpt: {r.chunk_text[:2000]}\n"
                    )
                ),
            ]
        )
        text = str(msg.content).lower()
        ok = "yes" in text or "да" in text
        flags.append(ok)
        if ok:
            relevant.append(r)
    return relevant, flags


def infer_grounded(answer: str) -> bool:
    a = answer.lower()
    if "недостаточно" in a or "недостаточно информации" in a:
        return False
    return not ("не содержат" in a and "информац" in a)


async def run_generate_llm(
    settings: AppSettings, question: str, results: list[SearchResultItem]
) -> dict[str, Any]:
    """Produce assistant answer, confidence, source_notes, is_grounded from retrieved chunks."""
    if not results:
        answer = "В ваших заметках нет достаточно информации, чтобы ответить на этот вопрос."
        return {
            "answer": answer,
            "confidence": "none",
            "source_notes": [],
            "is_grounded": False,
        }
    lines, source_rows = aggregate_sources(results)
    context = "\n".join(lines)
    llm = LLMProviderFactory.chat_model(settings.llm)
    sys = SystemMessage(
        content=(
            "You answer ONLY using the provided note excerpts. "
            "If the excerpts are insufficient, say in Russian that the notes do not "
            "contain enough information. Do not invent facts. Answer in Russian."
        )
    )
    hum = HumanMessage(
        content=(f"Контекст из заметок пользователя:\n{context}\n\nВопрос: {question}")
    )
    res = await llm.ainvoke([sys, hum])
    answer = str(res.content)
    is_grounded = infer_grounded(answer)
    conf: str = "high" if is_grounded else "none"
    from ai_notes.domain.agent import SourceNoteRef

    source_notes = [
        SourceNoteRef(
            note_id=str(row["note_id"]),
            note_title=str(row["note_title"]),
            relevance_snippet=str(row["snip"]),
        )
        for row in source_rows
    ]
    return {
        "answer": answer,
        "confidence": conf,
        "source_notes": [s.model_dump(mode="json") for s in source_notes],
        "is_grounded": is_grounded,
    }


def item_dicts_to_results(items: list[dict[str, object]]) -> list[SearchResultItem]:
    return _deser_results(items)
