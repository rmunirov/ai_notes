import { createContext, useContext, useEffect, useState, type ReactNode } from "react";
import { tokens } from "../theme/tokens";

export type ShellLayout = {
  sidebarWidth: number;
  agentWidth: number;
};

const defaultLayout: ShellLayout = {
  sidebarWidth: tokens.layout.sidebarWidth,
  agentWidth: tokens.layout.agentWidth,
};

function computeLayout(viewportWidth: number): ShellLayout {
  if (viewportWidth < 880) {
    return { sidebarWidth: 200, agentWidth: 260 };
  }
  if (viewportWidth < 1040) {
    return { sidebarWidth: 240, agentWidth: 300 };
  }
  if (viewportWidth < 1200) {
    return { sidebarWidth: 260, agentWidth: 320 };
  }
  return { sidebarWidth: tokens.layout.sidebarWidth, agentWidth: tokens.layout.agentWidth };
}

const ShellLayoutContext = createContext<ShellLayout>(defaultLayout);

export function ShellLayoutProvider({ children }: { children: ReactNode }) {
  const [layout, setLayout] = useState<ShellLayout>(() =>
    typeof window === "undefined" ? defaultLayout : computeLayout(window.innerWidth),
  );

  useEffect(() => {
    const onResize = () => setLayout(computeLayout(window.innerWidth));
    onResize();
    window.addEventListener("resize", onResize);
    return () => window.removeEventListener("resize", onResize);
  }, []);

  return <ShellLayoutContext.Provider value={layout}>{children}</ShellLayoutContext.Provider>;
}

export function useShellLayout(): ShellLayout {
  return useContext(ShellLayoutContext);
}
