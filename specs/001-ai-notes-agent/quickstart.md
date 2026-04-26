# Quickstart: AI-агент личных заметок и базы знаний

**Phase 1 output** | Branch: `001-ai-notes-agent` | Date: 2026-04-26

---

## Предварительные требования

| Инструмент | Версия | Установка |
|------------|--------|-----------|
| Python | ≥ 3.12 | https://python.org или `pyenv install 3.12` |
| uv | latest | `curl -LsSf https://astral.sh/uv/install.sh \| sh` |
| Docker + Docker Compose | Docker ≥ 24 | https://docs.docker.com/get-docker/ |
| Node.js | ≥ 20 LTS | https://nodejs.org |
| Rust + Cargo | stable | `curl --proto '=https' --tlsv1.2 -sSf https://sh.rustup.rs \| sh` |
| Tauri CLI | v2 | устанавливается автоматически через `npm install` |

> **Только для Windows**: убедитесь, что установлен Microsoft C++ Build Tools
> (через Visual Studio Installer → "Desktop development with C++").

---

## 1. Clone и начальная настройка

```bash
git clone <repository-url> ai-notes
cd ai-notes
```

---

## 2. Настройка PostgreSQL (Docker)

Запустите PostgreSQL с расширением pgvector:

```bash
docker compose up -d postgres
```

Файл `docker-compose.yml` в корне проекта поднимает:
- `postgres` — PostgreSQL 16 + pgvector, порт 5432
- Данные сохраняются в Docker volume `pgdata` (переживает рестарт контейнера)

Проверка:

```bash
docker compose ps
# postgres должен быть в статусе "running"
```

---

## 3. Настройка бэкенда (Python / uv)

```bash
cd backend

# Установить все зависимости (включая dev и test группы)
uv sync --all-extras

# Применить миграции Alembic (создаст таблицы + pgvector extension)
uv run alembic upgrade head
```

### Конфигурация окружения

Скопируйте шаблон и заполните:

```bash
cp ../.env.example .env
```

Минимальная конфигурация `.env`:

```dotenv
# База данных
DB_URL=postgresql+asyncpg://ai_notes:ai_notes@localhost:5432/ai_notes

# LLM провайдер (OpenAI по умолчанию)
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-openai-key
LLM_MODEL=gpt-4o-mini
LLM_EMBEDDING_MODEL=text-embedding-3-small
LLM_EMBEDDING_DIMENSIONS=1536
LLM_TIMEOUT=30.0
```

### Опционально: LM Studio (локальная модель)

1. Скачайте и запустите [LM Studio](https://lmstudio.ai/)
2. Загрузите модель (например, `Mistral 7B Instruct`)
3. Запустите локальный сервер в LM Studio (по умолчанию `http://localhost:1234/v1`)
4. Обновите `.env`:

```dotenv
LLM_BASE_URL=http://localhost:1234/v1
LLM_API_KEY=lm-studio       # любая непустая строка
LLM_MODEL=mistral-7b-instruct-v0.3   # имя модели из LM Studio
LLM_EMBEDDING_MODEL=nomic-embed-text  # модель эмбеддингов в LM Studio
LLM_EMBEDDING_DIMENSIONS=768          # соответствует выбранной модели
```

> **Важно**: значение `LLM_EMBEDDING_DIMENSIONS` должно совпадать с реальной размерностью
> выбранной embedding-модели. При смене модели потребуется новая Alembic-миграция и
> переиндексация всех заметок.

---

## 4. Запуск бэкенда

```bash
cd backend
uv run python -m ai_notes.main
# Бэкенд запустится на динамическом порту (напечатает PORT=XXXX в stdout)
```

В режиме разработки (фиксированный порт 8000, hot reload):

```bash
uv run uvicorn ai_notes.main:app --reload --port 8000
```

API документация (Swagger UI): http://localhost:8000/docs

---

## 5. Запуск десктопного приложения

```bash
cd desktop

# Установить JS-зависимости
npm install

# Режим разработки (hot reload UI + бэкенд как отдельный процесс)
npm run tauri dev

# Production сборка
npm run tauri build
```

> В режиме `tauri dev` бэкенд НЕ запускается автоматически — запустите его вручную (шаг 4).
> В production-сборке Tauri запускает Python-бэкенд как sidecar автоматически.

---

## 6. Запуск тестов

### Unit тесты (без БД)

```bash
cd backend
uv run pytest tests/unit -v
```

### Интеграционные тесты (требуют Docker)

Testcontainers автоматически поднимет PostgreSQL:

```bash
cd backend
uv run pytest tests/integration -v
```

> Первый запуск медленнее — Docker скачивает образ `pgvector/pgvector:pg16`.

### Все тесты с покрытием

```bash
cd backend
uv run pytest --cov=ai_notes --cov-report=term-missing --cov-fail-under=70
```

### Type checking (mypy)

```bash
cd backend
uv run mypy src/ai_notes --strict
```

### Все проверки (как в CI)

```bash
cd backend
uv run ruff check src/           # linting
uv run ruff format --check src/  # форматирование
uv run mypy src/ai_notes --strict
uv run pytest --cov=ai_notes --cov-fail-under=70
```

---

## 7. Остановка и очистка

```bash
# Остановить PostgreSQL контейнер
docker compose down

# Остановить и удалить данные (ОСТОРОЖНО: удаляет все заметки!)
docker compose down -v
```

---

## Структура `.env.example`

```dotenv
# ===== База данных =====
DB_URL=postgresql+asyncpg://ai_notes:ai_notes@localhost:5432/ai_notes

# ===== LLM Провайдер =====
# Для OpenAI:
LLM_BASE_URL=https://api.openai.com/v1
LLM_API_KEY=sk-your-key-here
LLM_MODEL=gpt-4o-mini
LLM_EMBEDDING_MODEL=text-embedding-3-small
LLM_EMBEDDING_DIMENSIONS=1536

# Для LM Studio (раскомментируйте и закомментируйте блок OpenAI):
# LLM_BASE_URL=http://localhost:1234/v1
# LLM_API_KEY=lm-studio
# LLM_MODEL=your-model-name
# LLM_EMBEDDING_MODEL=your-embedding-model
# LLM_EMBEDDING_DIMENSIONS=768

# ===== Общие =====
LLM_TIMEOUT=30.0
DEBUG=false
PORT=0
```

---

## Типичные проблемы

| Проблема | Причина | Решение |
|----------|---------|---------|
| `pgvector extension not found` | Образ БД без pgvector | Используйте `pgvector/pgvector:pg16` в docker-compose |
| `alembic: can't connect to database` | PostgreSQL не запущен | `docker compose up -d postgres` |
| `mypy: Cannot find implementation or library stub` | Отсутствуют stubs | `uv sync --all-extras` (включает mypy stubs) |
| Tauri build fails on Windows | Отсутствует C++ Build Tools | Установите через Visual Studio Installer |
| `LLM_EMBEDDING_DIMENSIONS mismatch` | Размерность модели не совпадает с БД | Создайте новую Alembic-миграцию, переиндексируйте |
| Медленный первый поиск | Индекс IVFFlat требует `VACUUM ANALYZE` | `uv run python -m ai_notes.cli vacuum` |
