from __future__ import annotations

from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator


class SourceNoteRef(BaseModel):
    """Refs from LLM structured output; ``note_id`` is str so providers (e.g. GigaChat)
    that reject JSON Schema ``format: uuid`` still accept the tool response schema."""

    note_id: str = Field(description="Идентификатор заметки в виде строки UUID.")
    note_title: str
    relevance_snippet: str = ""

    @field_validator("note_id", mode="before")
    @classmethod
    def _note_id_as_uuid_string(cls, v: object) -> str:
        if isinstance(v, UUID):
            return str(v)
        if isinstance(v, str):
            return str(UUID(v))
        raise TypeError("note_id must be a UUID string")


class AgentQueryRequest(BaseModel):
    question: str = Field(min_length=1, max_length=5000)
    thread_id: UUID | None = None


class AgentQueryResponse(BaseModel):
    answer: str
    confidence: Literal["high", "medium", "low", "none"]
    source_notes: list[SourceNoteRef]
    thread_id: UUID
    is_grounded: bool


class AgentAnswer(BaseModel):
    """Structured-output schema produced by `langchain.agents.create_agent`.

    Used as the `response_format` (via `ToolStrategy`) so the LLM yields a
    machine-parsable answer instead of free-form text.
    """

    answer: str = Field(description="Ответ на вопрос пользователя на русском языке.")
    confidence: Literal["high", "medium", "low", "none"] = Field(
        description=(
            "Уровень уверенности: 'high'/'medium'/'low' если ответ опирается на заметки, "
            "'none' если данных в заметках недостаточно."
        )
    )
    is_grounded: bool = Field(
        description="True, если ответ полностью основан на предоставленных фрагментах заметок."
    )
    source_notes: list[SourceNoteRef] = Field(
        default_factory=list,
        description="Заметки, использованные для ответа (только если is_grounded=True).",
    )


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
