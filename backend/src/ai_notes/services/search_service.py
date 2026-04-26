from __future__ import annotations

import uuid

from sqlalchemy import text
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import LLMSettings
from ai_notes.domain.search import SearchRequest, SearchResponse, SearchResultItem
from ai_notes.infrastructure.embeddings.provider import LangChainEmbeddingProvider
from ai_notes.infrastructure.llm.factory import LLMProviderFactory


class SearchService:
    def __init__(self, settings: LLMSettings) -> None:
        self._settings = settings

    async def search(self, session: AsyncSession, req: SearchRequest) -> SearchResponse:
        if not LLMProviderFactory.is_configured_for_remote(self._settings):
            msg = "Настройте LLM-провайдер (ключ и base URL) для семантического поиска."
            raise SearchUnavailableError(msg)
        emb = LangChainEmbeddingProvider(LLMProviderFactory.embeddings(self._settings))
        query_vec = await emb.embed_query(req.query)
        vec_literal = "[" + ",".join(str(float(x)) for x in query_vec) + "]"
        sql = text(
            """
            SELECT n.id AS note_id, n.title AS note_title, c.chunk_text,
                   1 - (c.embedding <=> CAST(:qv AS vector)) AS score
            FROM note_chunks c
            JOIN notes n ON n.id = c.note_id
            WHERE c.embedding IS NOT NULL
            ORDER BY c.embedding <=> CAST(:qv AS vector)
            LIMIT :lim
            """
        )
        res = await session.execute(sql, {"qv": vec_literal, "lim": req.limit * 3})
        rows = res.mappings().all()
        # aggregate best score per note
        by_note: dict[uuid.UUID, dict[str, str | float]] = {}
        for r in rows:
            nid = r["note_id"]
            sc = float(r["score"])
            if nid not in by_note or sc > float(by_note[nid]["score"]):
                by_note[nid] = {
                    "note_id": str(nid),
                    "title": r["note_title"],
                    "chunk": r["chunk_text"],
                    "score": sc,
                }
        results_sorted = sorted(by_note.values(), key=lambda x: float(x["score"]), reverse=True)[
            : req.limit
        ]
        items = [
            SearchResultItem(
                note_id=uuid.UUID(str(x["note_id"])),
                note_title=str(x["title"]),
                chunk_text=str(x["chunk"]),
                similarity_score=float(x["score"]),
            )
            for x in results_sorted
        ]
        return SearchResponse(query=req.query, results=items, total=len(items))


class SearchUnavailableError(Exception):
    pass
