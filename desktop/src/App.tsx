import { useState } from "react";
import { ErrorBoundary } from "./components/ErrorBoundary";
import { NoteList } from "./components/NoteList/NoteList";
import { NoteEditor } from "./components/NoteEditor/NoteEditor";
import { SaveErrorToast } from "./components/NoteEditor/SaveErrorToast";
import { AgentPanel } from "./components/AgentPanel/AgentPanel";
import { useNotesStore } from "./store/notesStore";

export function App() {
  const [showAgent, setShowAgent] = useState(true);
  const s = useNotesStore();
  return (
    <div style={{ display: "flex", height: "100vh" }}>
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
          <AgentPanel />
        </ErrorBoundary>
      ) : null}
      <button
        type="button"
        onClick={() => setShowAgent((v) => !v)}
        style={{ position: "fixed", top: 8, right: 8, zIndex: 9 }}
        aria-pressed={showAgent}
        aria-label="Показать панель агента"
      >
        {showAgent ? "Скрыть агента" : "Показать агента"}
      </button>
    </div>
  );
}
