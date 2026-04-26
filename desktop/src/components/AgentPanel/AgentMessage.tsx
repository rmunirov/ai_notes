import { tokens } from "../../theme/tokens";

export function AgentMessage({
  role,
  content,
}: {
  role: "user" | "assistant";
  content: string;
}) {
  return (
    <div
      style={{
        textAlign: role === "user" ? "right" : "left",
        margin: 8,
        padding: 8,
        background: role === "user" ? tokens.colors.surface : "transparent",
        borderRadius: 6,
        whiteSpace: "pre-wrap" as const,
      }}
    >
      {content}
    </div>
  );
}
