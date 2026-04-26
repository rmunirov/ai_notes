import React from "react";
import ReactDOM from "react-dom/client";
import { App } from "./App";
import { initTauri } from "./api/tauri";
import "./index.css";

async function boot() {
  try {
    const t = await import("@tauri-apps/api/core");
    initTauri(t.invoke);
  } catch {
    initTauri(null);
  }
  ReactDOM.createRoot(document.getElementById("root")!).render(
    <React.StrictMode>
      <App />
    </React.StrictMode>
  );
}

void boot();
