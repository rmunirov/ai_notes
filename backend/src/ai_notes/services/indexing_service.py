from __future__ import annotations

import uuid

from sqlalchemy import delete
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import LLMSettings
from ai_notes.infrastructure.db.models import NoteChunkModel, NoteModel
from ai_notes.infrastructure.embeddings.provider import LangChainEmbeddingProvider
from ai_notes.infrastructure.llm.factory import LLMProviderFactory
from ai_notes.services.chunking_service import ChunkingService


class IndexingService:
    def __init__(self, settings: LLMSettings) -> None:
        self._settings = settings
        self._chunker = ChunkingService()

    async def reindex_note(self, session: AsyncSession, note_id: uuid.UUID) -> None:
        if not LLMProviderFactory.is_configured_for_remote(self._settings):
            return
        note = await session.get(NoteModel, note_id)
        if note is None:
            return
        await session.execute(delete(NoteChunkModel).where(NoteChunkModel.note_id == note_id))
        chunks = self._chunker.split(note.body_text)
        if not chunks:
            await session.flush()
            return
        emb = LangChainEmbeddingProvider(LLMProviderFactory.embeddings(self._settings))
        vectors = await emb.embed_documents(chunks)
        for idx, (ctext, vec) in enumerate(zip(chunks, vectors, strict=True)):
            session.add(
                NoteChunkModel(
                    id=uuid.uuid4(),
                    note_id=note_id,
                    chunk_index=idx,
                    chunk_text=ctext,
                    embedding=vec,
                )
            )
        await session.flush()
