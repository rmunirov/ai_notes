from __future__ import annotations

import uuid

from fastapi import APIRouter, BackgroundTasks, Depends, HTTPException, Query, Request, Response
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import AppSettings
from ai_notes.deps import get_app_settings, get_db
from ai_notes.domain.note import Note, NoteCreate, NoteListResponse, NoteUpdate
from ai_notes.services.note_service import NoteService

router = APIRouter(prefix="/notes", tags=["notes"])


@router.post("", response_model=Note, status_code=201)
async def create_note(
    data: NoteCreate,
    request: Request,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    settings: AppSettings = Depends(get_app_settings),
) -> Note:
    _ = request
    svc = NoteService(settings)
    return await svc.create(session, data, background_tasks)


@router.get("", response_model=NoteListResponse)
async def list_notes(
    offset: int = Query(0, ge=0),
    limit: int = Query(50, ge=1, le=200),
    session: AsyncSession = Depends(get_db),
    settings: AppSettings = Depends(get_app_settings),
) -> NoteListResponse:
    return await NoteService(settings).list(session, offset=offset, limit=limit)


@router.get("/{note_id}", response_model=Note)
async def get_note(
    note_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    settings: AppSettings = Depends(get_app_settings),
) -> Note:
    n = await NoteService(settings).get(session, note_id)
    if n is None:
        _not_found()
    assert n is not None
    return n


@router.patch("/{note_id}", response_model=Note)
async def patch_note(
    note_id: uuid.UUID,
    data: NoteUpdate,
    background_tasks: BackgroundTasks,
    session: AsyncSession = Depends(get_db),
    settings: AppSettings = Depends(get_app_settings),
) -> Note:
    n = await NoteService(settings).update(session, note_id, data, background_tasks)
    if n is None:
        _not_found()
    assert n is not None
    return n


@router.delete("/{note_id}", status_code=204)
async def delete_note(
    note_id: uuid.UUID,
    session: AsyncSession = Depends(get_db),
    settings: AppSettings = Depends(get_app_settings),
) -> Response:
    ok = await NoteService(settings).delete(session, note_id)
    if not ok:
        _not_found()
    return Response(status_code=204)


def _not_found() -> None:
    raise HTTPException(
        status_code=404,
        detail={
            "type": "https://ai-notes.local/problems/note-not-found",
            "title": "Заметка не найдена",
            "detail": "Заметка с указанным ID не существует.",
            "status": 404,
        },
    )
