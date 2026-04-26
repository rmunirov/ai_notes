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
    <div style={{ display: "flex", gap: tokens.space.sm, marginBottom: tokens.space.sm, alignItems: "center" }}>
      <input
        aria-label="Семантический поиск"
        value={v}
        onChange={(e) => setV(e.target.value)}
        placeholder="Семантический поиск…"
        style={{
          flex: 1,
          minWidth: 0,
          height: 56,
          padding: "0 12px",
          background: tokens.colors.surfaceContainerHigh,
          color: tokens.colors.onSurface,
          border: `1px solid ${tokens.colors.outlineVariant}`,
          borderRadius: tokens.radius.xs,
          fontFamily: "inherit",
          fontSize: 16,
          outline: "none",
        }}
      />
      {s.searchLoading && (
        <span style={{ color: tokens.colors.onSurfaceVariant, fontSize: 14 }}>…</span>
      )}
      {v ? (
        <button
          type="button"
          onClick={() => {
            setV("");
            s.clearSearch();
          }}
          style={{
            margin: 0,
            padding: "10px 12px",
            minHeight: 36,
            fontFamily: "inherit",
            fontSize: 14,
            fontWeight: 500,
            color: tokens.colors.primary,
            background: "transparent",
            border: "none",
            borderRadius: tokens.radius.pill,
            cursor: "pointer",
            flexShrink: 0,
          }}
        >
          Сброс
        </button>
      ) : null}
    </div>
  );
}
