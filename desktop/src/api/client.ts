import { getInvoker } from "./tauri";

const base = async (): Promise<string> => {
  const inv = getInvoker();
  if (inv) {
    const port = (await inv("get_backend_port", {})) as number;
    return `http://127.0.0.1:${port}`;
  }
  if (import.meta.env.DEV) {
    return "/api";
  }
  return import.meta.env.VITE_BACKEND_URL ?? "http://127.0.0.1:8765";
};

export async function apiGet<T>(path: string): Promise<T> {
  const b = await base();
  const r = await fetch(`${b}${path}`);
  if (!r.ok) throw new Error(`${r.status} ${r.statusText}`);
  return (await r.json()) as T;
}

export async function apiSend<T>(path: string, init: RequestInit): Promise<T> {
  const b = await base();
  const headers: Record<string, string> = { ...(init.headers as Record<string, string>) };
  if (init.body && !headers["Content-Type"]) {
    headers["Content-Type"] = "application/json";
  }
  const r = await fetch(`${b}${path}`, {
    ...init,
    headers,
  });
  if (!r.ok) {
    const t = await r.text();
    throw new Error(t || `${r.status}`);
  }
  return (await r.json()) as T;
}
