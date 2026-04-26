import { create } from "zustand";
import { apiSend } from "../api/client";

type Msg = { role: "user" | "assistant"; content: string };

type State = {
  threadId: string | null;
  messages: Msg[];
  loading: boolean;
  error: string | null;
  ask: (q: string) => Promise<void>;
  reset: () => void;
};

export const useAgentStore = create<State>((set, get) => ({
  threadId: null,
  messages: [],
  loading: false,
  error: null,
  ask: async (q) => {
    set({ loading: true, error: null });
    try {
      const body: Record<string, unknown> = { question: q };
      if (get().threadId) body.thread_id = get().threadId;
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
  reset: () => set({ threadId: null, messages: [], error: null }),
}));
