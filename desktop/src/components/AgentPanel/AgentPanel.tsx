import { useState } from "react";
import { useAgentStore } from "../../store/agentStore";
import { useNotesStore } from "../../store/notesStore";
import { useShellLayout } from "../../layout/ShellLayoutContext";
import { tokens } from "../../theme/tokens";
import { AgentMessage } from "./AgentMessage";
import { Button } from "../common/Button";

type Props = {
  onRequestClose?: () => void;
};

export function AgentPanel({ onRequestClose }: Props) {
  const a = useAgentStore();
  const n = useNotesStore();
  const { agentWidth } = useShellLayout();
  const [q, setQ] = useState("");
  const emptyNotes = n.list.length === 0;
  if (emptyNotes) {
    return (
      <div
        style={{
          width: agentWidth,
          flexShrink: 0,
          padding: tokens.space.md,
          color: tokens.colors.onSurfaceVariant,
          background: tokens.colors.surfaceContainerHigh,
          borderLeft: `1px solid ${tokens.colors.outlineVariant}`,
          height: "100vh",
          boxSizing: "border-box",
        }}
      >
        Создайте заметки, чтобы задавать вопросы. Сначала создайте заметки, затем спросите меня
        о них.
      </div>
    );
  }
  return (
    <div
      style={{
        width: agentWidth,
        flexShrink: 0,
        borderLeft: `1px solid ${tokens.colors.outlineVariant}`,
        display: "flex",
        flexDirection: "column",
        height: "100vh",
        background: tokens.colors.surfaceContainerHigh,
        boxSizing: "border-box",
      }}
    >
      <div
        style={{
          display: "flex",
          justifyContent: "flex-end",
          alignItems: "center",
          padding: "8px 8px 0",
          flexShrink: 0,
        }}
      >
        {onRequestClose ? (
          <button
            type="button"
            onClick={onRequestClose}
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
            }}
            aria-label="Скрыть панель агента"
          >
            Скрыть агента
          </button>
        ) : null}
      </div>
      <div
        style={{
          flex: 1,
          overflow: "auto",
          padding: `0 ${tokens.space.sm}px ${tokens.space.sm}px`,
          minHeight: 0,
        }}
      >
        {a.error && <p style={{ color: tokens.colors.error }}>{a.error}</p>}
        {a.messages.map((m, i) => (
          <AgentMessage key={i} role={m.role} content={m.content} />
        ))}
        {a.loading && <div style={{ color: tokens.colors.onSurfaceVariant }}>…</div>}
      </div>
      <form
        style={{
          padding: 12,
          display: "flex",
          gap: tokens.space.sm,
          alignItems: "center",
          background: tokens.colors.surfaceContainer,
          flexShrink: 0,
          borderTop: `1px solid ${tokens.colors.outlineVariant}`,
        }}
        onSubmit={(e) => {
          e.preventDefault();
          if (!q.trim()) return;
          void a.ask(q);
          setQ("");
        }}
      >
        <input
          aria-label="Вопрос агенту"
          placeholder="Вопрос агенту"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{
            flex: 1,
            minWidth: 0,
            height: 48,
            padding: "0 12px",
            background: tokens.colors.surfaceContainerHighest,
            color: tokens.colors.onSurface,
            border: `1px solid ${tokens.colors.outline}`,
            borderRadius: tokens.radius.xs,
            fontFamily: "inherit",
            fontSize: 14,
            outline: "none",
          }}
        />
        <Button type="submit" variant="filledAccent">
          Спросить
        </Button>
      </form>
    </div>
  );
}
