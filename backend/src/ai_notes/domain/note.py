from __future__ import annotations

from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class NoteCreate(BaseModel):
    title: str = Field(default="", max_length=500)
    body_html: str = Field(default="")


class NoteUpdate(BaseModel):
    title: str | None = Field(default=None, max_length=500)
    body_html: str | None = None


class Note(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    body_html: str
    body_text: str
    created_at: datetime
    updated_at: datetime


class NoteSummary(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    preview: str
    updated_at: datetime


class NoteListResponse(BaseModel):
    items: list[NoteSummary]
    total: int
    offset: int
    limit: int
