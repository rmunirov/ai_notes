import { useEffect, type CSSProperties } from "react";
import { tokens } from "../../theme/tokens";
import { useNotesStore } from "../../store/notesStore";
import { useShellLayout } from "../../layout/ShellLayoutContext";
import { EmptyState } from "../common/EmptyState";
import { ErrorInline } from "../common/ErrorInline";
import { LoadingSpinner } from "../common/LoadingSpinner";
import { SearchBar } from "./SearchBar";
import { SearchResults } from "./SearchResults";
import { Button } from "../common/Button";

export function NoteList() {
  const { sidebarWidth } = useShellLayout();
  const sidebarStyle: CSSProperties = {
    width: sidebarWidth,
    flexShrink: 0,
    borderRight: `1px solid ${tokens.colors.outlineVariant}`,
    background: tokens.colors.surfaceContainer,
    display: "flex",
    flexDirection: "column",
    height: "100vh",
    boxSizing: "border-box",
    minWidth: 0,
  };
  const s = useNotesStore();
  useEffect(() => {
    void s.fetchList();
  }, []);
  if (s.loadError) {
    return <ErrorInline message={s.loadError} onRetry={() => void s.fetchList()} />;
  }
  if (!s.inited) {
    return (
      <div style={{ ...sidebarStyle, justifyContent: "center" }}>
        <LoadingSpinner />
      </div>
    );
  }
  if (s.list.length === 0 && s.searchResults === null) {
    return (
      <div style={sidebarStyle}>
        <EmptyState
          title="Добро пожаловать"
          hint="Создайте первую заметку, чтобы начать"
          actionLabel="Новая заметка"
          onAction={() => void s.create()}
        />
        <div style={{ padding: `0 ${tokens.space.md}px ${tokens.space.md}px` }}>
          <SearchBar />
        </div>
      </div>
    );
  }
  return (
    <div style={sidebarStyle}>
      <div
        style={{
          padding: tokens.space.md,
          display: "flex",
          gap: tokens.space.sm,
          flexWrap: "wrap",
        }}
      >
        <Button variant="filledTonal" onClick={() => void s.create()}>
          Новая заметка
        </Button>
        <Button
          variant="outlined"
          disabled={!s.selected}
          onClick={() => s.selected && s.remove(s.selected)}
        >
          Удалить
        </Button>
      </div>
      <div style={{ padding: `0 ${tokens.space.md}px` }}>
        <SearchBar />
        {s.searchResults !== null ? <SearchResults /> : null}
      </div>
      <div
        style={{
          flex: 1,
          overflow: "auto",
          minHeight: 0,
          padding: `${tokens.space.sm}px`,
          display: "flex",
          flexDirection: "column",
          gap: tokens.space.sm,
        }}
      >
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
                    borderRadius: tokens.radius.sm,
                    background: tokens.colors.surfaceContainerHigh,
                    cursor: "pointer",
                    outline: s.selected === n.id ? `2px solid ${tokens.colors.primary}` : "none",
                    outlineOffset: 2,
                  }}
                >
                  <strong style={{ color: tokens.colors.onSurface, fontSize: 14 }}>
                    {n.title || "Без названия"}
                  </strong>
                  <div style={{ color: tokens.colors.onSurfaceVariant, fontSize: 12, marginTop: 4 }}>
                    {n.preview}
                  </div>
                </div>
              ))
          : null}
      </div>
    </div>
  );
}
