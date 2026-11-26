import test from "node:test";
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import path from "node:path";

// PACER_PATH lets tests/test_bridge_pacing.py run THIS file against a deliberately broken copy (a plant): every test
// below must be able to fail.
const mod = await import(process.env.PACER_PATH ? pathToFileURL(path.resolve(process.env.PACER_PATH)).href : "./pacer.mjs");
const { createPacer, pacerConfig, DEFAULTS } = mod;

function clock() {   // fake time that does NOT advance during a synchronous burst: "all arrive in the same instant" really is the same instant
  let t = 0;
  return { now: () => t, sleep: async () => {}, advance: (ms) => { t += ms; } };
}

test("concurrent sends are spaced by at least the minimum gap", async () => {
  const c = clock(); const p = createPacer({ minGapMs: 1000, jitterMs: 0, maxWaitMs: 60000, now: c.now, sleep: c.sleep, rand: () => 0 });
  const got = await Promise.all([1, 2, 3, 4, 5].map(() => p.acquire()));   // all five arrive at t=0; send time = waited_ms
  const s = got.map((r) => { assert.equal(r.ok, true); return r.waited_ms; }).sort((x, y) => x - y);
  assert.deepEqual(s, [0, 1000, 2000, 3000, 4000]);
  for (let i = 1; i < s.length; i++) assert.ok(s[i] - s[i - 1] >= 1000, `gap ${s[i] - s[i - 1]} < 1000`);
});

test("jitter is added on top of the gap and stays inside [gap, gap+jitter]", async () => {
  const c = clock(); const rs = [0, 0.999, 0]; let i = 0;
  const p = createPacer({ minGapMs: 1000, jitterMs: 2000, maxWaitMs: 60000, now: c.now, sleep: c.sleep, rand: () => rs[i++] });
  const t = (await Promise.all([p.acquire(), p.acquire(), p.acquire()])).map((r) => r.waited_ms);
  assert.equal(t[1] - t[0], 1000);                              // first reservation drew jitter 0
  assert.equal(t[2] - t[1], 1000 + Math.floor(0.999 * 2001));   // second drew 0.999: the gap after it is longer
  assert.ok(t[2] - t[1] > 1000 && t[2] - t[1] <= 3000);
});

test("an idle bridge sends immediately: no delay when nothing is queued", async () => {
  const c = clock(); const p = createPacer({ minGapMs: 1000, jitterMs: 0, maxWaitMs: 10000, now: c.now, sleep: c.sleep, rand: () => 0 });
  const a = await p.acquire(); c.advance(5000); const b = await p.acquire();
  assert.equal(a.waited_ms, 0); assert.equal(b.waited_ms, 0);
});

test("a send that would wait past the bound is REFUSED before anything is sent, and takes no slot", async () => {
  const c = clock(); const p = createPacer({ minGapMs: 1000, jitterMs: 0, maxWaitMs: 2500, now: c.now, sleep: c.sleep, rand: () => 0 });
  const got = await Promise.all([1, 2, 3, 4, 5, 6].map(() => p.acquire()));
  assert.equal(got.filter((x) => x.ok).length, 3);              // waits 0, 1000, 2000 pass; 3000+ exceed 2500
  assert.equal(got.filter((x) => !x.ok).length, 3);
  assert.ok(got.find((x) => !x.ok).retry_after_ms > 0);
  assert.equal(p.stats().refused, 3);
  c.advance(10000); assert.equal((await p.acquire()).ok, true); // a refusal consumed no slot: the queue drains
});

test("config: a mistyped or zero gap cannot switch pacing off; the wait bound cannot exceed the client budget", () => {
  assert.equal(pacerConfig({ PACE_MIN_GAP_MS: "0" }).minGapMs, DEFAULTS.minGapMs);
  assert.equal(pacerConfig({ PACE_MIN_GAP_MS: "abc" }).minGapMs, DEFAULTS.minGapMs);
  assert.equal(pacerConfig({ PACE_MAX_WAIT_MS: "999999" }).maxWaitMs, 12000);
  assert.equal(pacerConfig({ PACE_MIN_GAP_MS: "1500" }).minGapMs, 1500);   // positive control: a valid value is honoured
  assert.deepEqual(pacerConfig({}), DEFAULTS);
});
