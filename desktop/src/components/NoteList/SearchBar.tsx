import { useState, useEffect } from "react";
import { useNotesStore } from "../../store/notesStore";
import { tokens } from "../../theme/tokens";

export function SearchBar() {
  const [v, setV] = useState("");
  const s = useNotesStore();
  useEffect(() => {
    const t = setTimeout(() => {
      if (!v.trim()) s.clearSearch();
      else void s.doSearch(v);
    }, 300);
    return () => clearTimeout(t);
  }, [v, s]);
  return (
    <div style={{ display: "flex", gap: 8, marginBottom: 8 }}>
      <input
        aria-label="Семантический поиск"
        value={v}
        onChange={(e) => setV(e.target.value)}
        placeholder="Поиск по смыслу…"
        style={{ flex: 1, padding: 8, background: tokens.colors.surface, color: tokens.colors.text, border: `1px solid ${tokens.colors.border}` }}
      />
      {s.searchLoading && <span>…</span>}
      {v && (
        <button type="button" onClick={() => { setV(""); s.clearSearch(); }}>
          Сброс
        </button>
      )}
    </div>
  );
}
