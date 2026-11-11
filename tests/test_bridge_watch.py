"""The bridge transport seam: delivery-receipt sends, never-resent pending, the watcher, /health.

The old failure was trusting ACCEPTANCE. Here ok means a delivery receipt; accepted-but-not-
receipted is its own state that is never retried (a resend could duplicate) and never followed by
a fallback, and a ceiling in the bridge flags it so pending cannot become the new silent loss.
"""
import ast
import asyncio
import importlib.util
import json
import os

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "chike_handler_core_bw", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)
T = 1_000_000.0


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _load_mw(monkeypatch=None):
    import sys
    import types
    if monkeypatch is not None:
        pkg = types.ModuleType("chike_whatsapp")
        pkg.handler_core = core
        monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
        monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", core)
    spec = importlib.util.spec_from_file_location(
        "chike_modal_whatsapp_bw", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    return mw


# -- send result: ok ONLY on a delivery receipt ------------------------------------------
def test_only_a_delivery_receipt_is_ok():
    assert core.bridge_send_result(200, {"ok": True, "status": "delivered"}) == (True, None)


def test_accepted_without_receipt_is_pending_not_ok_and_not_a_plain_failure():
    ok, detail = core.bridge_send_result(200, {"ok": False, "pending": True, "id": "X1",
                                               "status": "server_ack"})
    assert ok is False and core.is_pending_receipt(detail)
    assert core.send_state(ok, detail) == "pending_receipt"


@pytest.mark.parametrize("code,body", [(503, {"error": "not_connected", "connection": "close"}),
                                       (401, {}), (400, {"error": "bad_request"}),
                                       (502, {"error": "send_threw"}), (200, None), (200, {})])
def test_everything_else_is_a_retryable_failure_never_pending(code, body):
    ok, detail = core.bridge_send_result(code, body)
    assert ok is False and not core.is_pending_receipt(detail)
    assert core.send_state(ok, detail) == "failed"


class _S:
    send_attempts = 3
    send_retry_delay_s = 0
    secrets = ()


def test_a_pending_send_is_never_retried_so_it_cannot_duplicate():
    calls = []

    async def send_once(to, text):
        calls.append(text)
        return False, f"{core.PENDING_RECEIPT}: id=A status=server_ack"
    ok, detail = _run(core.send_with_retry(send_once, "255@s.whatsapp.net", "hi", _S()))
    assert len(calls) == 1 and ok is False and core.is_pending_receipt(detail)


def test_a_plain_failure_is_still_retried():
    calls = []

    async def send_once(to, text):
        calls.append(1)
        return False, "bridge not connected (close)"
    _run(core.send_with_retry(send_once, "255@s.whatsapp.net", "hi", _S()))
    assert len(calls) == 3


def test_a_pending_answer_is_not_followed_by_a_fallback_message():
    """A pending answer must produce exactly one send: no retry, no FALLBACK on top."""
    sent = []

    async def send_once(to, text):
        sent.append(text)
        return False, f"{core.PENDING_RECEIPT}: id=A status=server_ack"

    class St(_S):
        supervised = False
        slow_ack_after_s = 0
        second_ack_after_s = 0
        model_timeout_s = 5
        cold_start_suspected_s = 30
        sender_salt = ""
        supervised_ack = ""

    async def ask(q):
        return {"reply": "Jibu"}
    row = _run(core.deliver("255700000001@s.whatsapp.net", "swali", ask, send_once, St(), "t"))
    assert sent == ["Jibu"], sent
    assert row["send_state"] == "pending_receipt" and row["send_ok"] is False
    assert row["reply_address_kind"] == "phone"


# -- the reply address is explicit in the record -----------------------------------------
def test_reply_address_kind():
    assert core.reply_address_kind("255700000001@s.whatsapp.net") == "phone"
    assert core.reply_address_kind("92686082166995@lid") == "lid"
    assert core.reply_address_kind("x@g.us") == "other"


def test_lid_sender_resolved_to_phone_is_recorded_as_phone():
    p = core.parse_webhook({"event": "messages.received", "data": {"messages": {
        "conversation": "hi", "key": {"remoteJid": "9@lid", "fromMe": False,
                                      "senderPn": "255700000001@s.whatsapp.net"}}}})
    assert core.reply_address_kind(p["sender"]) == "phone" and p["sender_lid"] == "9@lid"


# -- the bridge verdict ------------------------------------------------------------------
def _rec(conn="open", holding=True, age=5):
    return {"ts": T - age, "holding_lease": holding, "build": "x",
            "node": {"connection": conn, "last_event": "open"}}


def _alive(*holding):
    return {f"alive:{i}": {"ts": T - 3, "holding": h} for i, h in enumerate(holding)}


def test_connected_needs_every_condition():
    assert core.bridge_verdict(_rec(), _alive(True), T)[0] == "connected"
    assert core.bridge_verdict(_rec(conn="close"), _alive(True), T)[0] == "disconnected"
    assert core.bridge_verdict(_rec(conn="qr"), _alive(True), T)[0] == "disconnected"
    assert core.bridge_verdict(_rec(holding=False), _alive(False), T)[0] == "disconnected"
    assert core.bridge_verdict(_rec(age=300), _alive(True), T)[0] == "error"
    assert core.bridge_verdict(None, {}, T)[0] == "error"
    assert core.bridge_verdict({"ts": T}, {}, T)[0] == "error"


def test_logged_out_says_it_needs_a_qr():
    v, d = core.bridge_verdict(_rec(conn="logged_out"), _alive(True), T)
    assert v == "disconnected" and "QR" in d


def test_two_lease_holders_are_two_sockets_but_two_containers_are_not():
    v, d = core.bridge_verdict(_rec(), _alive(True, True), T)
    assert v == "error" and d.startswith("TWO_SOCKETS")
    assert core.bridge_verdict(_rec(), _alive(True, False), T)[0] == "connected", \
        "an idle container during a deploy overlap holds no socket"
    stale = {"alive:0": {"ts": T - 3, "holding": True},
             "alive:old": {"ts": T - 200, "holding": True}}
    assert core.bridge_verdict(_rec(), stale, T)[0] == "connected", "a dead container's heartbeat"


def test_two_sockets_alerts_on_the_first_reading_but_a_blip_does_not():
    st, ev = core.advance_session_health({}, "error", "TWO_SOCKETS: 2", T, fail_threshold=1)
    assert ev == ["down"]
    st, ev = core.advance_session_health({}, "disconnected", "close", T)
    assert ev == []


# -- the pending ceiling -----------------------------------------------------------------
def test_pending_alert_fires_once_per_interval_and_never_when_nothing_is_flagged():
    assert core.pending_alert_due(None, 0, T) is False
    assert core.pending_alert_due(None, 2, T) is True
    assert core.pending_alert_due(T - 60, 2, T) is False
    assert core.pending_alert_due(T - 3700, 2, T) is True


def test_the_bridge_ledger_flags_past_the_ceiling_and_survives_restarts():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "bridge", "server.mjs"),
               encoding="utf-8").read()
    assert "flagged_no_receipt" in src and "PENDING_FLAG_S" in src
    assert "kv.ledgerAll()" in src and "kv.ledgerPut" in src, "ledger must be persisted"


# -- structural: the watcher cannot reach a participant (same rule as the sweeper) -------
def _fn(name):
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"),
               encoding="utf-8").read()
    fn = next((n for n in ast.walk(ast.parse(src))
               if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name), None)
    assert fn is not None, f"{name} renamed -- re-point this test"
    return fn


@pytest.mark.parametrize("name", ["poll_bridge_status", "_bridge_status_now",
                                  "_send_alert_email", "_bridge_health"])
def test_the_watcher_has_no_whatsapp_send_path_and_no_queue_access(name):
    fn = _fn(name)
    called = {getattr(c.func, "id", None) or getattr(c.func, "attr", None)
              for c in ast.walk(fn) if isinstance(c, ast.Call)}
    names = {n.id for n in ast.walk(fn) if isinstance(n, ast.Name)}
    for forbidden in ("_send_once", "_send_once_bridge", "answer_and_send", "greet_and_send",
                      "apply_decision", "_notify_reviewers"):
        assert forbidden not in called, f"{name} calls {forbidden}"
    assert "REVIEW_QUEUE" not in names and "ChikeModel" not in names
    subs = {n.slice.value for n in ast.walk(fn) if isinstance(n, ast.Subscript)
            and isinstance(n.slice, ast.Constant) and isinstance(n.slice.value, str)}
    assert not subs & {"sender", "final", "draft"}


def test_the_bridge_status_read_never_writes_the_bridge_dicts():
    fn = _fn("_bridge_status_now")
    attrs = {c.func.attr for c in ast.walk(fn) if isinstance(c, ast.Call)
             and isinstance(c.func, ast.Attribute)}
    assert not attrs & {"put", "pop", "update", "clear", "post", "delete"}
    assert not [n for n in ast.walk(fn) if isinstance(n, ast.Assign)
                and any(isinstance(t, ast.Subscript) for t in n.targets)]


def test_poll_is_scheduled_every_two_minutes():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"),
               encoding="utf-8").read()
    assert "schedule=modal.Period(minutes=2)" in src


# -- /health -----------------------------------------------------------------------------
def test_health_reports_the_bridges_own_state(monkeypatch):
    mw = _load_mw(monkeypatch)
    rec = {"ts": 0, "holding_lease": True, "build": "b", "lease": {"holder": "c1"},
           "node": {"connection": "open", "last_event": "open", "disconnects_24h": 0,
                    "since_inbound_s": 12, "since_receipt_s": 3,
                    "outbound": {"pending": 1, "flagged_no_receipt": 1,
                                 "oldest_pending_s": 900}}}
    monkeypatch.setattr(mw, "_bridge_status_now", lambda: (
        "connected", "open", rec, {"alive:c1": {"ts": 1e12, "holding": True}}))
    monkeypatch.setattr(mw, "_session_state", lambda: {})
    monkeypatch.setattr(mw, "_review_queue_health", lambda: {})   # these two reach Modal's network
    monkeypatch.setattr(mw, "_cohort_health", lambda: {})
    for k in mw._ALERT_KEYS:
        monkeypatch.delenv(k, raising=False)
    b = mw.health.get_raw_f()()["bridge"]
    assert b["session_status"] == "connected" and b["lease_holder"] == "c1"
    assert b["lease_holders"] == 1 and b["containers_alive"] == 1
    assert b["pending"]["flagged_no_receipt"] == 1
    assert b["alerting"]["configured"] is False
    monkeypatch.setenv("ALERT_SMTP_PASS", "hunter2-secret-value")
    monkeypatch.setenv("BRIDGE_SEND_TOKEN", "bridge-send-token-value")
    out = json.dumps(mw.health.get_raw_f()())
    assert "hunter2-secret-value" not in out and "bridge-send-token-value" not in out


def test_a_failing_health_section_degrades_to_error_not_connected(monkeypatch):
    mw = _load_mw()            # no alias: _core() fails here, exactly the failure to survive
    monkeypatch.setattr(mw, "_bridge_status_now", lambda: ("connected", "open", {}, {}))
    assert mw._bridge_health()["session_status"] == "error"


def test_alert_email_refuses_cleanly_when_unconfigured(monkeypatch):
    mw = _load_mw()
    for k in mw._ALERT_KEYS:
        monkeypatch.delenv(k, raising=False)
    ok, detail = mw._send_alert_email("s", "b")
    assert ok is False and "not configured" in detail


# -- the transport: unreachable is retryable, an ambiguous response is not ---------------
def test_transport_classification(monkeypatch):
    import httpx
    mw = _load_mw(monkeypatch)
    monkeypatch.setenv("BRIDGE_SEND_TOKEN", "t")

    def run(exc=None, resp=None):
        class C:
            def __init__(self, **kw):
                pass

            async def __aenter__(self):
                return self

            async def __aexit__(self, *a):
                return False

            async def post(self, *a, **k):
                if exc:
                    raise exc
                return resp
        monkeypatch.setattr(httpx, "AsyncClient", C)
        return _run(mw._send_once_bridge("1", "x"))

    ok, d = run(exc=httpx.ConnectError("no"))
    assert not ok and not core.is_pending_receipt(d), "never reached the bridge: retryable"
    ok, d = run(exc=httpx.ReadTimeout("slow"))
    assert not ok and core.is_pending_receipt(d), "may have been sent: never resend"

    class R:
        status_code = 200

        def json(self):
            return {"ok": True, "status": "delivered"}
    assert run(resp=R()) == (True, None)


def test_the_real_bridge_send_over_real_http(monkeypatch):
    """The transport against a real local HTTP server speaking the bridge's responses: a receipt
    is ok, accepted-without-receipt is PENDING (never retried), not-connected is retryable, and
    the bearer token is actually sent."""
    import threading
    from http.server import BaseHTTPRequestHandler, HTTPServer
    seen = {}
    mode = {"m": "delivered"}

    class H(BaseHTTPRequestHandler):
        def log_message(self, *a):
            pass

        def do_POST(self):
            seen["auth"] = self.headers.get("authorization")
            body = json.loads(self.rfile.read(int(self.headers["content-length"])))
            seen["body"] = body
            code, out = {
                "delivered": (200, {"ok": True, "id": "A", "status": "delivered"}),
                "pending": (200, {"ok": False, "id": "A", "status": "server_ack", "pending": True}),
                "down": (503, {"ok": False, "error": "not_connected", "connection": "close"}),
            }[mode["m"]]
            raw = json.dumps(out).encode()
            self.send_response(code)
            self.send_header("content-length", str(len(raw)))
            self.end_headers()
            self.wfile.write(raw)
    srv = HTTPServer(("127.0.0.1", 0), H)
    threading.Thread(target=srv.serve_forever, daemon=True).start()
    try:
        mw = _load_mw(monkeypatch)
        monkeypatch.setattr(mw, "BRIDGE_URL", f"http://127.0.0.1:{srv.server_port}")
        monkeypatch.setenv("BRIDGE_SEND_TOKEN", "tok123")
        to = "255700000001@s.whatsapp.net"
        assert _run(mw._send_once_bridge(to, "jibu")) == (True, None)
        assert seen["auth"] == "Bearer tok123" and seen["body"] == {"to": to, "text": "jibu"}
        mode["m"] = "pending"
        ok, d = _run(mw._send_once_bridge(to, "jibu"))
        assert not ok and core.is_pending_receipt(d)
        mode["m"] = "down"
        ok, d = _run(mw._send_once_bridge(to, "jibu"))
        assert not ok and not core.is_pending_receipt(d) and "not connected" in d
    finally:
        srv.shutdown()
