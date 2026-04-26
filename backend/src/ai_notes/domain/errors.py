from __future__ import annotations

from typing import Any

from fastapi import Request
from fastapi.responses import JSONResponse

PROBLEM = "https://ai-notes.local/problems"


def problem_response(status: int, title: str, detail: str, type_id: str = "error") -> JSONResponse:
    return JSONResponse(
        status_code=status,
        content={
            "type": f"{PROBLEM}/{type_id}",
            "title": title,
            "detail": detail,
            "status": status,
        },
    )


def register_error_handlers(app: Any) -> None:  # FastAPI
    from fastapi import FastAPI
    from fastapi.exceptions import RequestValidationError

    if not isinstance(app, FastAPI):
        return

    @app.exception_handler(RequestValidationError)
    async def _validation(_: Request, exc: RequestValidationError) -> JSONResponse:
        return problem_response(
            422,
            "Некорректные данные",
            str(exc),
            "validation",
        )
