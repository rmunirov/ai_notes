from __future__ import annotations

import os

import pytest
from tests.conftest import TEST_DB_URL, reset_schema

from ai_notes.config import AppSettings
from ai_notes.domain.note import NoteCreate, NoteUpdate
from ai_notes.infrastructure.db.session import close_engine, get_session_maker, init_engine
from ai_notes.main import create_app
from ai_notes.services.note_service import NoteService


def _settings() -> AppSettings:
    return AppSettings(
        db_url=TEST_DB_URL,
        checkpoint_url=TEST_DB_URL.replace("postgresql+asyncpg://", "postgresql://", 1),
    )


@pytest.mark.asyncio
async def test_create_generates_body_text_and_preview() -> None:
    os.environ["DB_URL"] = TEST_DB_URL
    await reset_schema(TEST_DB_URL)
    init_engine(TEST_DB_URL)
    from asgi_lifespan import LifespanManager

    app = create_app()
    async with LifespanManager(app):
        sm = get_session_maker()
        async with sm() as session:
            svc = NoteService(_settings())
            n = await svc.create(
                session,
                NoteCreate(
                    title="Hello",
                    body_html="<p>First paragraph. More text " * 20 + "</p>",
                ),
                None,
            )
            assert "First paragraph" in (n.body_text or "")
            assert len(n.body_text or "") > 0
            lid = n.id
        async with sm() as session:
            got = await NoteService(_settings()).get(session, lid)
            assert got is not None
            assert got.title == "Hello"
    await close_engine()


@pytest.mark.asyncio
async def test_update_changes_note() -> None:
    os.environ["DB_URL"] = TEST_DB_URL
    await reset_schema(TEST_DB_URL)
    init_engine(TEST_DB_URL)
    from asgi_lifespan import LifespanManager

    app = create_app()
    async with LifespanManager(app):
        sm = get_session_maker()
        async with sm() as session:
            svc = NoteService(_settings())
            n = await svc.create(session, NoteCreate(title="", body_html="<p>Untitled</p>"), None)
            nid = n.id
            u = await svc.update(
                session,
                nid,
                NoteUpdate(title="T2", body_html="<p>Updated</p>"),
                None,
            )
            assert u is not None
            assert u.title == "T2"
            assert u.body_text == "Updated"
    await close_engine()


@pytest.mark.asyncio
async def test_delete_removes_note() -> None:
    os.environ["DB_URL"] = TEST_DB_URL
    await reset_schema(TEST_DB_URL)
    init_engine(TEST_DB_URL)
    from asgi_lifespan import LifespanManager

    app = create_app()
    async with LifespanManager(app):
        sm = get_session_maker()
        async with sm() as session:
            svc = NoteService(_settings())
            n = await svc.create(session, NoteCreate(title="X", body_html="<p>x</p>"), None)
            nid = n.id
            ok = await svc.delete(session, nid)
            assert ok is True
        async with sm() as session:
            g = await NoteService(_settings()).get(session, nid)
            assert g is None
    await close_engine()
