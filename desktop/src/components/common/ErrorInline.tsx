import { tokens } from "../../theme/tokens";
import { Button } from "./Button";

export function ErrorInline({ message, onRetry }: { message: string; onRetry: () => void }) {
  return (
    <div
      style={{
        color: tokens.colors.error,
        padding: tokens.space.md,
        background: tokens.colors.surfaceContainer,
      }}
    >
      {message}
      <Button variant="filledTonal" onClick={onRetry} style={{ marginLeft: 8 }}>
        Повторить
      </Button>
    </div>
  );
}
