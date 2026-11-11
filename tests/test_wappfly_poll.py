"""The Wappfly session watcher: pure state machine, structural limits, /health shape.

Status is a NECESSARY signal and never a sufficient one (the dashboard said "connected" through
an inbound outage on 2026-11-11), so nothing here claims forwarding works. What it does claim:
a dropped session is noticed in about 10 minutes, the alert goes by EMAIL (the watched channel
cannot carry its own alarm), and the watcher has no way to reach a participant.
"""
import ast
import importlib.util
import json
import os

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "chike_handler_core_poll", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
core = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(core)

T0 = 1_000_000.0
MIN = 60.0


def _load_mw(monkeypatch=None):
    import sys
    import types
    if monkeypatch is not None:        # in the container the app dir is /root/chike_whatsapp
        pkg = types.ModuleType("chike_whatsapp")
        pkg.handler_core = core
        monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
        monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", core)
    spec = importlib.util.spec_from_file_location(
        "chike_modal_whatsapp_poll", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    return mw


# ── the verdict: only an explicit connected is connected ───────────────────────────────
def test_only_an_explicit_200_connected_is_connected():
    assert core.wappfly_status_verdict(200, {"status": "connected"})[0] == "connected"
    assert core.wappfly_status_verdict(200, {"status": " Connected "})[0] == "connected"


@pytest.mark.parametrize("code,body", [
    (200, {"status": "disconnected"}), (200, {"status": "connecting"}),
    (200, {}), (200, None), (200, "ok"), (200, {"status": None}), (200, {"status": 1}),
    (401, {"status": "connected"}), (500, {"status": "connected"}), (404, None),
])
def test_everything_else_is_not_a_pass(code, body):
    assert core.wappfly_status_verdict(code, body)[0] != "connected"


# ── the state machine ───────────────────────────────────────────────────────────────────
def _run(readings, **kw):
    st, out = {}, []
    for i, v in enumerate(readings):
        st, ev = core.advance_session_health(st, v, v, T0 + i * 5 * MIN, **kw)
        out.append(ev)
    return st, out


def test_one_blip_does_not_alert_but_two_in_a_row_do():
    _, ev = _run(["connected", "error", "connected"])
    assert ev == [[], [], []], "a single failed read must not page anyone"
    _, ev = _run(["connected", "disconnected", "disconnected"])
    assert ev == [[], [], ["down"]]


def test_a_continuing_outage_alerts_once_then_repeats_only_after_the_interval():
    # 6h at a 5-minute cadence is 72 readings
    st, ev = _run(["disconnected"] * 80)
    flat = [e for step in ev for e in step]
    assert flat.count("down") == 1
    assert flat.count("still_down") == 1, flat
    assert ev[1] == ["down"]


def test_recovery_is_reported_only_if_the_outage_was():
    _, ev = _run(["disconnected", "connected"])
    assert ev[1] == [], "one failed read never alerted, so a recovery email would be noise"
    _, ev = _run(["disconnected", "disconnected", "connected", "connected"])
    assert ev[2] == ["recovered"] and ev[3] == []


def test_last_connected_time_survives_an_outage():
    st, _ = _run(["connected", "disconnected", "disconnected", "disconnected"])
    assert st["last_ok_ts"] == T0, "the number a human asks for: when did it last work"
    assert st["consecutive_failures"] == 3


def test_a_planted_dead_session_is_caught_where_a_clean_one_is_not():
    """R26: watch the control block the thing it exists to block, and pass a clean case."""
    _, dead = _run(["disconnected"] * 4)
    _, live = _run(["connected"] * 4)
    assert any(dead) and not any(live)


# ── the watcher's own heartbeat ────────────────────────────────────────────────────────
def test_poll_age_never_polled_or_old_is_stale():
    assert core.poll_age_verdict({}, T0)["stale"] is True
    assert core.poll_age_verdict(None, T0)["stale"] is True
    assert core.poll_age_verdict({"last_check_ts": T0}, T0 + 5 * MIN)["stale"] is False
    old = core.poll_age_verdict({"last_check_ts": T0}, T0 + 20 * MIN)
    assert old["stale"] is True and old["age_s"] == 1200
