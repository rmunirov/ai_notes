# AI Notes — desktop UI (Vite + React)

- **Run backend** from repo root: `cd backend && uv run uvicorn ai_notes.main:app --port 8765` (or `uv run python -m ai_notes`).
- **Run UI**: `npm install` then `npm run dev` — Vite dev server proxies API to `http://127.0.0.1:8765` (see `vite.config.ts`).

Tauri: integrate later with `npm create tauri-app@latest` in this folder; `client.ts` uses `@tauri-apps/api` when the shell is present, otherwise the browser dev build uses the Vite proxy.
