from __future__ import annotations

import logging
import uuid

from fastapi import BackgroundTasks
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import AppSettings
from ai_notes.domain.note import (
    Note,
    NoteCreate,
    NoteListResponse,
    NoteSummary,
    NoteUpdate,
)
from ai_notes.infrastructure.db.note_repository import NoteRepository
from ai_notes.infrastructure.db.session import get_session_maker
from ai_notes.services.indexing_service import IndexingService
from ai_notes.util.text import html_to_plain_text, preview_text

_log = logging.getLogger(__name__)
class NoteService:
    def __init__(self, settings: AppSettings) -> None:
        self._settings = settings

    async def create(
        self, session: AsyncSession, data: NoteCreate, bg: BackgroundTasks | None
    ) -> Note:
        body_text = html_to_plain_text(data.body_html)
        repo = NoteRepository(session)
        row = await repo.create(title=data.title, body_html=data.body_html, body_text=body_text)
        await session.commit()
        _log.info("note created note_id=%s", row.id)
        if bg is not None:
            self._schedule_reindex(bg, row.id)
        return Note.model_validate(row)

    async def get(self, session: AsyncSession, note_id: uuid.UUID) -> Note | None:
        repo = NoteRepository(session)
        row = await repo.get(note_id)
        if row is None:
            return None
        return Note.model_validate(row)

    async def list(self, session: AsyncSession, offset: int, limit: int) -> NoteListResponse:
        repo = NoteRepository(session)
        rows, total = await repo.list(offset=offset, limit=limit)
        items = [
            NoteSummary(
                id=r.id,
                title=r.title or "Без названия",
                preview=preview_text(r.body_text),
                updated_at=r.updated_at,
            )
            for r in rows
        ]
        return NoteListResponse(items=items, total=total, offset=offset, limit=limit)

    async def update(
        self,
        session: AsyncSession,
        note_id: uuid.UUID,
        data: NoteUpdate,
        bg: BackgroundTasks | None,
    ) -> Note | None:
        title = data.title
        body_html = data.body_html
        body_text: str | None = None
        if body_html is not None:
            body_text = html_to_plain_text(body_html)
        repo = NoteRepository(session)
        row = await repo.update(note_id, title=title, body_html=body_html, body_text=body_text)
        if row is None:
            return None
        await session.commit()
        _log.info("note updated note_id=%s", note_id)
        if bg is not None:
            self._schedule_reindex(bg, row.id)
        return Note.model_validate(row)

    async def delete(self, session: AsyncSession, note_id: uuid.UUID) -> bool:
        repo = NoteRepository(session)
        ok = await repo.remove(note_id)
        if ok:
            await session.commit()
            _log.info("note deleted note_id=%s", note_id)
        return ok

    def _schedule_reindex(self, bg: BackgroundTasks, note_id: uuid.UUID) -> None:
        settings = self._settings
        sm = get_session_maker()

        async def _job() -> None:
            async with sm() as s:
                try:
                    await IndexingService(settings.llm).reindex_note(s, note_id)
                    await s.commit()
                except Exception:
                    _log.exception("background reindex failed note_id=%s", note_id)

        bg.add_task(_job)

    @staticmethod
    def from_settings(settings: AppSettings) -> NoteService:
        return NoteService(settings)
