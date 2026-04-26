# Research: AI-агент личных заметок и базы знаний

**Phase 0 output** | Branch: `001-ai-notes-agent` | Date: 2026-04-26

---

## 1. Desktop Stack Decision

### Decision
**Tauri v2 + React 18 / TypeScript** в качестве UI-оболочки с **FastAPI Python sidecar** в качестве бэкенда.
Связь UI ↔ бэкенд: **локальный HTTP** (FastAPI слушает на динамически выданном порту, Tauri управляет
процессом через sidecar API).

### Rationale
| Критерий | Tauri v2 + React | Electron | Qt for Python (PyQt6) | PyWebView |
|----------|-----------------|----------|-----------------------|-----------|
| Размер бандла | ~5–15 MB | ~80–150 MB | ~30–60 MB | ~10 MB |
| Потребление памяти | Низкое (WebKit) | Высокое (Chromium) | Среднее (Qt) | Низкое |
| Rich text редактор | Tiptap/ProseMirror (production-grade) | То же | QTextEdit (ограниченный) | Tiptap через webview |
| Поддержка русского UI | Полная (Unicode) | Полная | Полная | Полная |
| Доступность (WCAG) | Полная (ARIA, браузерные инструменты) | Полная | Частичная (нет ARIA) | Частичная |
| Интеграция с Python | Sidecar subprocess + HTTP | Subprocess + HTTP | Прямой вызов (же процесс) | Прямой вызов |
| Зрелость экосистемы | Высокая (Tauri 2.0 stable) | Очень высокая | Высокая | Средняя |
| Сложность сборки | Средняя (Rust toolchain нужен) | Средняя | Низкая | Низкая |

**Почему не Electron**: избыточный размер (Chromium bundled), высокое потребление памяти — противоречит
Performance Principle.

**Почему не PyQt6**: QTextEdit не поддерживает production-grade rich text без существенной кастомизации;
доступность ограничена; менее современный look & feel. Если бы весь стек был Python (без отдельного JS),
PyQt6 был бы разумным выбором, но здесь выигрыш недостаточен.

**Почему не PyWebView**: слишком ограниченный IPC (только postMessage), нет native menu, sidecar
management не предусмотрен — придётся реализовывать то, что Tauri даёт из коробки.

### IPC: Локальный HTTP vs WebSocket vs subprocess pipes

**Выбрано: локальный HTTP (REST)**

| Способ | Pros | Cons |
|--------|------|------|
| Локальный HTTP (REST) | Стандартный; легко тестировать curl/pytest; FastAPI OpenAPI из коробки; stateless | Порт надо динамически выдавать и передавать в UI |
| WebSocket | Подходит для стриминга ответов агента | Сложнее тестировать; нужен отдельный URL-протокол |
| Subprocess pipes | Нет сетевого стека | Сложный протокол; нет инструментов отладки; не масштабируется |
| Embedded Python (PyO3) | Один процесс | Несовместимо с async FastAPI и LangGraph; сложная сборка |

**Уточнение**: для стриминга ответов агента (SSE) HTTP вполне достаточен через `text/event-stream`.
WebSocket зарезервирован как опция для будущих версий, если SSE окажется недостаточным.

**Порт-менеджмент**: Tauri sidecar запускает Python с `--port 0` (OS назначает свободный порт);
Rust-код читает порт из stdout бэкенда при старте и передаёт его в React через Tauri `invoke()`.

---

## 2. LangGraph vs Deep Agents

### Decision
**LangGraph 0.2+** без Deep Agents.

### Rationale
Агентский workflow в данном приложении — классический RAG pipeline с возможным multi-turn диалогом:

```
User question
    → Retrieve relevant note chunks (tool call)
    → Grade relevance
    → Generate answer (or "insufficient data" response)
    → Return with source citations
```

LangGraph `StateGraph` покрывает это нативно:
- Узлы: `retrieve`, `grade_relevance`, `generate`, `check_confidence`
- Условные рёбра: переход к `generate` vs `insufficient_data` на основе оценки релевантности
- Персистентный state thread в PostgreSQL (через LangGraph checkpoint store)

**Почему не Deep Agents**:
- Deep Agents добавляет `create_deep_agent()` + `SubAgentMiddleware` поверх LangGraph — дополнительный
  уровень абстракции без функционального выигрыша для этого workflow.
- HITL (human-in-the-loop) в Deep Agents полезен для approval-flows; в нашем случае взаимодействие
  пользователя с агентом — это стандартный chat-loop, который LangGraph поддерживает напрямую.
- LangChain + LangGraph уже указаны как основной стек; Deep Agents тоже строится поверх LangGraph,
  что создаёт двойную зависимость без явной пользы.

**Вывод**: Deep Agents не применяется. Решение задокументировано в соответствии с требованием пользователя.

---

## 3. Хранение эмбеддингов: pgvector vs отдельный векторный DB

### Decision
**PostgreSQL 16 + pgvector** — единственное хранилище для заметок И эмбеддингов.

### Rationale
| Критерий | pgvector | Qdrant / Chroma / Weaviate |
|----------|----------|---------------------------|
| Инфраструктура | Уже есть (PostgreSQL) | Доп. сервис |
| Транзакционность | ACID (note + embedding в одной транзакции) | Eventual consistency |
| Производительность при 5000 заметок | Достаточная (IVFFlat индекс) | Избыточная для масштаба |
| Миграции схемы | Alembic (уже есть) | Отдельные инструменты |
| Оперативные расходы | Нет | Доп. container + healthcheck |

**Chunking-стратегия**: длинные заметки (>500 слов) разбиваются на chunks с перекрытием 50 слов.
Каждый chunk хранится в `note_chunks` со своим embedding. Поиск ищет по chunks, но результат
агрегируется до уровня заметок (избегаем дублирования заметок в результатах).

**Размерность эмбеддинга**: Конфигурируется через `EMBEDDING_DIMENSIONS` в `.env`.
Дефолт: 1536 (OpenAI `text-embedding-3-small`). Для локальных моделей через LM Studio —
задаётся при настройке. pgvector поддерживает до 16 000 измерений.

---

## 4. LLM Provider Abstraction

### Decision
Единая фабрика `LLMProviderFactory` на базе `langchain_openai.ChatOpenAI` с конфигурируемым
`base_url`, `api_key`, `model` и `timeout`.

### Rationale
LM Studio реализует OpenAI-compatible API (`/v1/chat/completions`). Следовательно, один и тот же
`ChatOpenAI` клиент работает и с OpenAI, и с LM Studio — нужно только менять `base_url` и `model`.

```python
# Конфигурация (Pydantic BaseSettings):
class LLMSettings(BaseModel):
    provider: Literal["openai", "lmstudio", "custom"] = "openai"
    base_url: str = "https://api.openai.com/v1"
    api_key: SecretStr = SecretStr("placeholder")
    model: str = "gpt-4o-mini"
    timeout: float = 30.0
    embedding_model: str = "text-embedding-3-small"
    embedding_dimensions: int = 1536
```

Остальной код приложения работает только с интерфейсом `BaseChatModel` и `Embeddings` из LangChain —
провайдер-агностичность гарантирована.

**Embedding provider**: Аналогично — `OpenAIEmbeddings` с кастомным `base_url`. LM Studio
поддерживает `/v1/embeddings` endpoint.

---

## 5. Rich Text Editor

### Decision
**Tiptap v2** (React) — ProseMirror-based rich text редактор.

### Rationale
- Production-ready, используется в Notion, Linear, GitLab
- Поддерживает: заголовки (H1–H3), маркированные/нумерованные списки, жирный/курсив, inline code
- Headless API → полный контроль над стилями через design tokens
- Хранение: **HTML** в БД (поле `body_html`) + **plain text** (поле `body_text`) для поиска и
  embedding. Plain text генерируется из HTML на бэкенде при сохранении (без дублирования: HTML —
  source of truth, plain text — derived field).

### Альтернативы отклонены
- **Slate.js**: менее зрелый, сложная кастомизация
- **Quill**: устаревший (нет активной поддержки v2+)
- **Markdown + preview**: требует знания синтаксиса — нарушает требование спека о "обычном редакторе"

---

## 6. State Management (Frontend)

### Decision
**Zustand** — минималистичное state management решение для React.

### Rationale
- Нет boilerplate Redux
- Поддержка TypeScript из коробки
- Достаточен для: списка заметок, выбранной заметки, состояния агента, loading/error флагов
- Хорошо интегрируется с React Query для server state (кэш API-ответов)

**React Query** (`@tanstack/react-query`) для server state: кэширование, invalidation, loading states.

---

## 7. Тестирование: Testcontainers vs docker-compose в CI

### Decision
**Testcontainers-python** для интеграционных тестов + **docker-compose.yml** для local dev.

### Rationale
- Testcontainers поднимает PostgreSQL программно внутри pytest-сессии → тесты self-contained,
  не зависят от внешнего сервиса
- В CI (GitHub Actions) Docker доступен — Testcontainers работает без дополнительной настройки
- `docker-compose.yml` для удобства разработчика при локальном запуске бэкенда вне тестов

**pgvector в тестах**: образ `pgvector/pgvector:pg16` включает расширение — используем его
в docker-compose и как образ Testcontainers.

---

## 8. mypy Strict Mode

### Decision
`mypy --strict` применяется ко всему `backend/src/ai_notes/` коду.

### Rationale
Pydantic v2 полностью совместим с mypy (plugin `pydantic.mypy`). LangChain 0.3+ имеет стабы.
SQLAlchemy 2.x с `mypy.ini` plugin. Strict mode ловит:
- Неявные `Any` в сигнатурах
- Отсутствующие return types
- Некорректные Optional-handling
Цена: первоначальная настройка stubs; выгода: предотвращение runtime ошибок в async/typed LangGraph nodes.

**Исключения** (через `# type: ignore[...]`): только для известных проблем в сторонних библиотеках,
каждый `ignore` должен иметь комментарий с объяснением. Список отслеживается в `pyproject.toml`.

---

## 9. Packaging: uv

### Decision
**uv** как единственный инструмент управления пакетами (замена pip + virtualenv).

### Rationale
- `uv sync` воспроизводимо восстанавливает окружение из `uv.lock`
- Нет `pip install` ad-hoc команд; все зависимости в `pyproject.toml` (группы: main, dev, test)
- `uv run pytest` запускает в изолированном окружении без активации venv
- Скорость: значительно быстрее pip при cold install

---

## Summary of Decisions

| Область | Решение | Альтернатива отклонена |
|---------|---------|------------------------|
| Desktop shell | Tauri v2 | Electron (тяжёлый), PyQt6 (limited rich text) |
| UI framework | React 18 + TypeScript | Vue, Svelte (меньший экосистемный охват) |
| Rich text | Tiptap v2 | Quill (устарел), Slate (незрелый) |
| IPC | Локальный HTTP (REST + SSE) | WebSocket, pipes |
| Agent framework | LangGraph 0.2+ | Deep Agents (избыточная абстракция) |
| Vector storage | pgvector (PostgreSQL) | Qdrant/Chroma (доп. инфраструктура) |
| LLM abstraction | LangChain ChatOpenAI factory | Custom client |
| Python packaging | uv | pip + poetry |
| State (frontend) | Zustand + React Query | Redux, MobX |
| Integration tests | Testcontainers-python | docker-compose only |
