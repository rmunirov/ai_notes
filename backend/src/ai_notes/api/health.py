from __future__ import annotations

from fastapi import APIRouter, Depends, Request
from sqlalchemy import text

from ai_notes.config import AppSettings
from ai_notes.deps import get_app_settings
from ai_notes.infrastructure.db.session import get_engine
from ai_notes.infrastructure.llm.factory import LLMProviderFactory

router = APIRouter(tags=["health"])


@router.get("/health")
async def health(
    request: Request, settings: AppSettings = Depends(get_app_settings)
) -> dict[str, object]:
    db_status = "error"
    try:
        engine = get_engine()
        async with engine.connect() as conn:
            await conn.execute(text("SELECT 1"))
        db_status = "ok"
    except Exception:
        db_status = "error"
    version = getattr(request.app, "version", "0.1.0")
    prov = "none"
    if LLMProviderFactory.is_configured_for_remote(settings.llm):
        prov = "openai-compatible"
    return {
        "status": "ok" if db_status == "ok" else "degraded",
        "db": db_status,
        "llm_provider": prov,
        "version": version,
    }


@router.get("/settings/provider")
async def settings_provider(
    settings: AppSettings = Depends(get_app_settings),
) -> dict[str, object]:
    return {
        "provider": "openai-compatible",
        "base_url": settings.llm.base_url,
        "model": settings.llm.model,
        "embedding_model": settings.llm.embedding_model,
        "api_key_set": settings.llm.api_key_set,
    }
