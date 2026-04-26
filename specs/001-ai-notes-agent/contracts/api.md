# API Contract: FastAPI Backend

**Phase 1 output** | Branch: `001-ai-notes-agent` | Date: 2026-04-26

**Base URL**: `http://localhost:{PORT}` (порт назначается OS при старте; Tauri sidecar передаёт его UI)
**Content-Type**: `application/json` (кроме SSE endpoint)
**Error format**: RFC 7807 Problem Details

```json
{
  "type": "https://ai-notes.local/errors/{error-code}",
  "title": "Краткое описание",
  "detail": "Подробное сообщение для пользователя (plain language)",
  "status": 422
}
```

---

## Health

### GET /health

Проверка работоспособности бэкенда.

**Response 200**
```json
{
  "status": "ok",
  "db": "ok",
  "llm_provider": "openai",
  "version": "0.1.0"
}
```

**Response 503** — если DB недоступна
```json
{
  "status": "degraded",
  "db": "error",
  "detail": "Cannot connect to PostgreSQL"
}
```

---

## Notes

### POST /notes — Создать заметку

**Request body**
```json
{
  "title": "Встреча по проекту",
  "body_html": "<h2>Итоги</h2><ul><li>Задача 1</li></ul>"
}
```

| Поле | Тип | Обязателен | Ограничения |
|------|-----|-----------|-------------|
| `title` | string | Нет | max 500 символов; дефолт `""` |
| `body_html` | string | Нет | max 1 MB; дефолт `""` |

**Response 201**
```json
{
  "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
  "title": "Встреча по проекту",
  "body_html": "<h2>Итоги</h2><ul><li>Задача 1</li></ul>",
  "body_text": "Итоги\n\nЗадача 1",
  "created_at": "2026-04-26T09:00:00Z",
  "updated_at": "2026-04-26T09:00:00Z"
}
```

**Response 413** — тело HTML превышает 1 MB
**Response 422** — нарушение валидации (title > 500 символов и т.д.)

**Side effect**: фоновая задача запускает chunking + embedding индексацию.

---

### GET /notes — Список заметок

**Query params**

| Параметр | Тип | Дефолт | Описание |
|----------|-----|--------|----------|
| `offset` | int | 0 | Смещение для пагинации |
| `limit` | int | 50 | Кол-во заметок; max 200 |

**Response 200**
```json
{
  "items": [
    {
      "id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "title": "Встреча по проекту",
      "preview": "Итоги\n\nЗадача 1 Задача 2...",
      "updated_at": "2026-04-26T09:00:00Z"
    }
  ],
  "total": 42,
  "offset": 0,
  "limit": 50
}
```

---

### GET /notes/{note_id} — Получить заметку

**Path param**: `note_id` — UUID заметки

**Response 200** — полный объект `Note` (см. POST /notes → 201)

**Response 404**
```json
{
  "type": "https://ai-notes.local/errors/note-not-found",
  "title": "Заметка не найдена",
  "detail": "Заметка с указанным ID не существует.",
  "status": 404
}
```

---

### PATCH /notes/{note_id} — Обновить заметку

**Request body** (все поля опциональны)
```json
{
  "title": "Обновлённый заголовок",
  "body_html": "<p>Новый текст</p>"
}
```

**Response 200** — обновлённый объект `Note`
**Response 404** — заметка не найдена
**Response 422** — нарушение валидации

**Side effect**: переиндексация chunks и эмбеддингов в фоне.

---

### DELETE /notes/{note_id} — Удалить заметку

**Response 204** — успешное удаление (тело ответа пустое)
**Response 404** — заметка не найдена

**Side effect**: CASCADE удаляет все chunks. Операция необратима.

---

## Search

### POST /search — Семантический поиск

**Request body**
```json
{
  "query": "встреча с командой по дизайну",
  "limit": 10
}
```

| Поле | Тип | Обязателен | Ограничения |
|------|-----|-----------|-------------|
| `query` | string | Да | 1–1000 символов |
| `limit` | int | Нет | 1–50; дефолт 10 |

**Response 200**
```json
{
  "query": "встреча с командой по дизайну",
  "results": [
    {
      "note_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "note_title": "Встреча по проекту",
      "chunk_text": "Итоги встречи с командой: обсудили дизайн нового экрана...",
      "similarity_score": 0.91
    }
  ],
  "total": 3
}
```

**Response 200 (нет результатов)**
```json
{
  "query": "квантовая физика в 18 веке",
  "results": [],
  "total": 0
}
```

Пустой массив — не ошибка. UI отображает empty state.

**Response 503** — эмбеддинг-сервис недоступен
```json
{
  "type": "https://ai-notes.local/errors/embedding-unavailable",
  "title": "Поиск временно недоступен",
  "detail": "Не удалось подключиться к сервису эмбеддингов. Проверьте настройки LLM-провайдера.",
  "status": 503
}
```

---

## Agent

### POST /agent/query — Задать вопрос агенту

**Request body**
```json
{
  "question": "Что я решил насчёт архитектуры проекта?",
  "thread_id": null
}
```

| Поле | Тип | Обязателен | Описание |
|------|-----|-----------|----------|
| `question` | string | Да | 1–5000 символов |
| `thread_id` | UUID \| null | Нет | null = новый тред; UUID = продолжить диалог |

**Response 200 (ответ найден)**
```json
{
  "answer": "По вашим заметкам, вы решили использовать микросервисную архитектуру с...",
  "confidence": "high",
  "source_notes": [
    {
      "note_id": "3fa85f64-5717-4562-b3fc-2c963f66afa6",
      "note_title": "Архитектурное решение",
      "relevance_snippet": "Решил перейти на микросервисы из-за требования масштабирования..."
    }
  ],
  "thread_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "is_grounded": true
}
```

**Response 200 (данных недостаточно)**
```json
{
  "answer": "В ваших заметках нет достаточно информации, чтобы ответить на этот вопрос.",
  "confidence": "none",
  "source_notes": [],
  "thread_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "is_grounded": false
}
```

HTTP 200 в обоих случаях — отсутствие данных не является ошибкой приложения.
UI использует `is_grounded` и `confidence` для визуального оформления ответа.

**Response 503** — LLM-провайдер недоступен
```json
{
  "type": "https://ai-notes.local/errors/llm-unavailable",
  "title": "Агент временно недоступен",
  "detail": "Не удалось получить ответ от AI-сервиса. Проверьте соединение или настройки провайдера.",
  "status": 503
}
```

**Response 422** — вопрос пустой или превышает лимит

---

### GET /agent/threads/{thread_id}/messages — История диалога

**Response 200**
```json
{
  "thread_id": "7c9e6679-7425-40de-944b-e07fc1f90ae7",
  "messages": [
    {
      "id": "abc123...",
      "role": "user",
      "content": "Что я решил насчёт архитектуры?",
      "source_note_ids": [],
      "confidence_level": null,
      "created_at": "2026-04-26T09:01:00Z"
    },
    {
      "id": "def456...",
      "role": "assistant",
      "content": "По вашим заметкам...",
      "source_note_ids": ["3fa85f64-..."],
      "confidence_level": "high",
      "created_at": "2026-04-26T09:01:04Z"
    }
  ]
}
```

---

## Settings

### GET /settings/provider — Информация о текущем LLM-провайдере

**Response 200**
```json
{
  "provider": "openai",
  "base_url": "https://api.openai.com/v1",
  "model": "gpt-4o-mini",
  "embedding_model": "text-embedding-3-small",
  "api_key_set": true
}
```

*Примечание*: `api_key` в ответ НЕ включается — только факт его наличия (`api_key_set`).

---

## Error States (UI Contract)

UI MUST обрабатывать следующие состояния для каждой зоны:

| Зона | Состояние | Действие UI |
|------|-----------|-------------|
| Список заметок | Загрузка | Skeleton loader |
| Список заметок | Пустой (нет заметок) | Empty state с CTA "Создать первую заметку" |
| Список заметок | Ошибка загрузки | Inline error + кнопка "Повторить" |
| Редактор | Ошибка сохранения | Toast notification с описанием + "Повторить" |
| Поиск | Загрузка | Spinner в поисковой строке |
| Поиск | Нет результатов | Empty state "По вашему запросу ничего не найдено" |
| Поиск | Сервис недоступен | Error banner + инструкция по проверке настроек |
| Агент | Генерация ответа | Streaming индикатор (dots) или progress indicator |
| Агент | Ответ без данных (`is_grounded: false`) | Ответ с иконкой "нет данных" + CTA "Добавить заметки" |
| Агент | LLM недоступен | Error state с инструкцией + ссылка на настройки |
| Агент | Пустая база заметок | Специальный empty state с приглашением создать заметки |
