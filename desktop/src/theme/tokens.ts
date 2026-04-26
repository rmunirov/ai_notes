/** Material 3 dark baseline — синхронизировано с макетом Figma (AI Notes). */
export const tokens = {
  colors: {
    surface: "#1c1b1f",
    surfaceContainer: "#211f26",
    surfaceContainerHigh: "#2b2930",
    surfaceContainerHighest: "#36343b",
    onSurface: "#f5f3f7",
    onSurfaceBright: "#fffcff",
    onSurfaceVariant: "#c7c2d0",
    primary: "#d0bcff",
    onPrimary: "#381e72",
    primaryContainer: "#4f378b",
    onPrimaryContainer: "#eaddff",
    outline: "#948f99",
    outlineVariant: "#49454f",
    error: "#f2b8b5",
    onError: "#601410",
    /** Совместимость со старыми именами */
    bg: "#1c1b1f",
    border: "#49454f",
    text: "#f5f3f7",
    textMuted: "#c7c2d0",
  },
  radius: { xs: 4, sm: 12, md: 16, pill: 20 },
  space: { sm: 8, md: 16, lg: 24 },
  layout: { sidebarWidth: 280, agentWidth: 360 },
} as const;
