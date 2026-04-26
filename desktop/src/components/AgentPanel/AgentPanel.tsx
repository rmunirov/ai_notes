import { useState } from "react";
import { useAgentStore } from "../../store/agentStore";
import { useNotesStore } from "../../store/notesStore";
import { tokens } from "../../theme/tokens";
import { AgentMessage } from "./AgentMessage";
import { Button } from "../common/Button";

export function AgentPanel() {
  const a = useAgentStore();
  const n = useNotesStore();
  const [q, setQ] = useState("");
  const emptyNotes = n.list.length === 0;
  if (emptyNotes) {
    return (
      <div style={{ padding: 16, color: tokens.colors.textMuted, maxWidth: 400 }}>
        Создайте заметки, чтобы задавать вопросы. Сначала создайте заметки, затем спросите меня
        о них.
      </div>
    );
  }
  return (
    <div
      style={{
        width: 360,
        borderLeft: `1px solid ${tokens.colors.border}`,
        display: "flex",
        flexDirection: "column",
        height: "100vh",
      }}
    >
      <div style={{ flex: 1, overflow: "auto", padding: 8 }}>
        {a.error && <p style={{ color: tokens.colors.error }}>{a.error}</p>}
        {a.messages.map((m, i) => (
          <AgentMessage key={i} role={m.role} content={m.content} />
        ))}
        {a.loading && <div>…</div>}
      </div>
      <form
        style={{ padding: 8, display: "flex", gap: 8 }}
        onSubmit={(e) => {
          e.preventDefault();
          if (!q.trim()) return;
          void a.ask(q);
          setQ("");
        }}
      >
        <input
          aria-label="Вопрос агенту"
          value={q}
          onChange={(e) => setQ(e.target.value)}
          style={{ flex: 1, padding: 8, background: tokens.colors.surface, color: tokens.colors.text, border: `1px solid ${tokens.colors.border}` }}
        />
        <Button type="submit">Спросить</Button>
      </form>
    </div>
  );
}
