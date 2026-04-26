import { tokens } from "../../theme/tokens";
import { Button } from "./Button";

type P = { title: string; hint: string; actionLabel: string; onAction: () => void };
export function EmptyState({ title, hint, actionLabel, onAction }: P) {
  return (
    <div style={{ padding: tokens.space.lg, textAlign: "center" as const }}>
      <h2 style={{ margin: 0 }}>{title}</h2>
      <p style={{ color: tokens.colors.textMuted }}>{hint}</p>
      <Button onClick={onAction}>{actionLabel}</Button>
    </div>
  );
}
