import { tokens } from "../../theme/tokens";

export function Button(props: React.ButtonHTMLAttributes<HTMLButtonElement>) {
  return (
    <button
      {...props}
      style={{
        padding: `${tokens.space.sm}px ${tokens.space.md}px`,
        background: tokens.colors.primary,
        color: "#fff",
        border: "none",
        borderRadius: 6,
        cursor: "pointer",
        ...((props.style as object) ?? {}),
      }}
    />
  );
}
