import { Component, type ErrorInfo, type ReactNode } from "react";
import { tokens } from "../theme/tokens";

export class ErrorBoundary extends Component<{ children: ReactNode; label: string }, { err: Error | null }> {
  state = { err: null as Error | null };
  static getDerivedStateFromError(err: Error) {
    return { err };
  }
  override componentDidCatch(e: Error, i: ErrorInfo) {
    console.error(i, e);
  }
  override render() {
    if (this.state.err) {
      return (
        <div style={{ color: tokens.colors.error, padding: 16 }}>{this.props.label}: {this.state.err.message}</div>
      );
    }
    return this.props.children;
  }
}
