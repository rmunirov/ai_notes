from __future__ import annotations

import logging
import os
import sys
from contextlib import asynccontextmanager
from typing import Any

import uvicorn
from fastapi import FastAPI, Request
from fastapi.exceptions import RequestValidationError
from fastapi.middleware.cors import CORSMiddleware
from fastapi.responses import JSONResponse

from ai_notes import __version__
from ai_notes.agent.graph import build_agent, memory_checkpointer
from ai_notes.api import agent, health, notes, search
from ai_notes.config import get_settings
from ai_notes.infrastructure.db.session import close_engine, get_engine, init_engine

log = logging.getLogger(__name__)


@asynccontextmanager
async def lifespan(app: FastAPI) -> Any:
    settings = get_settings()
    app.state.settings = settings
    app.state.version = __version__
    app.state.agent_checkpointer = None
    app.state.agent = None
    init_engine(settings.db_url)
    from sqlalchemy import text

    try:
        from langgraph.checkpoint.postgres.aio import AsyncPostgresSaver

        async with AsyncPostgresSaver.from_conn_string(
            settings.checkpoint_url,
        ) as checkpointer:
            await checkpointer.setup()
            app.state.agent_checkpointer = checkpointer
            app.state.agent = build_agent(settings, checkpointer)
            try:
                async with get_engine().connect() as c:
                    await c.execute(text("SELECT 1"))
            except Exception as e:  # noqa: BLE001
                log.error("DB health check at startup: %s", e)
            yield
    except Exception as e:  # noqa: BLE001
        log.info("AsyncPostgres checkpointer unavailable, agent uses in-memory: %s", e)
        app.state.agent_checkpointer = memory_checkpointer()
        app.state.agent = build_agent(settings, app.state.agent_checkpointer)
        try:
            async with get_engine().connect() as c:
                await c.execute(text("SELECT 1"))
        except Exception as e2:  # noqa: BLE001
            log.error("DB health check at startup: %s", e2)
        yield
    await close_engine()


def create_app() -> FastAPI:
    app = FastAPI(title="AI Notes API", version=__version__, lifespan=lifespan)
    app.add_middleware(
        CORSMiddleware,
        allow_origins=["*"],
        allow_credentials=True,
        allow_methods=["*"],
        allow_headers=["*"],
    )
    app.include_router(health.router)
    app.include_router(notes.router)
    app.include_router(search.router)
    app.include_router(agent.router)

    @app.exception_handler(RequestValidationError)
    async def _v(_: Request, exc: RequestValidationError) -> JSONResponse:  # noqa: ARG001
        return JSONResponse(
            status_code=422,
            content={
                "type": "https://ai-notes.local/problems/validation",
                "title": "Некорректные данные",
                "detail": str(exc),
                "status": 422,
            },
        )

    return app


app = create_app()

_PORT_PRINTED = False


def _port_from_env() -> int:
    p = int(os.environ.get("PORT", "8765"))
    if p < 0:
        return 8765
    if p == 0:
        import socket

        s = socket.socket()
        s.bind(("127.0.0.1", 0))
        port = s.getsockname()[1]
        s.close()
        return int(port)
    return p


def run() -> None:
    port = _port_from_env()
    if not _PORT_PRINTED:
        print(f"PORT={port}", file=sys.stdout, flush=True)  # noqa: T201
    use_reload = get_settings().debug
    log_level = "debug" if get_settings().debug else "info"
    uvicorn.run(
        "ai_notes.main:app",
        host="127.0.0.1",
        port=port,
        log_level=log_level,
        reload=use_reload,
    )
