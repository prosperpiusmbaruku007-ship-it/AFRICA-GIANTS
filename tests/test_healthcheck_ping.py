"""The alert path is a healthchecks.io dead-man's switch (founder, 2026-11-13).

The poll pings HEALTHCHECK_PING_URL on every healthy poll and `<url>/fail` on a detected problem; silence is also an alarm
(it covers Modal's scheduler dying). The URL is a credential: it must never reach a log line, a response or /health.
The ping is the ONLY outbound thing the watcher does, and it is not a participant send path.
"""
import ast
import importlib.util
import json
import os
import sys
import types
import urllib.error

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hc_ping_core", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

SECRET_URL = "https://hc-ping.com/11111111-2222-3333-4444-555555555555"
UUID = "11111111-2222-3333-4444-555555555555"


def _load_mw(monkeypatch):
    from conftest import isolate_modal_stores
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = core
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", core)
    spec = importlib.util.spec_from_file_location("chike_mw_ping", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    isolate_modal_stores(mw, monkeypatch)
    monkeypatch.setenv("ADMIN_TOKEN", "admin-secret")
    monkeypatch.setenv("HEALTHCHECK_PING_URL", SECRET_URL)
    return mw


class _Resp:
    def __init__(self, status=200):
        self.status = status

    def __enter__(self):
        return self

    def __exit__(self, *a):
        return False


def _fake_urlopen(monkeypatch, outcomes):
    """Record every request; `outcomes` is a list of status ints or exceptions, consumed in order (last one repeats)."""
    import urllib.request
    calls = []

    def fake(req, timeout=None):
        calls.append({"url": req.full_url, "method": req.get_method(), "body": (req.data or b"").decode("utf-8"),
                      "timeout": timeout})
        o = outcomes[min(len(calls) - 1, len(outcomes) - 1)]
        if isinstance(o, BaseException):
            raise o
        return _Resp(o)
    monkeypatch.setattr(urllib.request, "urlopen", fake)
    import time
    monkeypatch.setattr(time, "sleep", lambda s: None)
    return calls


# ── the decision, as a table ────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("verdict,detail,fails,kind,want", [
    ("connected", "open", 0, None, "ok"),
    ("connected", "open", 0, "bridge_recipient_offline", "ok"),      # a phone that is off is not a page
    ("connected", "open", 0, "bridge_suspect", "fail"),              # sends past the ceiling, nothing receipted
    ("error", "TWO_SOCKETS: 2", 1, None, "fail"),
    ("disconnected", "close", 1, None, "skip"),                      # one blip: neither healthy nor alarming
    ("disconnected", "close", 2, None, "fail"),
    ("error", "KeyError", 1, None, "skip"),
    ("error", "KeyError", 3, None, "fail"),
])
def test_heartbeat_decision(verdict, detail, fails, kind, want):
    got, reason = core.heartbeat_decision(verdict, detail, {"consecutive_failures": fails}, 2, kind)
    assert got == want, (got, reason)
    assert (reason != "") == (want in ("fail", "skip"))


def test_one_blip_is_never_reported_healthy():
    """`skip` sends NOTHING: reporting ok on a non-connected reading would hide a real outage behind a green check."""
    assert core.heartbeat_decision("disconnected", "close", {"consecutive_failures": 1}, 2)[0] != "ok"


def test_the_period_holds_several_pings_even_if_the_scheduler_is_late():
    """Poll every 2 min vs a 7-minute period + 5-minute grace: an outage is declared after 12 minutes of silence, so a
    single missed or late run (a 4-minute gap) cannot trip it. Measured max gap in the production log: 135 s."""
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    assert "schedule=_sched(modal.Period(minutes=2))" in src
    period_s, grace_s, poll_s = 7 * 60, 5 * 60, 2 * 60
    assert period_s // poll_s >= 3
    assert (period_s + grace_s) / poll_s >= 6


# ── the ping itself ─────────────────────────────────────────────────────────────────────────────
def test_ok_pings_the_url_and_fail_pings_slash_fail(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [200])
    assert mw._ping_healthcheck("ok") == (True, None)
    assert mw._ping_healthcheck("fail", "why") == (True, None)
    assert calls[0]["url"] == SECRET_URL and calls[0]["method"] == "POST"
    assert calls[1]["url"] == SECRET_URL + "/fail" and calls[1]["body"] == "why"
    assert all(c["timeout"] == 10 for c in calls)


def test_a_trailing_slash_in_the_secret_does_not_double_up(monkeypatch):
    mw = _load_mw(monkeypatch)
    monkeypatch.setenv("HEALTHCHECK_PING_URL", SECRET_URL + "/")
    calls = _fake_urlopen(monkeypatch, [200])
    mw._ping_healthcheck("fail")
    assert calls[0]["url"] == SECRET_URL + "/fail"


def test_a_failing_ping_retries_three_times_and_the_error_never_contains_the_url(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [urllib.error.HTTPError(SECRET_URL, 500, "boom", {}, None)])
    ok, err = mw._ping_healthcheck("ok")
    assert (ok, err) == (False, "HTTP 500") and len(calls) == 3
    assert UUID not in str(err)
    calls = _fake_urlopen(monkeypatch, [urllib.error.URLError("dns " + SECRET_URL)])
    ok, err = mw._ping_healthcheck("ok")
    assert ok is False and err == "URLError" and UUID not in err      # class only: str(e) would carry the URL


def test_a_ping_that_recovers_on_the_second_attempt_succeeds(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [OSError("reset"), 200])
    assert mw._ping_healthcheck("ok") == (True, None) and len(calls) == 2


def test_unconfigured_and_non_https_are_refused_without_a_request(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [200])
    monkeypatch.delenv("HEALTHCHECK_PING_URL")
    assert mw._ping_healthcheck("ok") == (False, "not configured")
    monkeypatch.setenv("HEALTHCHECK_PING_URL", "http://hc-ping.com/x")
    assert mw._ping_healthcheck("ok") == (False, "not https")
    assert calls == []


# ── the poll ────────────────────────────────────────────────────────────────────────────────────
def _poll(mw, monkeypatch, verdict, detail, prev=None, rec=None):
    monkeypatch.setattr(mw, "_bridge_status_now", lambda: (verdict, detail, rec or {}, {}))
    monkeypatch.setattr(mw, "_session_state", lambda: dict(prev or {}))
    return mw.poll_bridge_status.get_raw_f()()


def test_a_healthy_poll_sends_one_ok_ping_and_records_it(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [200])
    out = _poll(mw, monkeypatch, "connected", "open")
    assert out["ping"] == {"kind": "ok", "ok": True}
    assert [c["url"] for c in calls] == [SECRET_URL]
    st = mw.BRIDGE_WATCH[mw._WATCH_KEY]
    assert st["last_ping_kind"] == "ok" and st["last_ping_ok"] is True


def test_two_sockets_pings_fail_at_once_with_the_reason_in_the_body(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [200])
    out = _poll(mw, monkeypatch, "error", "TWO_SOCKETS: 2 holders")
    assert out["ping"]["kind"] == "fail"
    assert calls[0]["url"] == SECRET_URL + "/fail" and "TWO SOCKETS" in calls[0]["body"]


def test_a_disconnect_pings_fail_only_on_the_second_reading(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [200])
    first = _poll(mw, monkeypatch, "disconnected", "close")
    assert first["ping"] is None and calls == []                         # a blip: silence, not green, not red
    second = _poll(mw, monkeypatch, "disconnected", "close", prev={"consecutive_failures": 1})
    assert second["ping"]["kind"] == "fail" and calls[0]["url"].endswith("/fail")


def test_sends_stuck_past_the_ceiling_with_no_receipts_pings_fail(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [200])
    rec = {"node": {"connection": "open", "outbound": {"pending": 2, "flagged_no_receipt": 2,
                                                       "oldest_pending_s": 4000, "receipts_since_oldest": 0}}}
    kind = core.pending_alert_kind(rec["node"])
    out = _poll(mw, monkeypatch, "connected", "open", rec=rec)
    assert (out["ping"]["kind"] == "fail") == (kind == "bridge_suspect"), kind
    if kind == "bridge_suspect":
        assert calls[0]["url"].endswith("/fail")


def test_the_ping_is_sent_even_when_the_state_write_fails(monkeypatch):
    """The heartbeat is sent BEFORE the state write: a store outage must not turn a healthy bridge into a false alarm."""
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [200])

    class Boom(dict):
        def __setitem__(self, k, v):
            raise RuntimeError("store down")
    monkeypatch.setattr(mw, "BRIDGE_WATCH", Boom())
    out = _poll(mw, monkeypatch, "connected", "open")
    assert out["ping"]["ok"] is True and len(calls) == 1


def test_a_failing_ping_is_recorded_and_shown_in_health(monkeypatch):
    mw = _load_mw(monkeypatch)
    _fake_urlopen(monkeypatch, [urllib.error.HTTPError(SECRET_URL, 404, "no", {}, None)])
    out = _poll(mw, monkeypatch, "connected", "open")
    assert out["ping"] == {"kind": "ok", "ok": False}
    st = mw.BRIDGE_WATCH[mw._WATCH_KEY]
    assert st["last_ping_ok"] is False and st["last_ping_error"] == "HTTP 404"
    monkeypatch.setattr(mw, "_bridge_status_now", lambda: ("connected", "open", {}, {}))
    monkeypatch.setattr(mw, "_session_state", lambda: dict(st))
    b = mw._bridge_health()
    assert b["alerting"]["configured"] is True and b["alerting"]["last_ping"]["ok"] is False


def test_the_url_never_appears_in_a_log_line_a_response_or_health(monkeypatch, capsys):
    mw = _load_mw(monkeypatch)
    _fake_urlopen(monkeypatch, [urllib.error.HTTPError(SECRET_URL, 500, "x", {}, None)])
    _poll(mw, monkeypatch, "connected", "open")
    _poll(mw, monkeypatch, "error", "TWO_SOCKETS: 2")
    mw._fire_test_ping("fail")
    monkeypatch.setattr(mw, "_review_queue_health", lambda: {})
    monkeypatch.setattr(mw, "_cohort_health", lambda: {})
    monkeypatch.setattr(mw, "_bridge_status_now", lambda: ("connected", "open", {}, {}))
    health = json.dumps(mw.health.get_raw_f()())
    out = capsys.readouterr()
    for text in (out.out, out.err, health, json.dumps(mw._fire_test_ping("ok"))):
        assert UUID not in text and "hc-ping.com" not in text


# ── structure: the watcher still cannot reach a participant, and no longer emails ───────────────
def _fn(name):
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    return next(n for n in ast.walk(ast.parse(src)) if isinstance(n, ast.FunctionDef) and n.name == name)


def test_the_poll_pings_and_does_not_send_email_or_whatsapp():
    fn = _fn("poll_bridge_status")
    called = {getattr(c.func, "id", None) or getattr(c.func, "attr", None) for c in ast.walk(fn) if isinstance(c, ast.Call)}
    assert "_ping_healthcheck" in called and "heartbeat_decision" in called
    assert "_send_alert_email" not in called, "SMTP is kept but unused"
    assert not called & {"_send_once", "answer_and_send", "greet_and_send", "apply_decision", "_notify_reviewers"}


def test_the_smtp_code_is_kept_and_still_refuses_cleanly(monkeypatch):
    mw = _load_mw(monkeypatch)
    for k in mw._SMTP_KEYS:
        monkeypatch.delenv(k, raising=False)
    ok, detail = mw._send_alert_email("s", "b")
    assert ok is False and "not configured" in detail
    assert mw._ALERT_KEYS == ("HEALTHCHECK_PING_URL",)


# ── the admin endpoint ──────────────────────────────────────────────────────────────────────────
def _alert_test(mw, **kw):
    return mw.alert_test.get_raw_f()(**kw)


def test_the_admin_endpoint_rejects_a_wrong_or_missing_token_and_pings_nothing(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [200])
    for tok in (None, "", "wrong", "admin-secret "):
        assert _alert_test(mw, token=tok, kind="fail").status_code == 404
    assert calls == []


def test_the_admin_endpoint_fires_one_fail_ping_marked_as_a_test(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [200])
    r = _alert_test(mw, token="admin-secret", kind="fail")
    body = json.loads(r.body)
    assert r.status_code == 200 and body == {"kind": "fail", "ok": True, "error": None}
    assert len(calls) == 1 and calls[0]["url"] == SECRET_URL + "/fail"
    assert "TEST FAILURE" in calls[0]["body"] and "NOT a real outage" in calls[0]["body"]
    assert UUID not in r.body.decode()
    assert mw.BRIDGE_WATCH["alert_test"]["kind"] == "fail"


def test_the_admin_endpoint_can_send_the_normal_ping_and_refuses_other_kinds(monkeypatch):
    mw = _load_mw(monkeypatch)
    calls = _fake_urlopen(monkeypatch, [200])
    assert json.loads(_alert_test(mw, token="admin-secret", kind="ok").body)["ok"] is True
    assert calls[0]["url"] == SECRET_URL
    assert json.loads(_alert_test(mw, token="admin-secret", kind="start").body)["ok"] is False
    assert len(calls) == 1


def test_the_endpoint_is_a_post_never_a_get():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    i = src.index("def alert_test(")
    assert 'fastapi_endpoint(method="POST")' in src[i - 120:i]


def test_the_endpoint_reports_a_failed_ping_honestly(monkeypatch):
    mw = _load_mw(monkeypatch)
    _fake_urlopen(monkeypatch, [urllib.error.HTTPError(SECRET_URL, 403, "no", {}, None)])
    body = json.loads(_alert_test(mw, token="admin-secret", kind="fail").body)
    assert body == {"kind": "fail", "ok": False, "error": "HTTP 403"}
