// CHIKE WhatsApp bridge: Baileys <-> the existing webhook handler.
//
// Inbound  : messages.upsert -> POST WEBHOOK_URL in the SAME shape Wappfly used, so
//            handler_core.parse_webhook and everything behind it are unchanged.
// Outbound : POST /send {to,text} -> acknowledged ONLY on WhatsApp's delivery receipt.
// State    : every field of /state is set from the library's own events, never inferred.
import http from "node:http";
import QRCode from "qrcode";
import { makeKv, useKvAuthState } from "./authstate.mjs";
import pino from "pino";
import makeWASocket, {
  DisconnectReason, fetchLatestBaileysVersion, Browsers,
} from "@whiskeysockets/baileys";

const PORT = Number(process.env.PORT || 8080);
// Auth state lives in a Modal Dict, reached through the Python supervisor on localhost. NOT a
// Volume: Volumes need explicit commits, so a preemption could lose recent key updates.
const KV = process.env.KV_URL || "http://127.0.0.1:8081";
const CTL_TOKEN = process.env.CTL_TOKEN || "";
const ADMIN_TOKEN = process.env.BRIDGE_ADMIN_TOKEN || "";
const SEND_TOKEN = process.env.BRIDGE_SEND_TOKEN || "";
const WEBHOOK_URL = process.env.WEBHOOK_URL || "";
const RECEIPT_WAIT_MS = Number(process.env.RECEIPT_WAIT_MS || 20000);
// The ceiling is how long a send may wait for its delivery receipt before it is FLAGGED.
// Measured 2026-11-11, five sends to a recipient who confirmed receiving every one: receipt lags of
// 3s, 7s, 10s, 178s and 1298s (21.6 minutes). So 10 minutes cried wolf at the first sample, and
// 30 minutes would have cleared the longest by a narrow margin. 60 minutes sits ~2.8x above the
// observed maximum; /state reports the live lag distribution (median, max, count) so this is a
// number to revisit against data, not to guess.
const PENDING_FLAG_S = Number(process.env.PENDING_FLAG_S || 3600);
// Baileys 7.0.0-rc14 is a RELEASE CANDIDATE, pinned exactly in package.json. WhatsApp changes its
// protocol without notice, so the library can break underneath us; /state shows the library's own
// disconnect reasons so that shows up as an alert rather than as silence.
const log = pino({ level: process.env.LOG_LEVEL || "warn" });

const now = () => Math.floor(Date.now() / 1000);
const S = {
  connection: "starting",          // starting | connecting | qr | open | close | logged_out
  last_event: null, last_event_ts: null,
  last_disconnect: null,           // {code, name, ts}
  disconnects: [],                 // unix ts of every close, for the "more than 3/day" criterion
  reconnect_attempts: 0, next_reconnect_ts: null,
  connected_since_ts: null,
  last_inbound_ts: null, last_outbound_ts: null, last_receipt_ts: null,
  qr: null, qr_ts: null, me: null, started_ts: now(),
};
const LEDGER = new Map();          // id -> {to, ts, status, receipt_ts}
const STATUS = { 2: "server_ack", 3: "delivered", 4: "read", 5: "read" };
let sock = null;
let stopping = false;

function ev(name) { S.last_event = name; S.last_event_ts = now(); }
function codeName(code) {
  return Object.entries(DisconnectReason).find(([, v]) => v === code)?.[0] || String(code);
}

const kv = makeKv(KV, CTL_TOKEN);

let connecting = false;
async function start() {
  if (connecting) return; connecting = true;
  const { state, saveCreds } = await useKvAuthState(kv);
  // The send ledger survives restarts: a message accepted just before a restart must still be
  // watched for its receipt and flagged, or "pending" becomes a silent loss.
  try {
    for (const [id, row] of Object.entries(await kv.ledgerAll())) {
      if (now() - row.ts > 86400) { kv.ledgerDel(id).catch(() => {}); continue; }
      if (!LEDGER.has(id)) LEDGER.set(id, row);
    }
  } catch (e) { ev("ledger_load_error"); log.error(e); }
  const { version } = await fetchLatestBaileysVersion();
  S.connection = "connecting"; ev("connecting");
  sock = makeWASocket({
    version, auth: state, logger: log, browser: Browsers.ubuntu("Chike"),
    markOnlineOnConnect: false, syncFullHistory: false,
  });
  sock.ev.on("creds.update", saveCreds);

  sock.ev.on("connection.update", (u) => {
    if (u.qr) { S.qr = u.qr; S.qr_ts = now(); S.connection = "qr"; ev("qr"); }
    if (u.connection === "open") {
      S.connection = "open"; S.qr = null; S.reconnect_attempts = 0;
      S.next_reconnect_ts = null; S.connected_since_ts = now();
      S.me = sock.user?.id || null; ev("open");
    }
    if (u.connection === "close") {
      const code = u.lastDisconnect?.error?.output?.statusCode;
      S.last_disconnect = { code: code ?? null, name: codeName(code), ts: now() };
      // Only a close of a PAIRED session counts toward the "disconnects per day" revisit criterion:
      // QR-timeout closes before the scan are not lost connections.
      if (S.me) { S.disconnects.push(now()); S.disconnects = S.disconnects.filter((t) => t > now() - 86400); }
      S.connected_since_ts = null; ev("close:" + codeName(code));
      if (stopping) return;
      if (code === DisconnectReason.loggedOut) {
        S.connection = "logged_out";   // needs a new QR scan; reconnecting cannot help
        return;
      }
      S.connection = "close";
      // 440 = another socket took the session. Reconnecting at once starts a fight, so wait.
      const base = code === DisconnectReason.connectionReplaced ? 60 : 2;
      const wait = Math.min(120, base * 2 ** Math.min(S.reconnect_attempts, 5))
        + Math.floor(Math.random() * 3);
      S.reconnect_attempts += 1; S.next_reconnect_ts = now() + wait;
      connecting = false;
      setTimeout(() => start().catch((e) => { connecting = false; ev("start_error"); S.connection = "close"; log.error(e); }),
        wait * 1000);
    }
  });

  sock.ev.on("messages.upsert", async ({ messages, type }) => {
    if (type !== "notify") return;
    for (const m of messages) {
      if (!m.message || m.key.fromMe) continue;
      const text = m.message.conversation || m.message.extendedTextMessage?.text || "";
      S.last_inbound_ts = now();
      if (!text || !WEBHOOK_URL) continue;
      // Baileys v7 puts the phone JID in remoteJidAlt when remoteJid is a linked-ID; hand it
      // over in the field parse_webhook already reads, so replies go to the phone.
      const key = { remoteJid: m.key.remoteJid, fromMe: false, id: m.key.id };
      const alt = m.key.remoteJidAlt || m.key.participantAlt;
      if (alt) key.senderPn = alt;
      const body = { event: "messages.received",
        data: { messages: { key, conversation: text, messageTimestamp: m.messageTimestamp,
                            pushName: m.pushName } } };
      try {
        const r = await fetch(WEBHOOK_URL, { method: "POST",
          headers: { "content-type": "application/json" }, body: JSON.stringify(body) });
        if (!r.ok) { ev("webhook_http_" + r.status); }
      } catch (e) { ev("webhook_error"); log.error(e); }
    }
  });

  // The delivery receipt. status 2 = accepted by WhatsApp's server; 3 = reached the device.
  sock.ev.on("messages.update", (updates) => {
    for (const { key, update } of updates) {
      const row = LEDGER.get(key.id);
      if (!row || update.status == null) continue;
      const name = STATUS[update.status];
      if (!name) continue;
      if (update.status >= 3 && !row.receipt_ts) { row.receipt_ts = now(); S.last_receipt_ts = now(); }
      if (update.status > row.rank) { row.rank = update.status; row.status = name; kv.ledgerPut(key.id, row).catch(() => {}); }
    }
  });
}

function toJid(to) {
  if (to.includes("@")) return to;
  const d = to.replace(/\D/g, "");
  return d ? d + "@s.whatsapp.net" : "";
}

async function send({ to, text }) {
  if (S.connection !== "open" || !sock) return { code: 503, body: { ok: false, error: "not_connected", connection: S.connection } };
  const jid = toJid(String(to || ""));
  if (!jid || !text) return { code: 400, body: { ok: false, error: "bad_request" } };
  let sent;
  try { sent = await sock.sendMessage(jid, { text: String(text) }); }
  catch (e) { return { code: 502, body: { ok: false, error: "send_threw:" + (e?.message || e).toString().slice(0, 120) } }; }
  const id = sent?.key?.id;
  if (!id) return { code: 502, body: { ok: false, error: "no_message_id" } };
  S.last_outbound_ts = now();
  const row = { to: jid, ts: now(), status: "sent", rank: 1, receipt_ts: null };
  LEDGER.set(id, row);
  kv.ledgerPut(id, row).catch(() => {});
  const t0 = Date.now();
  while (Date.now() - t0 < RECEIPT_WAIT_MS && row.rank < 3) await new Promise((r) => setTimeout(r, 250));
  // ok is true ONLY on a delivery receipt. "server_ack" means WhatsApp took it, not that it arrived,
  // so it is reported as pending and the caller must NOT resend (that would duplicate).
  return { code: 200, body: { ok: row.rank >= 3, id, status: row.status, pending: row.rank < 3 } };
}

function ledgerSummary() {
  const t = now(); let pending = 0, oldest = 0, flagged = 0;
  for (const [id, r] of LEDGER) {
    if (t - r.ts > 86400) { LEDGER.delete(id); continue; }
    if (r.rank < 3) { pending++; oldest = Math.max(oldest, t - r.ts); if (t - r.ts > PENDING_FLAG_S) flagged++; }
  }
  const lags = [...LEDGER.values()].filter((r) => r.receipt_ts).map((r) => r.receipt_ts - r.ts).sort((a, b) => a - b);
  return { sent_24h: LEDGER.size, pending, oldest_pending_s: oldest, flagged_no_receipt: flagged,
           ceiling_s: PENDING_FLAG_S, receipts_24h: lags.length,
           receipt_lag_median_s: lags.length ? lags[Math.floor(lags.length / 2)] : null,
           receipt_lag_max_s: lags.length ? lags[lags.length - 1] : null };
}

function state() {
  const t = now();
  const ago = (x) => (x ? t - x : null);
  return {
    connection: S.connection, last_event: S.last_event, last_event_age_s: ago(S.last_event_ts),
    last_disconnect: S.last_disconnect, disconnects_24h: S.disconnects.length,
    reconnect_attempts: S.reconnect_attempts, connected_for_s: ago(S.connected_since_ts),
    since_inbound_s: ago(S.last_inbound_ts), since_outbound_s: ago(S.last_outbound_ts),
    since_receipt_s: ago(S.last_receipt_ts), uptime_s: t - S.started_ts,
    has_qr: !!S.qr, paired: !!S.me, outbound: ledgerSummary(),
  };
}

const json = (res, code, obj) => { res.writeHead(code, { "content-type": "application/json" }); res.end(JSON.stringify(obj)); };
const eq = (a, b) => a && b && a.length === b.length && Buffer.from(a).equals(Buffer.from(b));

const server = http.createServer(async (req, res) => {
  const u = new URL(req.url, "http://x");
  const admin = eq(u.searchParams.get("token") || "", ADMIN_TOKEN);
  if (u.pathname === "/healthz") return json(res, 200, { up: true });
  if (u.pathname === "/state") return admin ? json(res, 200, state()) : json(res, 401, { error: "unauthorized" });
  if (u.pathname === "/admin/qr") {
    if (!admin) return json(res, 401, { error: "unauthorized" });
    let body;
    if (S.qr) body = `<img src="${await QRCode.toDataURL(S.qr, { width: 360 })}"><p>Scan: WhatsApp &gt; Linked devices &gt; Link a device</p>`;
    else if (S.connection === "open") body = `<p><b>Connected</b> as ${S.me ? S.me.split(":")[0].split("@")[0].slice(-4).padStart(8, "*") : "?"}. Nothing to scan.</p>`;
    else body = `<p>State: ${S.connection}. Waiting for a QR... this page refreshes.</p>`;
    res.writeHead(200, { "content-type": "text/html", "cache-control": "no-store" });
    return res.end(`<!doctype html><meta name=viewport content="width=device-width"><meta http-equiv=refresh content=4><body style="font-family:sans-serif;text-align:center">${body}</body>`);
  }
  // Local control from the Python supervisor, which alone decides when the socket may open
  // (it holds the lease). Never reachable without the per-process token.
  if (u.pathname === "/_ctl/connect" && req.method === "POST") {
    if (!eq(req.headers["x-ctl"] || "", CTL_TOKEN)) return json(res, 401, { error: "unauthorized" });
    start().catch((e) => { connecting = false; S.connection = "close"; ev("start_error"); console.error(e); });
    return json(res, 200, { ok: true });
  }
  if (u.pathname === "/admin/reset" && req.method === "POST") {
    // Forget the login (after a logout, or to re-pair on a new SIM). Destructive, so explicit.
    if (!admin || u.searchParams.get("confirm") !== "yes") return json(res, 401, { error: "unauthorized_or_unconfirmed" });
    await kv.clear(); json(res, 200, { ok: true, note: "auth wiped; process exits and restarts unpaired" });
    return setTimeout(() => process.exit(0), 300);
  }
  if (u.pathname === "/send" && req.method === "POST") {
    const auth = (req.headers.authorization || "").replace(/^Bearer /, "");
    if (!eq(auth, SEND_TOKEN)) return json(res, 401, { error: "unauthorized" });
    let raw = ""; for await (const c of req) raw += c;
    let p; try { p = JSON.parse(raw); } catch { return json(res, 400, { error: "bad_json" }); }
    const r = await send(p); return json(res, r.code, r.body);
  }
  json(res, 404, { error: "not_found" });
});

if (!ADMIN_TOKEN || !SEND_TOKEN || !CTL_TOKEN) { console.error("BRIDGE_ADMIN_TOKEN, BRIDGE_SEND_TOKEN and CTL_TOKEN are required"); process.exit(2); }
// Listening is NOT connecting: the socket opens only when the supervisor says it holds the lease.
S.connection = "idle";
server.listen(PORT, "0.0.0.0", () => console.log("bridge listening", PORT));
for (const sig of ["SIGTERM", "SIGINT"]) process.on(sig, () => { stopping = true; try { sock?.end(); } catch {} setTimeout(() => process.exit(0), 1500); });
