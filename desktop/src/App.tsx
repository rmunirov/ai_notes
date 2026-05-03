import { useState } from "react";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { NoteList } from "./components/NoteList/NoteList";
import { NoteEditor } from "./components/NoteEditor/NoteEditor";
import { SaveErrorToast } from "./components/NoteEditor/SaveErrorToast";
import { AgentPanel } from "./components/AgentPanel/AgentPanel";
import { useNotesStore } from "./store/notesStore";
import { tokens } from "./theme/tokens";
import { ShellLayoutProvider } from "./layout/ShellLayoutContext";

function AppShell() {
  const [showAgent, setShowAgent] = useState(true);
  const s = useNotesStore();
  return (
    <div
      style={{
        display: "flex",
        height: "100vh",
        overflow: "hidden",
        minWidth: 0,
        minHeight: 0,
      }}
    >
      <ErrorBoundary label="Список">
        <NoteList />
      </ErrorBoundary>
      <ErrorBoundary label="Редактор">
        <NoteEditor />
      </ErrorBoundary>
      {s.saveError && (
        <SaveErrorToast
          message={s.saveError}
          onRetry={() => void s.save()}
        />
      )}
      {showAgent ? (
        <ErrorBoundary label="Агент">
          <AgentPanel onRequestClose={() => setShowAgent(false)} />
        </ErrorBoundary>
      ) : (
        <button
          type="button"
          onClick={() => setShowAgent(true)}
          style={{
            position: "fixed",
            top: 16,
            right: 16,
            zIndex: 9,
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
          }}
          aria-label="Показать панель агента"
        >
          Показать агента
        </button>
      )}
    </div>
  );
}

export function App() {
  return (
    <ShellLayoutProvider>
      <AppShell />
    </ShellLayoutProvider>
  );
}
