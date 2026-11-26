// Outbound pacing for the bridge: a MINIMUM GAP plus RANDOM JITTER between consecutive sends (item G, 2026-11-26).
// The send ceilings in modal_whatsapp.py stay the HARD brake; this only stops the unofficial session emitting a
// machine-regular burst (several acks, a digest and reviewer pushes landing in the same second).
//
// Slots are reserved SYNCHRONOUSLY (no await between reading and writing nextFree), so concurrent requests cannot
// both take the same slot. Sends are therefore spaced by >= minGapMs even when they arrive together.
//
// ⛔ THE WAIT IS BOUNDED, AND THE BOUND IS NOT A TUNING CHOICE. The Python client times out at 35 s and the bridge may
// already wait up to 20 s for a receipt, so a send queued for longer than ~10 s would make the client report an
// AMBIGUOUS timeout (PENDING_RECEIPT, never retried) for a message that WAS sent. Past the bound the request is refused
// BEFORE anything is sent (429 pacing_backlog): a clean, retryable failure, never a phantom "pending".
export const DEFAULTS = { minGapMs: 1000, jitterMs: 2000, maxWaitMs: 10000 };
const FLOOR_GAP_MS = 250;        // a mistyped tunable can never switch pacing off (same rule as the send ceilings)
const CEIL_WAIT_MS = 12000;      // and can never exceed the client budget

// An unset or blank value is the DEFAULT, not 0 (Number("") is 0: an unset PACE_MAX_WAIT_MS would otherwise refuse every queued send).
function num(v, d) { const s = String(v ?? "").trim(); if (!s) return d; const n = Number(s); return Number.isFinite(n) ? n : d; }

export function pacerConfig(env = {}) {
  const gap = num(env.PACE_MIN_GAP_MS, DEFAULTS.minGapMs);
  const jit = num(env.PACE_JITTER_MS, DEFAULTS.jitterMs);
  const wait = num(env.PACE_MAX_WAIT_MS, DEFAULTS.maxWaitMs);
  return {
    minGapMs: gap >= FLOOR_GAP_MS ? gap : DEFAULTS.minGapMs,
    jitterMs: jit >= 0 ? jit : DEFAULTS.jitterMs,
    maxWaitMs: wait >= 0 ? Math.min(wait, CEIL_WAIT_MS) : DEFAULTS.maxWaitMs,
  };
}

export function createPacer({ minGapMs, jitterMs, maxWaitMs, now = Date.now, rand = Math.random,
                              sleep = (ms) => new Promise((r) => setTimeout(r, ms)) }) {
  let nextFree = 0;
  const stats = { slots: 0, delayed: 0, refused: 0, max_wait_ms: 0 };
  return {
    async acquire() {
      const t = now();
      const start = Math.max(t, nextFree);
      const wait = start - t;
      if (wait > maxWaitMs) { stats.refused++; return { ok: false, retry_after_ms: wait - maxWaitMs }; }
      nextFree = start + minGapMs + Math.floor(rand() * (jitterMs + 1));
      stats.slots++;
      if (wait > 0) { stats.delayed++; stats.max_wait_ms = Math.max(stats.max_wait_ms, wait); await sleep(wait); }
      return { ok: true, waited_ms: wait };
    },
    stats() { return { ...stats, minGapMs, jitterMs, maxWaitMs }; },
  };
}
