from __future__ import annotations

from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.ext.asyncio import AsyncSession

from ai_notes.config import AppSettings
from ai_notes.deps import get_app_settings, get_db
from ai_notes.domain.search import SearchRequest, SearchResponse
from ai_notes.services.search_service import SearchService, SearchUnavailableError

router = APIRouter(prefix="/search", tags=["search"])


@router.post("", response_model=SearchResponse)
async def search_notes(
    body: SearchRequest,
    session: AsyncSession = Depends(get_db),
    settings: AppSettings = Depends(get_app_settings),
) -> SearchResponse:
    try:
        return await SearchService(settings.llm).search(session, body)
    except SearchUnavailableError as e:
        raise HTTPException(
            status_code=503,
            detail={
                "type": "https://ai-notes.local/problems/embedding-unavailable",
                "title": "Поиск временно недоступен",
                "detail": str(e),
                "status": 503,
            },
        ) from e
