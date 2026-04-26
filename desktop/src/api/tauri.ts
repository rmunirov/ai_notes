type Invoker = (cmd: string, args?: Record<string, unknown>) => Promise<unknown>;

let invoker: Invoker | null = null;

export function initTauri(i: Invoker | null) {
  invoker = i;
}

export function getInvoker(): Invoker | null {
  return invoker;
}
