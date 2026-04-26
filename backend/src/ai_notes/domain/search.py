from __future__ import annotations

from uuid import UUID

from pydantic import BaseModel, Field


class SearchRequest(BaseModel):
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=50)


class SearchResultItem(BaseModel):
    note_id: UUID
    note_title: str
    chunk_text: str
    similarity_score: float


class SearchResponse(BaseModel):
    query: str
    results: list[SearchResultItem]
    total: int
