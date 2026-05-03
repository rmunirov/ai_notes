# AI Notes — desktop UI (Vite + React + Tauri 2)

## Веб (только браузер)

1. Поднимите API: `cd ../backend && uv run uvicorn ai_notes.main:app --reload --host 127.0.0.1 --port 8765` (или `uv run ai-notes`).
2. `npm install` → `npm run dev` → http://localhost:5173/ (прокси `/api` на `http://127.0.0.1:8765`, см. `vite.config.ts`).

## Нативное окно (Tauri)

Требуются **Rust (cargo)** и **uv** в `PATH`. В dev Tauri поднимает Vite и пытается запустить API: `uv run python -m ai_notes` из каталога `backend` (динамический порт, `get_backend_port`).

- `npm run tauri:dev` — окно + dev server (и встроенный бэкенд, если `uv` доступен).
- `AI_NOTES_SKIP_BACKEND=1` + `npm run tauri:dev` — только UI, API вручную на `8765` (клиент использует порт по умолчанию `8765`, если порт из `invoke` недоступен — см. `src-tauri/src/lib.rs`).
- `npm run build` затем `npm run tauri:build` — production bundle.

`client.ts` в Tauri вызывает `get_backend_port`; в обычном браузере используется прокси `/api`.
