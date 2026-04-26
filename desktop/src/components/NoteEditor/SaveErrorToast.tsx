import { tokens } from "../../theme/tokens";
import { Button } from "../common/Button";

export function SaveErrorToast({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div
      style={{
        position: "fixed",
        bottom: 24,
        right: 24,
        background: tokens.colors.surfaceContainerHigh,
        border: `1px solid ${tokens.colors.error}`,
        color: tokens.colors.onSurface,
        padding: 12,
        borderRadius: tokens.radius.sm,
        maxWidth: 400,
        zIndex: 1000,
      }}
    >
      <p style={{ margin: 0, marginBottom: 8 }}>{message}</p>
      <Button variant="filledTonal" onClick={onRetry}>
        Повторить
      </Button>
    </div>
  );
}
