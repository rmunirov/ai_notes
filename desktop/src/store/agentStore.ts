import { create } from "zustand";
import { apiSend } from "../api/client";

const THREAD_STORAGE_KEY = "ai_notes_agent_thread_id";

function getOrCreateThreadId(): string {
  try {
    let id = sessionStorage.getItem(THREAD_STORAGE_KEY);
    if (!id) {
      id = crypto.randomUUID();
      sessionStorage.setItem(THREAD_STORAGE_KEY, id);
    }
    return id;
  } catch {
    return crypto.randomUUID();
  }
}

type Msg = { role: "user" | "assistant"; content: string };

type State = {
  threadId: string | null;
  messages: Msg[];
  loading: boolean;
  error: string | null;
  ask: (q: string) => Promise<void>;
  reset: () => void;
};

export const useAgentStore = create<State>((set) => ({
  threadId: null,
  messages: [],
  loading: false,
  error: null,
  ask: async (q) => {
    set({ loading: true, error: null });
    try {
      const thread_id = getOrCreateThreadId();
      const body = { question: q, thread_id };
      const r = await apiSend<{
        answer: string;
        thread_id: string;
        is_grounded: boolean;
      }>("/agent/query", { method: "POST", body: JSON.stringify(body) });
      set((s) => ({
        threadId: r.thread_id,
        messages: [
          ...s.messages,
          { role: "user" as const, content: q },
          { role: "assistant" as const, content: r.answer },
        ],
      }));
    } catch (e) {
      set({ error: String(e) });
    } finally {
      set({ loading: false });
    }
  },
  reset: () => {
    try {
      sessionStorage.removeItem(THREAD_STORAGE_KEY);
    } catch {
      /* ignore */
    }
    set({ threadId: null, messages: [], error: null });
  },
}));
