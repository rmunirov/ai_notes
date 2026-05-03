import { tokens } from "../../theme/tokens";

export function AgentMessage({
  role,
  content,
}: {
  role: "user" | "assistant";
  content: string;
}) {
  const isUser = role === "user";
  return (
    <div
      style={{
        display: "flex",
        justifyContent: isUser ? "flex-start" : "flex-start",
        marginBottom: 12,
      }}
    >
      <div
        style={{
          maxWidth: "92%",
          padding: 8,
          borderRadius: isUser ? 16 : 0,
          background: isUser ? tokens.colors.primaryContainer : "transparent",
          color: isUser ? tokens.colors.onPrimaryContainer : tokens.colors.onSurfaceVariant,
          whiteSpace: "pre-wrap" as const,
          fontSize: 14,
          lineHeight: 1.45,
        }}
      >
        {content}
      </div>
    </div>
  );
}
