/** Placeholder: use window.confirm; replace with native dialog if needed. */
export function useConfirm() {
  return (message: string) => globalThis.confirm(message);
}
