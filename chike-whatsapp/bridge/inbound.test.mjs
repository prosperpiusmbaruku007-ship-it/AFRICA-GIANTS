import test from "node:test";
import assert from "node:assert/strict";
import { pathToFileURL } from "node:url";
import path from "node:path";

// INBOUND_PATH lets tests/test_bridge_inbound.py run THIS file against a deliberately broken copy (a plant): every test below must be able to fail.
const mod = await import(process.env.INBOUND_PATH ? pathToFileURL(path.resolve(process.env.INBOUND_PATH)).href : "./inbound.mjs");
const { extractInbound, wantsReceiptWait } = mod;

test("a plain message gives its text and no quoted id", () => {
  assert.deepEqual(extractInbound({ conversation: "Habari" }), { text: "Habari", quotedId: "" });
});

test("a quoted reply gives its text AND the id of the message it quotes", () => {
  const m = { extendedTextMessage: { text: "TUMA", contextInfo: { stanzaId: "3EB0ABCDEF", participant: "x@s.whatsapp.net" } } };
  assert.deepEqual(extractInbound(m), { text: "TUMA", quotedId: "3EB0ABCDEF" });
});

test("an extended text message that quotes nothing has no quoted id", () => {
  assert.deepEqual(extractInbound({ extendedTextMessage: { text: "TUMA" } }), { text: "TUMA", quotedId: "" });
  assert.deepEqual(extractInbound({ extendedTextMessage: { text: "TUMA", contextInfo: {} } }), { text: "TUMA", quotedId: "" });
});

test("a quoted id that is not a string is ignored, never coerced", () => {
  for (const bad of [123, null, {}, ["a"], true]) {
    assert.equal(extractInbound({ extendedTextMessage: { text: "TUMA", contextInfo: { stanzaId: bad } } }).quotedId, "");
  }
});

test("the text rule is the old one: conversation wins over extended text, and a message with neither has no text", () => {
  assert.equal(extractInbound({ conversation: "A", extendedTextMessage: { text: "B" } }).text, "A");
  assert.equal(extractInbound({ imageMessage: {} }).text, "");
});

test("a missing message never throws", () => {
  assert.deepEqual(extractInbound(null), { text: "", quotedId: "" });
  assert.deepEqual(extractInbound(undefined), { text: "", quotedId: "" });
});

test("a send waits for the receipt unless wait_receipt is EXACTLY false", () => {
  assert.equal(wantsReceiptWait({ wait_receipt: false }), false);
  for (const p of [undefined, null, {}, { wait_receipt: true }, { wait_receipt: "false" }, { wait_receipt: 0 }, { wait_receipt: null }, { to: "x", text: "y" }]) {
    assert.equal(wantsReceiptWait(p), true, JSON.stringify(p));
  }
});
