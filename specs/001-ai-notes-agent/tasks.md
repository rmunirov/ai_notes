---
description: "Task list for AI-агент личных заметок и базы знаний"
---

# Tasks: AI-агент личных заметок и базы знаний

**Input**: Design documents from `specs/001-ai-notes-agent/`
**Prerequisites**: plan.md ✅ · spec.md ✅ · data-model.md ✅ · contracts/api.md ✅ · research.md ✅ · quickstart.md ✅

**Tests**: Включены (TDD — Constitution Principle II, план подтверждён).
Тестовые задачи предшествуют задачам реализации в каждом пользовательском сценарии.

**Organization**: Задачи сгруппированы по пользовательским сценариям из spec.md.

## Format: `[ID] [P?] [Story?] Description`

- **[P]**: Можно выполнять параллельно (разные файлы, нет незавершённых зависимостей)
- **[Story]**: Принадлежность к пользовательскому сценарию (US1–US4)
- Все пути файлов указаны относительно корня репозитория

## Path Conventions

- Бэкенд Python: `backend/src/ai_notes/`, тесты: `backend/tests/`
- Фронтенд React: `desktop/src/`, Tauri shell: `desktop/src-tauri/`
- Инфраструктура: `docker-compose.yml`, `.env.example`, `.github/`

---

## Phase 1: Setup (Shared Infrastructure)

**Purpose**: Инициализация обоих проектов, конфигурация, инструменты качества

- [x] T001 Создать структуру директорий бэкенда: `backend/src/ai_notes/{api,domain,services,infrastructure/{db,embeddings,llm},agent}/` и `backend/tests/{unit,integration}/`
- [x] T002 [P] Инициализировать Tauri v2 проект: `desktop/` с React + TypeScript шаблоном (`npm create tauri-app`)
- [x] T003 [P] Создать `backend/pyproject.toml` (uv-managed): зависимости main/dev/test групп, mypy strict config, ruff config, pytest config
- [x] T004 [P] Создать `docker-compose.yml` в корне: сервис `postgres` на базе образа `pgvector/pgvector:pg16`, volume `pgdata`, порт 5432
- [x] T005 [P] Создать `.env.example` в корне со всеми переменными: `DB_URL`, `LLM_BASE_URL`, `LLM_API_KEY`, `LLM_MODEL`, `LLM_EMBEDDING_MODEL`, `LLM_EMBEDDING_DIMENSIONS`, `LLM_TIMEOUT`, `DEBUG`, `PORT`
- [x] T006 [P] Создать `backend/src/ai_notes/config.py`: `LLMSettings`, `DatabaseSettings`, `AppSettings` (Pydantic BaseSettings, env-driven, без hard-coded localhost)
- [x] T007 Инициализировать Alembic в `backend/alembic/`: `alembic.ini`, `env.py` (async, читает `DB_URL` из конфига)
- [x] T008 Создать `backend/src/ai_notes/infrastructure/db/session.py`: `AsyncEngine`, `AsyncSession` factory через `asyncpg`
- [x] T009 [P] Создать `backend/tests/conftest.py`: `pytest-asyncio` async fixtures, Testcontainers PostgreSQL (`pgvector/pgvector:pg16`), Alembic upgrade head на тестовой БД

**Checkpoint**: Оба проекта инициализированы, Docker PostgreSQL запускается, тестовое окружение готово

---

## Phase 2: Foundational (Blocking Prerequisites)

**Purpose**: Ядро инфраструктуры, блокирующее все пользовательские сценарии

**⚠️ CRITICAL**: Ни один пользовательский сценарий не начинается до завершения этой фазы

- [x] T010 Создать Alembic миграцию `001_create_notes_table.py` в `backend/alembic/versions/`: таблица `notes` (id UUID PK, title TEXT, body_html TEXT, body_text TEXT, created_at/updated_at TIMESTAMPTZ) + trigger `set_updated_at`
- [x] T011 [P] Создать `backend/src/ai_notes/infrastructure/db/models.py`: `Base`, `NoteModel` (SQLAlchemy 2.x mapped_column)
- [x] T012 [P] Создать `backend/src/ai_notes/infrastructure/llm/factory.py`: `LLMProviderFactory` — возвращает `ChatOpenAI` и `OpenAIEmbeddings` с конфигурируемым `base_url`, `api_key`, `model`, `timeout`; остальной код работает только с `BaseChatModel` / `Embeddings`
- [x] T013 Создать `backend/src/ai_notes/main.py`: FastAPI app, включает все routers, startup/shutdown lifecycle (DB engine, LangGraph checkpoint init), выводит `PORT=<n>` в stdout при старте
- [x] T014 [P] Создать `backend/src/ai_notes/api/health.py`: `GET /health` — проверяет БД и возвращает статус провайдера
- [x] T015 [P] Создать `desktop/src/api/client.ts`: HTTP-клиент (fetch-based), читает backend port через Tauri `invoke('get_backend_port')`, экспортирует типизированные функции для каждого эндпоинта
- [x] T016 [P] Создать `desktop/src/theme/tokens.ts`: design tokens (цвета, типографика, отступы, elevation) — единственный источник стилевых значений
- [x] T017 Реализовать `desktop/src-tauri/src/main.rs`: Tauri sidecar запускает Python-бэкенд, читает `PORT=<n>` из stdout, сохраняет в app state, предоставляет команду `get_backend_port` для фронтенда
- [x] T018 [P] Создать `desktop/src/components/common/`: `EmptyState.tsx`, `ErrorInline.tsx`, `LoadingSpinner.tsx`, `Button.tsx`, `ConfirmDialog.tsx` — используют только tokens из `theme/tokens.ts`

**Checkpoint**: FastAPI стартует, health endpoint отвечает, Tauri shell открывает окно с подключением к бэкенду

---

## Phase 3: User Story 1 — Создание и редактирование заметки (Priority: P1) 🎯 MVP

**Goal**: Пользователь создаёт, редактирует, просматривает и удаляет заметки; данные сохраняются при перезапуске

**Independent Test**: Создать заметку → перезапустить приложение → заметка на месте с правильным содержимым

### Тесты для User Story 1 (написать ПЕРВЫМИ, убедиться что ПАДАЮТ)

- [x] T019 [P] [US1] Написать интеграционный тест CRUD заметок в `backend/tests/integration/test_notes.py`: create, get, list (pagination), update (title + body), delete + cascade, save-error при недоступной БД
- [x] T020 [P] [US1] Написать unit-тест `NoteService` в `backend/tests/unit/test_note_service.py`: preview generation (первые 200 символов body_text), empty title fallback, updated_at обновляется

### Реализация User Story 1

- [x] T021 [P] [US1] Создать `backend/src/ai_notes/domain/note.py`: `NoteCreate`, `NoteUpdate`, `Note`, `NoteSummary`, `NoteList` (Pydantic v2, `model_config = ConfigDict(from_attributes=True)`)
- [x] T022 [US1] Создать `backend/src/ai_notes/infrastructure/db/note_repository.py`: `NoteRepository` (async CRUD, использует `AsyncSession`; SRP — только доступ к данным)
- [x] T023 [US1] Реализовать `backend/src/ai_notes/services/note_service.py`: `NoteService` (create, get, list с пагинацией, update, delete; генерация `body_text` из HTML; генерация preview)
- [x] T024 [US1] Реализовать `backend/src/ai_notes/api/notes.py`: роутер `/notes` — `POST`, `GET /`, `GET /{id}`, `PATCH /{id}`, `DELETE /{id}`; RFC 7807 error responses
- [x] T025 [P] [US1] Создать `desktop/src/components/NoteList/NoteList.tsx`: список `NoteSummary`, состояния loading (skeleton) / empty ("Создайте первую заметку") / error (inline + retry)
- [x] T026 [P] [US1] Создать `desktop/src/components/NoteEditor/NoteEditor.tsx`: Tiptap editor с расширениями Heading (H1–H3), BulletList, OrderedList, Bold, Italic; авто-сохранение с debounce 1 с
- [x] T027 [P] [US1] Создать `desktop/src/components/NoteEditor/SaveErrorToast.tsx`: toast-уведомление об ошибке сохранения (plain-language текст + кнопка "Повторить")
- [x] T028 [US1] Создать `desktop/src/store/notesStore.ts`: Zustand store — список заметок, выбранная заметка, loading/saving/error флаги, CRUD actions через `api/client.ts`
- [x] T029 [US1] Собрать двухпанельный layout в `desktop/src/App.tsx`: `NoteList` слева (с кнопкой "Новая заметка") + `NoteEditor` справа; keyboard focus order (Tab навигация)

**Checkpoint**: User Story 1 полностью функциональна — можно создавать, редактировать, удалять заметки, они сохраняются при перезапуске

---

## Phase 4: User Story 2 — Семантический поиск заметок (Priority: P2)

**Goal**: Пользователь находит заметки по смыслу запроса, получает список с фрагментами и переходит к полной заметке

**Independent Test**: Создать 5 заметок на разные темы → ввести запрос, сформулированный иначе, чем текст заметки → получить релевантный результат

### Тесты для User Story 2 (написать ПЕРВЫМИ, убедиться что ПАДАЮТ)

- [x] T030 [P] [US2] Написать unit-тест `ChunkingService` в `backend/tests/unit/test_chunking.py`: длинная заметка разбивается на chunks с перекрытием; короткая заметка — один chunk; edge case: пустой текст
- [x] T031 [P] [US2] Написать интеграционный тест поиска в `backend/tests/integration/test_search.py`: индексирование заметки → поиск по похожему запросу возвращает эту заметку; пустая БД → пустой результат; сервис эмбеддингов недоступен → 503

### Реализация User Story 2

- [x] T032 Создать Alembic миграцию `002_add_note_chunks.py` в `backend/alembic/versions/`: таблица `note_chunks` (id, note_id FK CASCADE, chunk_index, chunk_text, embedding VECTOR(1536), indexed_at) + UNIQUE(note_id, chunk_index) + IVFFlat индекс (`lists=100`, `vector_cosine_ops`)
- [x] T033 [P] [US2] Добавить `NoteChunkModel` в `backend/src/ai_notes/infrastructure/db/models.py` (relationship к `NoteModel`, cascade delete)
- [x] T034 [P] [US2] Создать `backend/src/ai_notes/infrastructure/embeddings/provider.py`: Protocol `EmbeddingProvider` + реализация `LangChainEmbeddingProvider` (делегирует в `OpenAIEmbeddings` с конфигурируемым `base_url`)
- [x] T035 [P] [US2] Создать `backend/src/ai_notes/domain/search.py`: `SearchQuery`, `SearchResultItem`, `SearchResponse` (Pydantic v2)
- [x] T036 [US2] Реализовать `backend/src/ai_notes/services/chunking_service.py`: `ChunkingService` — `RecursiveCharacterTextSplitter` (chunk_size=500 слов, overlap=50 слов, разделители `["\n\n", "\n", ". ", " "]`), возвращает `list[str]`
- [x] T037 [US2] Реализовать `backend/src/ai_notes/services/search_service.py`: `SearchService` — embed query → pgvector cosine similarity → агрегация до уровня заметок → `SearchResponse`
- [x] T038 [US2] Добавить фоновую индексацию в `backend/src/ai_notes/services/note_service.py`: после create/update запускать `BackgroundTasks` — удалить старые chunks → chunking → embed → сохранить в `note_chunks`
- [x] T039 [US2] Реализовать `backend/src/ai_notes/api/search.py`: `POST /search`; 503 при недоступности эмбеддинг-провайдера с понятным сообщением
- [x] T040 [P] [US2] Создать `desktop/src/components/NoteList/SearchBar.tsx`: поисковый input, spinner при загрузке, кнопка очистки, debounce 300 мс
- [x] T041 [P] [US2] Создать `desktop/src/components/NoteList/SearchResults.tsx`: список результатов с fragment preview + score badge; empty state "Ничего не найдено"; error banner при 503
- [x] T042 [US2] Интегрировать поиск в `desktop/src/store/notesStore.ts` (search mode vs list mode) и `desktop/src/components/NoteList/NoteList.tsx` (переключение между SearchResults и обычным списком)

**Checkpoint**: User Stories 1 и 2 независимо функциональны — CRUD + семантический поиск работают

---

## Phase 5: User Story 3 — Диалог с агентом (Priority: P3)

**Goal**: Пользователь задаёт вопрос на естественном языке; агент отвечает только на основе заметок; при недостатке данных честно сообщает об этом

**Independent Test**: Создать 3 заметки по теме → задать вопрос → получить ответ со ссылками → задать вопрос вне базы → получить "нет данных"

### Тесты для User Story 3 (написать ПЕРВЫМИ, убедиться что ПАДАЮТ)

- [x] T043 [P] [US3] Написать unit-тесты LangGraph узлов в `backend/tests/unit/test_agent_nodes.py`: `retrieve` находит релевантные chunks; `grade_relevance` возвращает `none` при нерелевантных chunks; `generate` формирует `is_grounded=False` при `confidence=none`
- [x] T044 [P] [US3] Написать интеграционный тест агента в `backend/tests/integration/test_agent.py`: вопрос с релевантными заметками → `is_grounded=True`, source_notes непустые; вопрос без релевантных заметок → `is_grounded=False`; продолжение thread → messages сохраняются

### Реализация User Story 3

- [x] T045 Создать Alembic миграцию `003_add_agent_tables.py` в `backend/alembic/versions/`: таблицы `agent_threads`, `agent_messages` (role CHECK, confidence_level CHECK, source_note_ids UUID[]) + индекс по `(thread_id, created_at)`
- [x] T046 [P] [US3] Создать `backend/src/ai_notes/domain/agent.py`: `AgentQuery`, `AgentResponse`, `SourceNote`, `AgentMessage` (Pydantic v2, Literal types для role и confidence)
- [x] T047 [P] [US3] Реализовать узлы LangGraph в `backend/src/ai_notes/agent/nodes.py`: `retrieve_node` (вызывает SearchService, получает top-5 chunks), `grade_relevance_node` (LLM grader: relevant/not-relevant per chunk), `generate_node` (генерирует ответ или "insufficient data" при `confidence=none`)
- [x] T048 [US3] Реализовать `backend/src/ai_notes/agent/graph.py`: `StateGraph` с состоянием `AgentState`, рёбра: `retrieve → grade_relevance → generate`; условное ребро: если все chunks нерелевантны — `generate` получает флаг `no_data=True`; `AsyncPostgresSaver` checkpoint store
- [x] T049 [US3] Реализовать `backend/src/ai_notes/services/agent_service.py`: `AgentService` — вызывает граф, управляет thread (создание / продолжение), сохраняет сообщения в `agent_messages`, возвращает `AgentResponse`
- [x] T050 [US3] Реализовать `backend/src/ai_notes/api/agent.py`: `POST /agent/query`, `GET /agent/threads/{id}/messages`; 503 при недоступности LLM
- [x] T051 [P] [US3] Создать `desktop/src/components/AgentPanel/AgentMessage.tsx`: отображение одного сообщения (user/assistant role), confidence badge ("на основе заметок" / "нет данных" / уровень уверенности), список source_notes со ссылками на заметки
- [x] T052 [P] [US3] Создать `desktop/src/components/AgentPanel/AgentPanel.tsx`: текстовый input вопроса, список `AgentMessage`, индикатор генерации (анимированные dots); empty state при пустой базе заметок ("Создайте заметки, чтобы задавать вопросы")
- [x] T053 [US3] Создать `desktop/src/store/agentStore.ts`: Zustand store — `threadId`, `messages[]`, `isLoading`, `error`; action `sendQuestion` вызывает `POST /agent/query`
- [x] T054 [US3] Интегрировать `AgentPanel` в `desktop/src/App.tsx`: трёхзонный layout (NoteList | NoteEditor | AgentPanel); переключение видимости AgentPanel кнопкой

**Checkpoint**: Все три user story независимо функциональны — CRUD, поиск, диалог с агентом работают

---

## Phase 6: User Story 4 — Онбординг нового пользователя (Priority: P1)

**Goal**: Новый пользователь создаёт первую заметку и задаёт первый вопрос в одном сеансе без настройки

**Independent Test**: Запустить приложение на чистой машине (PostgreSQL и бэкенд уже запущены) — без каких-либо действий создать заметку и задать вопрос

- [x] T055 [P] [US4] Уточнить `desktop/src/components/NoteList/NoteList.tsx` empty state: крупный заголовок "Добро пожаловать", подзаголовок "Создайте первую заметку", кнопка "Новая заметка" (CTA)
- [x] T056 [P] [US4] Добавить onboarding tooltip в `desktop/src/App.tsx`: при первом запуске (нет заметок) — подсказка в AgentPanel "Сначала создайте заметки, затем спросите меня о них"
- [x] T057 [US4] Проверить graceful degradation бэкенда при отсутствии LLM_API_KEY в `backend/src/ai_notes/main.py`: приложение запускается, CRUD и список работают; search и agent возвращают 503 с понятным сообщением "Настройте LLM-провайдер"
- [x] T058 [US4] Создать `specs/001-ai-notes-agent/checklists/e2e-onboarding.md`: ручной чеклист E2E онбординга (clone → start → первая заметка → первый вопрос), покрывающий SC-001 из spec.md

**Checkpoint**: Все 4 пользовательских сценария работают; новый пользователь может начать за < 5 минут

---

## Phase 7: Polish & Cross-Cutting Concerns

**Purpose**: Качество, CI, доступность, производительность

- [x] T059 [P] Создать `desktop/src/components/ErrorBoundary.tsx`: React Error Boundary для каждой из трёх зон (NoteList, NoteEditor, AgentPanel) — отображает friendly fallback, не крашит всё приложение
- [x] T060 [P] Настроить CI в `.github/workflows/ci.yml`: jobs — `backend-quality` (ruff check, mypy --strict, pytest --cov --cov-fail-under=70 с Testcontainers), `desktop-build` (npm ci, tsc --noEmit, tauri build)
- [x] T061 [P] Прогнать `uv run mypy backend/src/ai_notes --strict` и устранить все ошибки типов во всех модулях
- [x] T062 [P] Прогнать `uv run ruff check backend/src/ --fix` и `ruff format backend/src/` — zero-warning
- [x] T063 [P] Аудит доступности UI: проверить focus order (Tab), contrast ratio ≥ 4.5:1, ARIA-атрибуты на интерактивных элементах `desktop/src/components/**`
- [x] T064 [P] Добавить `GET /settings/provider` в `backend/src/ai_notes/api/health.py`: возвращает provider, model, api_key_set (без раскрытия ключа)
- [x] T065 Провести финальную валидацию `specs/001-ai-notes-agent/quickstart.md`: выполнить все шаги с нуля, исправить несоответствия

---

## Dependencies & Execution Order

### Phase Dependencies

- **Setup (Phase 1)**: Нет зависимостей — стартует немедленно
- **Foundational (Phase 2)**: Зависит от завершения Setup — **блокирует все user stories**
- **US1 (Phase 3)**: Зависит от Foundational — нет зависимостей от других stories
- **US2 (Phase 4)**: Зависит от Foundational; интегрируется с US1 (NoteService), но тестируется независимо
- **US3 (Phase 5)**: Зависит от Foundational + US2 (SearchService используется агентом)
- **US4 (Phase 6)**: Зависит от US1 + US3 — это cross-cutting E2E валидация
- **Polish (Phase 7)**: Зависит от всех user stories

### User Story Dependencies

- **US1 (P1)**: Независима после Foundational
- **US2 (P2)**: Зависит от US1 (NoteService); тест US2 независим (собственный fixture с заметками)
- **US3 (P3)**: Зависит от US2 (SearchService внутри агента); может разрабатываться параллельно при mock SearchService
- **US4 (P1)**: Зависит от US1 + US3; является E2E проверкой, не самостоятельным функциональным блоком

### Within Each User Story

- Тесты MUST быть написаны и ПАДАТЬ до реализации (Constitution Principle II)
- Domain models → Repository/Provider → Service → API router → Frontend store → Frontend components
- Story полностью завершена до перехода к следующей

### Parallel Opportunities

- T001–T009 (Setup): T002, T003, T004, T005, T006 можно запускать параллельно
- T010–T018 (Foundational): T011, T012, T014, T015, T016, T017, T018 параллельны
- US1: T019+T020 параллельны; T021 параллелен T022; T025+T026+T027 параллельны
- US2: T030+T031 параллельны; T033+T034+T035 параллельны; T040+T041 параллельны
- US3: T043+T044 параллельны; T047 параллелен T046; T051+T052 параллельны
- Polish: T059, T060, T061, T062, T063, T064 все параллельны

---

## Parallel Example: User Story 1

```bash
# Запустить тесты параллельно (должны ПАДАТЬ):
Task: "T019 Integration test CRUD в backend/tests/integration/test_notes.py"
Task: "T020 Unit test NoteService в backend/tests/unit/test_note_service.py"

# Запустить domain + ORM параллельно:
Task: "T021 domain/note.py — Pydantic models"
Task: "T022 infrastructure/db/note_repository.py — NoteRepository"

# Запустить frontend компоненты параллельно:
Task: "T025 NoteList.tsx"
Task: "T026 NoteEditor.tsx"
Task: "T027 SaveErrorToast.tsx"
```

---

## Implementation Strategy

### MVP First (User Story 1 только — Фаза 1 до Фазы 3)

1. Завершить Phase 1: Setup
2. Завершить Phase 2: Foundational (КРИТИЧНО — блокирует всё)
3. Завершить Phase 3: US1
4. **СТОП и ВАЛИДАЦИЯ**: заметки создаются, сохраняются при перезапуске, UI отвечает < 1 с
5. Готово к демонстрации как simple notes app

### Incremental Delivery

1. Setup + Foundational → инфраструктура готова
2. US1 → CRUD работает → демо как заметочник
3. US2 → добавить семантический поиск → демо расширенного поиска
4. US3 → добавить агента → полная ценность продукта
5. US4 + Polish → production-ready

### Parallel Team Strategy

С несколькими разработчиками после завершения Foundational:
- Разработчик A: Backend US1 (NoteService, API router)
- Разработчик B: Frontend US1 (NoteList, NoteEditor, store)
- Разработчик C: US2 backend (ChunkingService, SearchService, embeddings)

---

## Notes

- `[P]` = разные файлы, нет незавершённых зависимостей
- `[USn]` = принадлежность к user story для трассируемости
- Каждый тест пишется и проверяется на FAIL до реализации (TDD)
- Commit после каждой задачи или логической группы
- Остановиться на каждом checkpoint для независимой валидации story
- Исключить: расплывчатые задачи, конфликты по одному файлу, inter-story зависимости, нарушающие независимость
