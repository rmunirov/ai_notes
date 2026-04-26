# Implementation Plan: AI-агент личных заметок и базы знаний

**Branch**: `001-ai-notes-agent` | **Date**: 2026-04-26 | **Spec**: [spec.md](spec.md)
**Input**: Feature specification from `specs/001-ai-notes-agent/spec.md`

## Summary

Десктопное приложение для личных заметок с семантическим поиском и диалогом с AI-агентом.
Python FastAPI-бэкенд обрабатывает CRUD заметок, векторные эмбеддинги (pgvector/PostgreSQL) и
LangGraph-агент строит ответы исключительно на базе пользовательских заметок. Tauri v2 оборачивает
React/TypeScript-фронтенд и управляет жизненным циклом бэкенд-процесса.

## Technical Context

**Language/Version**: Python 3.12 (бэкенд) · TypeScript 5.x / React 18 (UI)
**Primary Dependencies**: FastAPI 0.115+, LangChain 0.3+, LangGraph 0.2+, SQLAlchemy 2.x, Alembic,
  Pydantic v2, pgvector, Tauri v2, Tiptap (rich text editor)
**Storage**: PostgreSQL 16 с расширением pgvector; Alembic для версионирования схемы
**Testing**: pytest + pytest-asyncio (unit + integration) · Testcontainers-python (PostgreSQL в CI) ·
  mypy --strict (type-checking) · coverage ≥ 70% на core-пакетах
**Target Platform**: Десктопное приложение (Windows / macOS / Linux) через Tauri v2 shell
**Project Type**: Desktop app — Tauri v2 shell + React UI + Python FastAPI sidecar
**Performance Goals**:
  - Загрузка списка заметок (cold): ≤ 1,5 с TTI
  - Семантический поиск (5000 заметок): ≤ 2 с p95
  - Сохранение заметки: ≤ 200 мс perceived
  - Ответ агента (типовой вопрос): ≤ 5 с p95
  - Запуск приложения (warm): ≤ 800 мс
**Constraints**: Данные хранятся локально; нет облачной синхронизации в MVP; один пользователь;
  LLM-провайдер конфигурируется (OpenAI-compatible API или LM Studio); нет hard-coded localhost
**Scale/Scope**: До 5000 коротких заметок (~500 слов); один пользователь; MVP без multi-tenancy

## Constitution Check

*GATE: Must pass before Phase 0 research. Re-checked after Phase 1 design.*

| Principle | Gate | Status | Notes |
|-----------|------|--------|-------|
| I. Code Quality First | SRP, DRY, cyclomatic ≤ 10, no dead code | ✅ PASS | Модули разбиты по bounded contexts: api/, domain/, services/, infrastructure/, agent/ — каждый с единственной ответственностью |
| II. Test-First Development | TDD, coverage ≥ 80% (конституция) / 70% floor (пользователь) | ✅ PASS | Используем floor 70% на core-пакетах как пользовательское требование; публичные контракты покрыты интеграционными тестами |
| III. Consistent User Experience | Design tokens, WCAG 2.1 AA, plain-language errors | ✅ PASS | Tiptap/React + единая тема; Tauri не ограничивает доступность; русскоязычный UI; error-state компоненты описаны в contracts/ |
| IV. Performance by Design | Бюджеты определены до кода | ✅ PASS | Все метрики задекларированы в Technical Context выше |
| V. CI & Quality Gates | mypy strict, zero-warning, Testcontainers | ✅ PASS | mypy wired в CI; pytest-cov с floor; docker-compose для PostgreSQL в CI |

**Constitution Check: PASS** — все ворота пройдены. Нарушений нет, таблица Complexity Tracking не требуется.

*Post-Phase 1 re-check*: Архитектура (2 runtime: Python + Tauri/Node) не нарушает принципов;
Tauri sidecar изолирует Python-процесс. Усложнение оправдано: Tauri — единственный способ
получить нативное десктопное окно без дополнительного runtime при Python-бэкенде.

## Project Structure

### Documentation (this feature)

```text
specs/001-ai-notes-agent/
├── plan.md              # Этот файл
├── research.md          # Phase 0: стек-решения и trade-offs
├── data-model.md        # Phase 1: схема БД, Pydantic-модели
├── quickstart.md        # Phase 1: clone → first run
├── contracts/
│   └── api.md           # Phase 1: REST API контракты
└── checklists/
    └── requirements.md  # Уже создан speckit-specify
```

### Source Code (repository root)

```text
ai-notes/
├── backend/                          # Python FastAPI бэкенд
│   ├── src/
│   │   └── ai_notes/
│   │       ├── api/                  # FastAPI routers (notes, search, agent, health)
│   │       ├── domain/               # Pydantic v2 DTOs и доменные модели
│   │       ├── services/             # Бизнес-логика (NoteService, SearchService, AgentService)
│   │       ├── infrastructure/
│   │       │   ├── db/               # SQLAlchemy 2.x ORM модели
│   │       │   ├── migrations/       # Alembic migrations (versioned)
│   │       │   ├── embeddings/       # Абстракция эмбеддинг-провайдера
│   │       │   └── llm/              # Абстракция LLM-провайдера (OpenAI-compat factory)
│   │       ├── agent/                # LangGraph graph, nodes, tools
│   │       └── config.py             # Pydantic BaseSettings (env-driven)
│   ├── tests/
│   │   ├── unit/                     # Доменная логика, graph nodes, Pydantic модели
│   │   ├── integration/              # PostgreSQL через Testcontainers
│   │   └── conftest.py
│   ├── alembic/
│   ├── pyproject.toml                # uv-managed; включает mypy, ruff, pytest
│   └── uv.lock
├── desktop/                          # Tauri v2 десктопная оболочка
│   ├── src/                          # React 18 + TypeScript UI
│   │   ├── components/
│   │   │   ├── NoteList/             # Список заметок + пустые состояния
│   │   │   ├── NoteEditor/           # Tiptap rich text editor
│   │   │   └── AgentPanel/           # Q&A интерфейс агента
│   │   ├── api/                      # HTTP-клиент к FastAPI
│   │   ├── store/                    # Zustand state management
│   │   ├── theme/                    # Design tokens (цвета, типографика, отступы)
│   │   └── App.tsx
│   ├── src-tauri/                    # Rust Tauri shell
│   │   ├── src/main.rs               # Запуск Python sidecar, управление портом
│   │   └── tauri.conf.json           # Конфиг Tauri: sidecar, permissions
│   ├── package.json
│   └── tsconfig.json
├── docker-compose.yml                # PostgreSQL 16 + pgvector для local/CI
├── .env.example                      # Шаблон переменных окружения
└── specs/
    └── 001-ai-notes-agent/
```

**Structure Decision**: Разделение backend/ и desktop/ — два независимых runtime.
Python-бэкенд — единственный владелец данных и AI-логики; Tauri-фронтенд — исключительно UI.
Связь через локальный HTTP (см. research.md: Desktop Stack Decision).

## Complexity Tracking

> Нарушений Constitution Check нет — таблица не заполняется.
