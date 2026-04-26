import { useNotesStore } from "../../store/notesStore";
import { tokens } from "../../theme/tokens";

export function SearchResults() {
  const s = useNotesStore();
  const r = s.searchResults;
  if (r == null) return null;
  if (r.length === 0) {
    return <p style={{ color: tokens.colors.onSurfaceVariant, fontSize: 14 }}>Ничего не найдено</p>;
  }
  return (
    <div style={{ marginBottom: tokens.space.sm }}>
      {r.map((x) => (
        <div
          key={x.note_id}
          role="button"
          tabIndex={0}
          onClick={() => void s.open(x.note_id)}
          onKeyDown={(e) => (e.key === "Enter" ? void s.open(x.note_id) : null)}
          style={{
            padding: 12,
            marginBottom: tokens.space.sm,
            borderRadius: tokens.radius.sm,
            background: tokens.colors.surfaceContainerHigh,
            cursor: "pointer",
          }}
        >
          <div style={{ color: tokens.colors.onSurface, fontSize: 14, fontWeight: 500 }}>
            {x.note_title}
          </div>
          <div style={{ fontSize: 12, color: tokens.colors.onSurfaceVariant, marginTop: 4 }}>
            {x.chunk_text}
          </div>
        </div>
      ))}
    </div>
  );
}
