from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field


class SourceNoteRef(BaseModel):
    note_id: UUID
    note_title: str
    relevance_snippet: str = ""


class AgentQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    thread_id: UUID | None = None


class AgentQueryResponse(BaseModel):
    answer: str
    confidence: Literal["high", "medium", "low", "none"]
    source_notes: list[SourceNoteRef]
    thread_id: UUID
    is_grounded: bool


class AgentMessageView(BaseModel):
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    role: Literal["user", "assistant"]
    content: str
    source_note_ids: list[UUID]
    confidence_level: Literal["high", "medium", "low", "none"] | None
    created_at: datetime


class ThreadMessagesResponse(BaseModel):
    thread_id: UUID
    messages: list[AgentMessageView]
