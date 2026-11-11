import test from "node:test";
import assert from "node:assert/strict";
import { useKvAuthState } from "./authstate.mjs";

function mockKv(initial = {}) {
  const d = new Map(Object.entries(initial)); const calls = { all: 0, setMany: 0, delMany: 0 };
  return { d, calls, fail: false,
    all: async () => { calls.all++; return Object.fromEntries(d); },
    setMany: async (items) => { calls.setMany++; if (this?.fail) throw new Error("x"); for (const [k, v] of Object.entries(items)) d.set(k, v); },
    delMany: async (keys) => { calls.delMany++; keys.forEach((k) => d.delete(k)); } };
}

test("800 pre-keys commit in ONE write call, not 800", async () => {
  const kv = mockKv(); const { state } = await useKvAuthState(kv);
  const pre = {}; for (let i = 0; i < 800; i++) pre[i] = { private: Buffer.from("a"), public: Buffer.from("b") };
  await state.keys.set({ "pre-key": pre });
  assert.equal(kv.calls.setMany, 1); assert.equal(kv.d.size, 800);
});

test("survives a restart: a new instance reads back exactly what was written", async () => {
  const kv = mockKv(); const a = await useKvAuthState(kv);
  await a.saveCreds();
  await a.state.keys.set({ session: { "x@s.whatsapp.net": Buffer.from("secret-bytes") } });
  const b = await useKvAuthState(kv);                        // the "new container"
  assert.equal(b.state.creds.registrationId, a.state.creds.registrationId);
  const got = await b.state.keys.get("session", ["x@s.whatsapp.net"]);
  assert.equal(Buffer.from(got["x@s.whatsapp.net"]).toString(), "secret-bytes");
});

test("null deletes, and a missing key reads as null without a network call", async () => {
  const kv = mockKv(); const { state } = await useKvAuthState(kv);
  await state.keys.set({ "pre-key": { 1: { a: 1 } } });
  await state.keys.set({ "pre-key": { 1: null } });
  assert.equal(kv.d.size, 0); assert.equal(kv.calls.delMany, 1);
  assert.deepEqual(await state.keys.get("pre-key", [1, 2]), { 1: null, 2: null });
  assert.equal(kv.calls.all, 1);
});

test("a failed durable write leaves the cache untouched (never ahead of the Dict)", async () => {
  const kv = mockKv(); const { state, _cache } = await useKvAuthState(kv);
  kv.setMany = async () => { throw new Error("dict down"); };
  await assert.rejects(state.keys.set({ "pre-key": { 1: { a: 1 } } }));
  assert.equal(_cache.size, 0);
});
