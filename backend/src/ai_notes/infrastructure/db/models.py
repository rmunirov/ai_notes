from __future__ import annotations

import uuid
from datetime import datetime
from typing import Any

from pgvector.sqlalchemy import Vector  # type: ignore[import-untyped]
from sqlalchemy import (
    CheckConstraint,
    DateTime,
    ForeignKey,
    Integer,
    Text,
    UniqueConstraint,
    text,
)
from sqlalchemy.dialects.postgresql import ARRAY, UUID
from sqlalchemy.orm import Mapped, mapped_column, relationship

from ai_notes.infrastructure.db.base import Base

EMBED_DIM = 2560  # must match note_chunks.embedding (Alembic) and LLM_EMBEDDING_DIMENSIONS


class NoteModel(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="")
    body_html: Mapped[str] = mapped_column(Text, nullable=False, default="")
    body_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    chunks: Mapped[list[NoteChunkModel]] = relationship(
        "NoteChunkModel",
        back_populates="note",
        cascade="all, delete-orphan",
    )


class NoteChunkModel(Base):
    __tablename__ = "note_chunks"
    __table_args__ = (UniqueConstraint("note_id", "chunk_index", name="uq_note_chunk"),)

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    note_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("notes.id", ondelete="CASCADE"),
        nullable=False,
    )
    chunk_index: Mapped[int] = mapped_column(Integer, nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[Any] = mapped_column(Vector(EMBED_DIM), nullable=True)
    indexed_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    note: Mapped[NoteModel] = relationship("NoteModel", back_populates="chunks")


class AgentThreadModel(Base):
    __tablename__ = "agent_threads"

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    updated_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )
    messages: Mapped[list[AgentMessageModel]] = relationship(
        "AgentMessageModel",
        back_populates="thread",
        cascade="all, delete-orphan",
    )


class AgentMessageModel(Base):
    __tablename__ = "agent_messages"
    __table_args__ = (
        CheckConstraint("role IN ('user','assistant')", name="ck_agent_role"),
        CheckConstraint(
            "confidence_level IS NULL OR confidence_level IN ('high','medium','low','none')",
            name="ck_confidence",
        ),
    )

    id: Mapped[uuid.UUID] = mapped_column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    thread_id: Mapped[uuid.UUID] = mapped_column(
        UUID(as_uuid=True),
        ForeignKey("agent_threads.id", ondelete="CASCADE"),
        nullable=False,
    )
    role: Mapped[str] = mapped_column(Text, nullable=False)
    content: Mapped[str] = mapped_column(Text, nullable=False)
    source_note_ids: Mapped[list[uuid.UUID]] = mapped_column(
        ARRAY(UUID(as_uuid=True)), nullable=False, server_default="{}"
    )
    confidence_level: Mapped[str | None] = mapped_column(Text, nullable=True)
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=text("now()")
    )

    thread: Mapped[AgentThreadModel] = relationship("AgentThreadModel", back_populates="messages")
