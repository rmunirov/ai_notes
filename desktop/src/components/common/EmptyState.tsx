import { tokens } from "../../theme/tokens";
import { Button } from "./Button";

type P = { title: string; hint: string; actionLabel: string; onAction: () => void };
export function EmptyState({ title, hint, actionLabel, onAction }: P) {
  return (
    <div style={{ padding: tokens.space.lg, textAlign: "center" as const }}>
      <h2 style={{ margin: 0, color: tokens.colors.onSurface, fontSize: 22, fontWeight: 500 }}>
        {title}
      </h2>
      <p style={{ color: tokens.colors.onSurfaceVariant, margin: "12px 0 20px" }}>{hint}</p>
      <Button variant="filledTonal" onClick={onAction}>
        {actionLabel}
      </Button>
    </div>
  );
}
