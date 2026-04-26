import { useEffect } from "react";
import { tokens } from "../../theme/tokens";
import { useNotesStore } from "../../store/notesStore";
import { EmptyState } from "../common/EmptyState";
import { ErrorInline } from "../common/ErrorInline";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { SearchBar } from "./SearchBar";
import { SearchResults } from "./SearchResults";
import { Button } from "../common/Button";

export function NoteList() {
  const s = useNotesStore();
  useEffect(() => {
    void s.fetchList();
  }, []);
  if (s.loadError) {
    return <ErrorInline message={s.loadError} onRetry={() => void s.fetchList()} />;
  }
  if (!s.inited) {
    return <LoadingSpinner />;
  }
  if (s.list.length === 0 && s.searchResults === null) {
    return (
      <div style={{ borderRight: `1px solid ${tokens.colors.border}`, minWidth: 240 }}>
        <EmptyState
          title="Добро пожаловать"
          hint="Создайте первую заметку, чтобы начать"
          actionLabel="Новая заметка"
          onAction={() => void s.create()}
        />
        <div style={{ padding: tokens.space.md }}>
          <SearchBar />
        </div>
      </div>
    );
  }
  return (
    <div
      style={{
        borderRight: `1px solid ${tokens.colors.border}`,
        minWidth: 240,
        display: "flex",
        flexDirection: "column",
        height: "100vh",
      }}
    >
      <div style={{ padding: tokens.space.md, display: "flex", gap: 8 }}>
        <Button onClick={() => void s.create()}>Новая заметка</Button>
        <Button onClick={() => s.selected && s.remove(s.selected)}>Удалить</Button>
      </div>
      <div style={{ padding: `0 ${tokens.space.md}px` }}>
        <SearchBar />
        {s.searchResults !== null ? <SearchResults /> : null}
      </div>
      <div style={{ flex: 1, overflow: "auto" }}>
        {s.searchResults === null
          ? s.list.length === 0
            ? <LoadingSpinner />
            : s.list.map((n) => (
                <div
                  key={n.id}
                  role="button"
                  tabIndex={0}
                  onClick={() => void s.open(n.id)}
                  onKeyDown={(e) => (e.key === "Enter" ? void s.open(n.id) : null)}
                  style={{
                    padding: 12,
                    background: s.selected === n.id ? tokens.colors.surface : "transparent",
                    borderBottom: `1px solid ${tokens.colors.border}`,
                    cursor: "pointer",
                  }}
                >
                  <strong>{n.title || "Без названия"}</strong>
                  <div style={{ color: tokens.colors.textMuted, fontSize: 12 }}>{n.preview}</div>
                </div>
              ))
          : null}
      </div>
    </div>
  );
}
