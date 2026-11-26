# -*- coding: utf-8 -*-
"""SEND CEILINGS (2026-11-26, after the reminder storm). Every outbound goes through `_send_once`, which asks the ceiling gate first.

Plants (R26): each must FAIL against the 2026-11-13 behaviour, which had no ceiling at all -- the 21st send to one number and the 61st overall
both went out. Each limb has a positive control (the 20th / 60th passes) so a gate that blocks everything cannot pass.
"""
import asyncio
import importlib.util
import os
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


@pytest.fixture
def mw(monkeypatch):
    from conftest import isolate_modal_stores
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = core
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", core)
    spec = importlib.util.spec_from_file_location("chike_mw_ceiling", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    isolate_modal_stores(m, monkeypatch)
    monkeypatch.setenv("SENDER_SALT", "s")
    monkeypatch.setenv("SEND_CAP_PER_RECIPIENT_PER_HOUR", "20")
    monkeypatch.setenv("SEND_CAP_GLOBAL_PER_HOUR", "60")
    m.transport_calls = []

    async def raw(to, text):
        m.transport_calls.append(to)
        return True, None
    monkeypatch.setattr(m, "TRANSPORT", "bridge")
    monkeypatch.setattr(m, "_send_once_bridge", raw)
    m.alerts = []
    monkeypatch.setattr(m, "_ping_healthcheck", lambda kind, body="", url_env="HEALTHCHECK_PING_URL": (m.alerts.append((kind, body)) or (True, None)))
    return m


def _send(m, to, n=1):
    return [_run(m._send_once(to, "x")) for _ in range(n)]


def test_per_recipient_cap_trips_at_21_and_the_20th_still_goes(mw):
    res = _send(mw, "+255700000001", 21)
    assert all(ok for ok, _ in res[:20]), "positive control: 20 sends are allowed"
    assert res[20][0] is False and "ceiling" in res[20][1]
    assert len(mw.transport_calls) == 20, "the 21st never reached the transport"


def test_global_cap_trips_at_61_across_recipients(mw):
    res = [_run(mw._send_once(f"+2557000{i:05d}", "x")) for i in range(61)]
    assert all(ok for ok, _ in res[:60]), "positive control: 60 sends to 60 different people are allowed"
    assert res[60][0] is False and len(mw.transport_calls) == 60


def test_a_refused_send_does_not_keep_the_window_full(mw):
    _send(mw, "+255700000001", 21)
    ledger = [k for k in mw.SEND_CEILING if not str(k).startswith("alert:")]
    assert len(ledger) == 20, "the refused 21st reservation is removed, so retries cannot pin the window"


def test_fail_closed_when_the_ledger_cannot_be_written(mw, monkeypatch):
    class Broken(dict):
        def __setitem__(self, k, v):
            raise RuntimeError("modal down")
    monkeypatch.setattr(mw, "SEND_CEILING", Broken())
    ok, why = _run(mw._send_once("+255700000001", "x"))
    assert ok is False and "fail-closed" in why and mw.transport_calls == []


def test_warning_at_50_percent_and_alert_at_the_cap_each_once_per_hour(mw):
    _send(mw, "+255700000001", 9)
    assert mw.alerts == [], "9/20 is below 50%"
    _send(mw, "+255700000001", 1)
    assert len(mw.alerts) == 1 and "WARNING" in mw.alerts[0][1] and mw.alerts[0][0] == "fail"
    _send(mw, "+255700000001", 5)
    assert len(mw.alerts) == 1, "one warning per hour, not one per send"
    _send(mw, "+255700000001", 6)           # sends 16..21 -> 21st refused
    assert any("CAP" in b for _, b in mw.alerts) and sum("CAP" in b for _, b in mw.alerts) == 1
    assert "255700000001" not in " ".join(b for _, b in mw.alerts), "an alert never carries a number"


def test_the_ledger_holds_no_phone_numbers(mw):
    _send(mw, "+255700000001", 2)
    assert "255700000001" not in " ".join(map(str, mw.SEND_CEILING.keys()))


def test_old_reservations_age_out_of_the_window():
    now = 10_000_000.0
    tag = "aaaa"
    old = [core.send_ceiling_key(now - 3601, tag, str(i)) for i in range(50)]
    new = [core.send_ceiling_key(now, tag, "n")]
    d = core.send_ceiling_decision(old + new, tag, now, per_recipient=20, global_cap=60)
    assert d["allowed"] and d["recipient_n"] == 1


def test_a_mistyped_cap_cannot_switch_a_ceiling_off():
    assert core.parse_send_caps("0", "-5") == (20, 150)
    assert core.parse_send_caps("junk", None) == (20, 150)
    assert core.parse_send_caps("5", "7") == (5, 7)


def test_every_outbound_path_goes_through_the_gate():
    """_send_once is the only caller of the raw transports (a new direct call to a transport would bypass the ceiling)."""
    import ast
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    tree = ast.parse(src)
    callers = {}
    for f in ast.walk(tree):
        if isinstance(f, (ast.FunctionDef, ast.AsyncFunctionDef)):
            for c in ast.walk(f):
                if isinstance(c, ast.Call):
                    n = getattr(c.func, "id", None) or getattr(c.func, "attr", None)
                    if n in ("_send_once_bridge", "_send_once_wappfly"):
                        callers.setdefault(n, set()).add(f.name)
    assert callers == {"_send_once_bridge": {"_send_once"}, "_send_once_wappfly": {"_send_once"}}, callers
    gate = next(f for f in ast.walk(tree) if isinstance(f, ast.AsyncFunctionDef) and f.name == "_send_once")
    assert any(getattr(c.func, "id", None) == "_ceiling_gate" for c in ast.walk(gate) if isinstance(c, ast.Call))
