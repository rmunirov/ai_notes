import { tokens } from "../../theme/tokens";

export type ButtonVariant = "filledAccent" | "filledTonal" | "outlined" | "text";

type Props = React.ButtonHTMLAttributes<HTMLButtonElement> & {
  variant?: ButtonVariant;
};

const base: React.CSSProperties = {
  fontFamily: "inherit",
  fontSize: 14,
  fontWeight: 500,
  lineHeight: "20px",
  minHeight: 40,
  padding: "10px 24px",
  borderRadius: tokens.radius.pill,
  cursor: "pointer",
  boxSizing: "border-box",
};

const variants: Record<ButtonVariant, React.CSSProperties> = {
  filledAccent: {
    background: tokens.colors.primary,
    color: tokens.colors.onPrimary,
    border: "none",
  },
  filledTonal: {
    background: tokens.colors.primaryContainer,
    color: tokens.colors.onPrimaryContainer,
    border: "none",
  },
  outlined: {
    background: "transparent",
    color: tokens.colors.primary,
    border: `1px solid ${tokens.colors.outline}`,
  },
  text: {
    background: "transparent",
    color: tokens.colors.primary,
    border: "none",
    minHeight: 36,
    padding: "10px 12px",
  },
};

export function Button({ variant = "filledAccent", style, type = "button", ...props }: Props) {
  return (
    <button
      type={type}
      {...props}
      style={{
        ...base,
        ...variants[variant],
        ...(props.disabled
          ? { opacity: 0.38, cursor: "not-allowed" }
          : {}),
        ...style,
      }}
    />
  );
}
