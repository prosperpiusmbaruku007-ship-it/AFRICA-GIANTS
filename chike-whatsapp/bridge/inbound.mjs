// Inbound extraction + send options for the bridge (founder amendment, 2026-11-28: reply-to-approve).
//
// A reviewer approves a draft by REPLYING "TUMA" to its card, quoting it. WhatsApp delivers a quoted reply as an `extendedTextMessage`
// whose `contextInfo.stanzaId` is the id of the message it quotes. Until now the bridge forwarded only the text and DROPPED that id, so a reply to a
// card was indistinguishable from any other message. This module is pure (no sockets, no I/O) so it can be tested, and mutation-tested, like the pacer.
//
// The text rule is deliberately UNCHANGED from what server.mjs did inline before (`conversation`, else `extendedTextMessage.text`): this change must not
// admit or drop any message that was previously admitted or dropped. It only ADDS the quoted id.
export function extractInbound(message) {
  const m = message || {};
  const text = m.conversation || m.extendedTextMessage?.text || "";
  const q = m.extendedTextMessage?.contextInfo?.stanzaId;
  return { text, quotedId: typeof q === "string" ? q : "" };
}

// `wait_receipt` is honoured ONLY when it is exactly `false`. Anything else (missing, true, "false", 0, null) keeps the old behaviour of waiting for the delivery
// receipt, so a mistyped or absent hint can never change what a participant send does.
export function wantsReceiptWait(payload) {
  return !(payload && payload.wait_receipt === false);
}
