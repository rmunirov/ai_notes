# Data Model: AI-агент личных заметок и базы знаний

**Phase 1 output** | Branch: `001-ai-notes-agent` | Date: 2026-04-26

---

## Обзор

Единственное хранилище — PostgreSQL 16 с расширением pgvector. Схема управляется через Alembic.
Три bounded context:
1. **Notes** — хранение заметок и текстового контента
2. **Embeddings** — векторные представления chunks заметок для семантического поиска
3. **Agent** — история диалогов и LangGraph checkpoint state

---

## SQL-схема (Alembic migrations)

### Миграция 001: Базовая схема

```sql
-- Расширение pgvector
CREATE EXTENSION IF NOT EXISTS vector;

-- ===== NOTES =====

CREATE TABLE notes (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    title       TEXT        NOT NULL DEFAULT '',
    body_html   TEXT        NOT NULL DEFAULT '',   -- source of truth (Tiptap HTML)
    body_text   TEXT        NOT NULL DEFAULT '',   -- derived: plain text для embedding + поиска
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

-- Автообновление updated_at
CREATE OR REPLACE FUNCTION set_updated_at()
RETURNS TRIGGER LANGUAGE plpgsql AS $$
BEGIN
    NEW.updated_at = NOW();
    RETURN NEW;
END;
$$;

CREATE TRIGGER notes_updated_at
    BEFORE UPDATE ON notes
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ===== NOTE CHUNKS (для эмбеддингов) =====

CREATE TABLE note_chunks (
    id              UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    note_id         UUID        NOT NULL REFERENCES notes(id) ON DELETE CASCADE,
    chunk_index     INTEGER     NOT NULL,               -- порядок chunk внутри заметки
    chunk_text      TEXT        NOT NULL,               -- текст chunk (из body_text)
    embedding       VECTOR(1536),                       -- размерность конфигурируема (см. примечание)
    indexed_at      TIMESTAMPTZ NOT NULL DEFAULT NOW(), -- когда эмбеддинг был создан
    UNIQUE (note_id, chunk_index)
);

-- IVFFlat индекс для cosine similarity поиска
-- Параметр lists = ROUND(SQRT(expected_rows)); при 5000 заметках ~71 lists
CREATE INDEX note_chunks_embedding_idx
    ON note_chunks
    USING ivfflat (embedding vector_cosine_ops)
    WITH (lists = 100);

-- ===== AGENT THREADS =====

CREATE TABLE agent_threads (
    id          UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    created_at  TIMESTAMPTZ NOT NULL DEFAULT NOW(),
    updated_at  TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE TRIGGER agent_threads_updated_at
    BEFORE UPDATE ON agent_threads
    FOR EACH ROW EXECUTE FUNCTION set_updated_at();

-- ===== AGENT MESSAGES =====

CREATE TABLE agent_messages (
    id                  UUID        PRIMARY KEY DEFAULT gen_random_uuid(),
    thread_id           UUID        NOT NULL REFERENCES agent_threads(id) ON DELETE CASCADE,
    role                TEXT        NOT NULL CHECK (role IN ('user', 'assistant')),
    content             TEXT        NOT NULL,
    source_note_ids     UUID[]      NOT NULL DEFAULT '{}',    -- заметки, использованные в ответе
    confidence_level    TEXT        CHECK (confidence_level IN ('high', 'medium', 'low', 'none')),
    created_at          TIMESTAMPTZ NOT NULL DEFAULT NOW()
);

CREATE INDEX agent_messages_thread_idx ON agent_messages (thread_id, created_at);

-- ===== LANGGRAPH CHECKPOINT STATE =====
-- LangGraph использует собственные таблицы (checkpoints, checkpoint_blobs, checkpoint_writes)
-- при инициализации через AsyncPostgresSaver.
-- Эти таблицы создаются LangGraph автоматически при первом запуске;
-- управляются отдельно от Alembic (не трогать вручную).
```

**Примечание о размерности эмбеддинга**: `VECTOR(1536)` соответствует `text-embedding-3-small`.
При смене модели необходима новая Alembic-миграция (ALTER COLUMN + REINDEX). Размерность управляется
через конфигурацию `EMBEDDING_DIMENSIONS`.

---

## Pydantic v2 Domain Models (DTOs)

### Notes

```python
# backend/src/ai_notes/domain/note.py
from __future__ import annotations
from datetime import datetime
from uuid import UUID
import uuid

from pydantic import BaseModel, Field, ConfigDict


class NoteCreate(BaseModel):
    """DTO для создания новой заметки."""
    title: str = Field(default="", max_length=500)
    body_html: str = Field(default="")


class NoteUpdate(BaseModel):
    """DTO для обновления заметки (все поля опциональны)."""
    title: str | None = Field(default=None, max_length=500)
    body_html: str | None = Field(default=None)


class Note(BaseModel):
    """Полное представление заметки (из БД)."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    body_html: str
    body_text: str
    created_at: datetime
    updated_at: datetime


class NoteSummary(BaseModel):
    """Краткое представление для списка заметок."""
    model_config = ConfigDict(from_attributes=True)

    id: UUID
    title: str
    preview: str          # первые ~200 символов body_text
    updated_at: datetime


class NoteList(BaseModel):
    """Paginated список заметок."""
    items: list[NoteSummary]
    total: int
    offset: int
    limit: int
```

### Search

```python
# backend/src/ai_notes/domain/search.py
from pydantic import BaseModel, Field
from uuid import UUID


class SearchQuery(BaseModel):
    """Запрос семантического поиска."""
    query: str = Field(min_length=1, max_length=1000)
    limit: int = Field(default=10, ge=1, le=50)


class SearchResultItem(BaseModel):
    """Один результат семантического поиска."""
    note_id: UUID
    note_title: str
    chunk_text: str           # релевантный фрагмент
    similarity_score: float   # cosine similarity [0, 1]


class SearchResponse(BaseModel):
    """Ответ на поисковый запрос."""
    query: str
    results: list[SearchResultItem]
    total: int
```

### Agent

```python
# backend/src/ai_notes/domain/agent.py
from __future__ import annotations
from datetime import datetime
from typing import Literal
from uuid import UUID

from pydantic import BaseModel, Field


class AgentQuery(BaseModel):
    """Запрос к AI-агенту."""
    question: str = Field(min_length=1, max_length=5000)
    thread_id: UUID | None = Field(default=None)  # None → новый thread


class SourceNote(BaseModel):
    """Ссылка на заметку, использованную в ответе агента."""
    note_id: UUID
    note_title: str
    relevance_snippet: str   # фрагмент, обосновывающий включение


class AgentResponse(BaseModel):
    """Ответ AI-агента."""
    answer: str
    confidence: Literal["high", "medium", "low", "none"]
    source_notes: list[SourceNote]
    thread_id: UUID
    is_grounded: bool        # True если ответ основан на заметках; False если "нет данных"


class AgentMessage(BaseModel):
    """Одно сообщение в истории диалога."""
    id: UUID
    role: Literal["user", "assistant"]
    content: str
    source_note_ids: list[UUID]
    confidence_level: Literal["high", "medium", "low", "none"] | None
    created_at: datetime
```

### Config (Pydantic BaseSettings)

```python
# backend/src/ai_notes/config.py
from __future__ import annotations
from pydantic import SecretStr, Field
from pydantic_settings import BaseSettings, SettingsConfigDict


class LLMSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="LLM_")

    base_url: str = "https://api.openai.com/v1"
    api_key: SecretStr = Field(default=SecretStr("sk-placeholder"))
    model: str = "gpt-4o-mini"
    timeout: float = 30.0
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536


class DatabaseSettings(BaseSettings):
    model_config = SettingsConfigDict(env_prefix="DB_")

    url: str = "postgresql+asyncpg://ai_notes:ai_notes@localhost:5432/ai_notes"


class AppSettings(BaseSettings):
    model_config = SettingsConfigDict(
        env_file=".env",
        env_file_encoding="utf-8",
        extra="ignore",
    )

    debug: bool = False
    port: int = 0            # 0 = OS-assigned (Tauri sidecar mode)
    llm: LLMSettings = Field(default_factory=LLMSettings)
    db: DatabaseSettings = Field(default_factory=DatabaseSettings)
```

---

## SQLAlchemy 2.x ORM Models

```python
# backend/src/ai_notes/infrastructure/db/models.py
from __future__ import annotations
import uuid
from datetime import datetime

from sqlalchemy import String, Text, DateTime, CheckConstraint, UniqueConstraint, ARRAY
from sqlalchemy.dialects.postgresql import UUID as PGUUID
from sqlalchemy.orm import DeclarativeBase, Mapped, mapped_column, relationship
from pgvector.sqlalchemy import Vector


class Base(DeclarativeBase):
    pass


class NoteModel(Base):
    __tablename__ = "notes"

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True,
                                           default=uuid.uuid4)
    title: Mapped[str] = mapped_column(Text, nullable=False, default="")
    body_html: Mapped[str] = mapped_column(Text, nullable=False, default="")
    body_text: Mapped[str] = mapped_column(Text, nullable=False, default="")
    created_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)
    updated_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    chunks: Mapped[list[NoteChunkModel]] = relationship(
        "NoteChunkModel", back_populates="note", cascade="all, delete-orphan"
    )


class NoteChunkModel(Base):
    __tablename__ = "note_chunks"
    __table_args__ = (UniqueConstraint("note_id", "chunk_index"),)

    id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True), primary_key=True,
                                           default=uuid.uuid4)
    note_id: Mapped[uuid.UUID] = mapped_column(PGUUID(as_uuid=True),
                                                nullable=False)
    chunk_index: Mapped[int] = mapped_column(nullable=False)
    chunk_text: Mapped[str] = mapped_column(Text, nullable=False)
    embedding: Mapped[list[float] | None] = mapped_column(Vector(1536), nullable=True)
    indexed_at: Mapped[datetime] = mapped_column(DateTime(timezone=True), nullable=False)

    note: Mapped[NoteModel] = relationship("NoteModel", back_populates="chunks")
```

---

## Правила валидации

| Поле | Правило | Обработка нарушения |
|------|---------|---------------------|
| `notes.title` | max 500 символов | HTTP 422 с описанием поля |
| `notes.body_html` | Размер HTML ≤ 1 MB | HTTP 413 |
| `search.query` | 1–1000 символов | HTTP 422 |
| `agent.question` | 1–5000 символов | HTTP 422 |
| `note_chunks.chunk_text` | Непустой | Assertion в NoteChunkingService |
| `agent_messages.role` | 'user' или 'assistant' | DB CHECK constraint |
| `agent_messages.confidence_level` | Перечислимое или NULL | DB CHECK constraint |

---

## Chunking Strategy

- **Граница chunk**: 500 слов (приблизительно 3500 символов) с перекрытием 50 слов (350 символов)
- **Алгоритм**: LangChain `RecursiveCharacterTextSplitter` с разделителями `["\n\n", "\n", ". ", " "]`
- **Пере-индексация**: при обновлении заметки все старые chunks удаляются (CASCADE), новые создаются
- **Дедупликация**: chunk-текст хранится в `note_chunks.chunk_text`; оригинал — в `notes.body_text`.
  Это осознанное дублирование: chunk-текст может отличаться от соответствующего участка body_text
  из-за перекрытий. Документировано в compliance с Constitution Principle I (DRY exception justified).

---

## State Transitions

```
Note lifecycle:
  [CREATE] → SAVED → [UPDATE] → SAVED
                   ↓
              [DELETE] → DELETED (CASCADE deletes chunks + search index)

Chunk indexing:
  Note SAVED → background task: CHUNK → EMBED → STORED in note_chunks
  Note UPDATED → DELETE old chunks → CHUNK → EMBED → STORED

Agent thread:
  [NEW QUERY without thread_id] → CREATE thread → PROCESS → RESPOND
  [NEW QUERY with thread_id] → LOAD thread → PROCESS → RESPOND (multi-turn)
```
