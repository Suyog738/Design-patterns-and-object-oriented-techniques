export type RealtimeHandler = (event: unknown) => void;

export const REALTIME_ENABLED = false;

export function subscribeToEvents(handler: RealtimeHandler): () => void {
  void handler; // not used until Phase 12
  return () => {};
}