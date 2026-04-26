from __future__ import annotations

import uuid
from collections.abc import Sequence

from sqlalchemy import Select, func, select
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.infrastructure.db.models import NoteModel


class NoteRepository:
    def __init__(self, session: AsyncSession) -> None:
        self._session = session

    async def create(self, title: str, body_html: str, body_text: str) -> NoteModel:
        row = NoteModel(
            id=uuid.uuid4(),
            title=title,
            body_html=body_html,
            body_text=body_text,
        )
        self._session.add(row)
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def get(self, note_id: uuid.UUID) -> NoteModel | None:
        return await self._session.get(NoteModel, note_id)

    async def list(self, offset: int = 0, limit: int = 50) -> tuple[Sequence[NoteModel], int]:
        count_q = select(func.count()).select_from(NoteModel)
        total = int((await self._session.execute(count_q)).scalar_one())
        q: Select[tuple[NoteModel]] = (
            select(NoteModel).order_by(NoteModel.updated_at.desc()).offset(offset).limit(limit)
        )
        rows = (await self._session.execute(q)).scalars().all()
        return rows, total

    async def update(
        self, note_id: uuid.UUID, title: str | None, body_html: str | None, body_text: str | None
    ) -> NoteModel | None:
        row = await self.get(note_id)
        if row is None:
            return None
        if title is not None:
            row.title = title
        if body_html is not None:
            row.body_html = body_html
        if body_text is not None:
            row.body_text = body_text
        await self._session.flush()
        await self._session.refresh(row)
        return row

    async def remove(self, note_id: uuid.UUID) -> bool:
        row = await self.get(note_id)
        if row is None:
            return False
        await self._session.delete(row)
        await self._session.flush()
        return True
