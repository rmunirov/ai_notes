import { useNotesStore } from "../../store/notesStore";
import { tokens } from "../../theme/tokens";

export function SearchResults() {
  const s = useNotesStore();
  const r = s.searchResults;
  if (r == null) return null;
  if (r.length === 0) {
    return <p style={{ color: tokens.colors.textMuted }}>Ничего не найдено</p>;
  }
  return (
    <div>
      {r.map((x) => (
        <div
          key={x.note_id}
          role="button"
          tabIndex={0}
          onClick={() => void s.open(x.note_id)}
          style={{ padding: 8, borderBottom: `1px solid ${tokens.colors.border}`, cursor: "pointer" }}
        >
          <div>{x.note_title}</div>
          <div style={{ fontSize: 12, color: tokens.colors.textMuted }}>{x.chunk_text}</div>
        </div>
      ))}
    </div>
  );
}
