import { create } from "zustand";
import { apiGet, apiSend } from "../api/client";

export type NoteSummary = {
  id: string;
  title: string;
  preview: string;
  updated_at: string;
};

type State = {
  inited: boolean;
  list: NoteSummary[];
  total: number;
  selected: string | null;
  bodyHtml: string;
  bodyTitle: string;
  saving: boolean;
  loadError: string | null;
  saveError: string | null;
  search: string;
  searchResults: { note_id: string; note_title: string; chunk_text: string }[] | null;
  searchLoading: boolean;
  fetchList: () => Promise<void>;
  open: (id: string) => Promise<void>;
  create: () => Promise<void>;
  updateBody: (title: string, body: string) => void;
  save: () => Promise<void>;
  remove: (id: string) => Promise<void>;
  doSearch: (q: string) => Promise<void>;
  clearSearch: () => void;
};

export const useNotesStore = create<State>((set, get) => ({
  inited: false,
  list: [],
  total: 0,
  selected: null,
  bodyHtml: "",
  bodyTitle: "",
  saving: false,
  loadError: null,
  saveError: null,
  search: "",
  searchResults: null,
  searchLoading: false,
  fetchList: async () => {
    set({ loadError: null });
    try {
      const d = await apiGet<{ items: NoteSummary[]; total: number }>("/notes?offset=0&limit=200");
      set({ list: d.items, total: d.total, inited: true });
    } catch (e) {
      set({ loadError: String(e), inited: true });
    }
  },
  open: async (id: string) => {
    set({ loadError: null });
    const n = await apiGet<{
      id: string;
      title: string;
      body_html: string;
    }>(`/notes/${id}`);
    set({ selected: id, bodyTitle: n.title, bodyHtml: n.body_html });
  },
  create: async () => {
    const n = await apiSend<{
      id: string;
    }>("/notes", { method: "POST", body: JSON.stringify({ title: "", body_html: "" }) });
    set({ selected: n.id, bodyTitle: "", bodyHtml: "" });
    await get().fetchList();
  },
  updateBody: (title, body) => set({ bodyTitle: title, bodyHtml: body }),
  save: async () => {
    const { selected, bodyTitle, bodyHtml } = get();
    if (!selected) return;
    set({ saving: true, saveError: null });
    try {
      await apiSend(`/notes/${selected}`, {
        method: "PATCH",
        body: JSON.stringify({ title: bodyTitle, body_html: bodyHtml }),
      });
      await get().fetchList();
    } catch (e) {
      set({ saveError: String(e) });
    } finally {
      set({ saving: false });
    }
  },
  remove: async (id: string) => {
    if (!globalThis.confirm("Удалить заметку?")) return;
    await apiSend(`/notes/${id}`, { method: "DELETE" });
    if (get().selected === id) {
      set({ selected: null, bodyHtml: "", bodyTitle: "" });
    }
    await get().fetchList();
  },
  doSearch: async (q: string) => {
    if (!q.trim()) {
      set({ searchResults: null, search: "" });
      return;
    }
    set({ searchLoading: true, search: q });
    try {
      const d = await apiSend<{ results: { note_id: string; note_title: string; chunk_text: string }[] }>(
        "/search",
        { method: "POST", body: JSON.stringify({ query: q, limit: 10 }) }
      );
      set({ searchResults: d.results });
    } catch {
      set({ searchResults: [] });
    } finally {
      set({ searchLoading: false });
    }
  },
  clearSearch: () => set({ search: "", searchResults: null }),
}));
