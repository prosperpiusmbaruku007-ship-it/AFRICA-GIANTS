# -*- coding: utf-8 -*-
"""PRE-WARM ON GREETING (founder, 2026-11-28: minimise question-to-answer time for wave 1).

A greeting starts a GPU container (a cheap existing method is SPAWNED; no generation, no user content, output unused) while the first-contact message is being sent.

What must hold, each planted (R26): the greeting is never delayed or failed by it; it is idempotent (a recent model touch suppresses it); it is capped per sender and per hour
(atomic claims); it is OFF unless explicitly on; anything unparseable fails CLOSED (no warm-up, never 'unlimited'); and it sends nothing the participant wrote to the GPU app."""
import ast
import os
import sys
import threading
import time
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _load_mw as _load_mw_real, _run  # noqa: E402

SRC = os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py")


def S(i):
    return f"2557000001{i:02d}@s.whatsapp.net"


# ── the pure policy ─────────────────────────────────────────────────────────────────────────────────────────
def test_enabled_only_for_an_explicit_truthy_value_a_typo_or_missing_is_off():
    assert [core.parse_prewarm_enabled(v) for v in ("1", "true", "YES", " on ")] == [True] * 4
    assert [core.parse_prewarm_enabled(v) for v in (None, "", "0", "off", "tru", "enabled", "2")] == [False] * 7


def test_per_hour_zero_is_none_and_garbage_falls_back_to_the_cap_never_to_unlimited():
    assert core.parse_prewarm_per_hour("0") == 0
    assert core.parse_prewarm_per_hour("7") == 7
    for bad in (None, "", "many", "-3", "1.5x"):
        assert core.parse_prewarm_per_hour(bad) == core.PREWARM_PER_HOUR_DEFAULT


def test_cooldown_has_a_floor_and_garbage_falls_back():
    assert core.parse_prewarm_cooldown_s("600") == 600.0
    for bad in (None, "x", "30", "-1", "0"):
        assert core.parse_prewarm_cooldown_s(bad) == core.PREWARM_SENDER_COOLDOWN_DEFAULT_S


def test_skip_reason_boundaries_on_both_sides():
    now = 1_800_000_000.0
    assert core.prewarm_skip_reason(False, now, None) == "disabled"
    assert core.prewarm_skip_reason(True, now, now - 299) == "recently_warm"
    assert core.prewarm_skip_reason(True, now, now - 300) is None, "exactly 300 s is no longer recent"
    assert core.prewarm_skip_reason(True, now, None) is None
    assert core.prewarm_skip_reason(True, now, "??") is None, "an unreadable stamp must not suppress warming forever"
    assert core.prewarm_skip_reason(True, now, now + 500) is None, "a stamp from the future (clock quirk) is not 'recent'"


def test_keys_are_windowed_per_sender_and_slotted_per_hour():
    now = 1_800_000_000.0
    k1, slots = core.prewarm_keys("abc", now, 900, 3)
    k2, _ = core.prewarm_keys("abc", now + 899 - (now % 900), 900, 3)
    k3, _ = core.prewarm_keys("abc", now + 900, 900, 3)
    assert len(slots) == 3 and len(set(slots)) == 3
    assert core.prewarm_keys("abc", now, 900, 0)[1] == []
    assert k1 != k3, "a new window is a new key"
    assert k1.startswith("prewarm:s:abc:")


# ── through the REAL greeting handler ─────────────────────────────────────────────────────────────────────
@pytest.fixture
def mw(monkeypatch):
    m = _load_mw_real(monkeypatch)
    monkeypatch.delenv("DISCLOSURE", raising=False)
    monkeypatch.setenv("PREWARM_ENABLED", "1")
    monkeypatch.setenv("PREWARM_PER_HOUR", "12")
    monkeypatch.setenv("PREWARM_SENDER_COOLDOWN_S", "900")
    m.sent, m.model_calls, m.spawns = [], [], []

    async def fake_send(to, text):
        m.sent.append(text)
        return True, None
    monkeypatch.setattr(m, "_send_once", fake_send)

    class _Remote:
        @staticmethod
        async def aio(message):
            m.model_calls.append(message)
            return {"reply": "Ndiyo.", "working": "W", "facts": ["F"], "path": "engine:vat_registration"}

    class _Spawn:
        @staticmethod
        def spawn(*a, **k):
            m.spawns.append((a, k))

    class _Model:
        run = types.SimpleNamespace(remote=_Remote)
        served_index_identity = _Spawn
    monkeypatch.setattr(m, "ChikeModel", _Model)
    return m


def _greet(m, sender):
    return _run(m.greet_and_send.get_raw_f()(sender))


def _age_the_touch(m):
    m.BRIDGE_WATCH[m._PREWARM_TOUCH_KEY] = time.time() - 10_000


def test_a_greeting_spawns_exactly_one_warmup_with_no_arguments_and_no_model_call(mw):
    _greet(mw, S(1))
    assert len(mw.spawns) == 1
    assert mw.spawns[0] == ((), {}), "NOTHING the participant wrote (or anything else) is sent to the GPU app"
    assert mw.model_calls == [], "the warm-up is not an inference"
    assert mw.sent == [core.FIRST_CONTACT_TEXT], "and the greeting is the same one message as before"


def test_PLANT_the_greeting_is_not_delayed_by_a_slow_warmup(mw):
    """The spawn blocks (a slow network call). The first-contact message must be sent while it is STILL blocked: the warm-up runs in a thread, off the event loop."""
    started, release = threading.Event(), threading.Event()
    outcome = {}

    def slow_spawn(*a, **k):
        started.set()
        # The ONLY thing that can release this spawn is the test, and the test releases it only AFTER it has seen the greeting sent.
        # So `released_by_test` is True exactly when the greeting went out while the spawn was still blocked. If the warm-up ran on the event loop
        # (or the send waited for it) nothing could observe the greeting, the wait would time out, and this would be False.
        outcome["released_by_test"] = release.wait(timeout=3)
        mw.spawns.append(1)
    mw.ChikeModel.served_index_identity = types.SimpleNamespace(spawn=slow_spawn)

    async def go():
        import asyncio
        task = asyncio.ensure_future(mw.greet_and_send.get_raw_f()(S(2)))
        t0 = time.monotonic()
        while not mw.sent and time.monotonic() - t0 < 5:
            await asyncio.sleep(0.01)
        outcome["sent_seen"] = bool(mw.sent)
        release.set()
        await task
    _run(go())
    assert outcome.get("sent_seen") is True
    assert outcome.get("released_by_test") is True, "the greeting could not be sent while the warm-up was blocked: the warm-up is on the event loop"
    assert started.is_set() and mw.spawns == [1]


def test_a_failing_spawn_never_costs_the_greeting_and_leaves_its_row(mw):
    def boom(*a, **k):
        raise RuntimeError("modal unreachable")
    mw.ChikeModel.served_index_identity = types.SimpleNamespace(spawn=boom)
    out = _greet(mw, S(3))
    assert out["send_ok"] is True and mw.sent == [core.FIRST_CONTACT_TEXT]
    assert [r for r in mw.TRANSCRIPTS.values() if r.get("kind") == "greeting"], "the transcript row was still written"


def test_an_unreadable_or_unwritable_store_is_survived(mw, monkeypatch):
    class Broken(dict):
        def get(self, *a, **k):
            raise OSError("dict down")

        def put(self, *a, **k):
            raise OSError("dict down")

        def __setitem__(self, *a):
            raise OSError("dict down")
    monkeypatch.setattr(mw, "BRIDGE_WATCH", Broken())
    out = _greet(mw, S(4))
    assert out["send_ok"] is True and mw.sent == [core.FIRST_CONTACT_TEXT]
    assert mw.spawns == [], "a store that cannot record the claim does not warm (fail closed: no uncounted spend)"


def test_idempotent_a_recent_model_touch_means_no_warmup(mw):
    mw.BRIDGE_WATCH[mw._PREWARM_TOUCH_KEY] = time.time() - 60
    _greet(mw, S(5))
    assert mw.spawns == []


def test_a_real_question_stamps_the_container_as_warm_so_the_next_greeting_skips(mw):
    _run(mw.answer_and_send.get_raw_f()(S(6), "Mshahara wa TZS 800,000, PAYE ni kiasi gani?"))
    assert mw.model_calls, "setup: the model really was called"
    assert time.time() - float(mw.BRIDGE_WATCH[mw._PREWARM_TOUCH_KEY]) < 30
    assert mw.spawns == [], "answering a question never spawns a warm-up"
    _greet(mw, S(7))
    assert mw.spawns == [], "and a greeting seconds after a real question finds it warm"


def test_the_warmup_itself_stamps_so_a_second_greeting_seconds_later_does_not_double_spawn(mw):
    _greet(mw, S(8))
    _greet(mw, S(9))
    assert len(mw.spawns) == 1, "a warm-up is already in flight: a different sender seconds later must not start another"


def test_per_sender_cooldown(mw):
    _greet(mw, S(10))
    _age_the_touch(mw)                               # isolate the cooldown from the idempotence check
    _greet(mw, S(10))
    assert len(mw.spawns) == 1, "the same sender inside its window"
    _age_the_touch(mw)
    _greet(mw, S(11))
    assert len(mw.spawns) == 2, "a different sender is not held by it"


def test_PLANT_the_hourly_cap_is_atomic_and_enforced(mw, monkeypatch):
    monkeypatch.setenv("PREWARM_PER_HOUR", "2")
    for i in range(20, 26):
        _age_the_touch(mw)
        _greet(mw, S(i))
    assert len(mw.spawns) == 2, f"6 distinct senders, cap 2, got {len(mw.spawns)}"


def test_per_hour_zero_means_none(mw, monkeypatch):
    monkeypatch.setenv("PREWARM_PER_HOUR", "0")
    _greet(mw, S(30))
    assert mw.spawns == []


def test_OFF_unless_explicitly_on(mw, monkeypatch):
    for v in ("0", "off", "", "enabled", "tru"):
        monkeypatch.setenv("PREWARM_ENABLED", v)
        _age_the_touch(mw)
        _greet(mw, S(40 + len(v)))
    assert mw.spawns == []


def test_a_returning_user_greeting_also_warms(mw):
    _greet(mw, S(50))                                 # first contact
    _age_the_touch(mw)
    mw.BRIDGE_WATCH.clear()                           # fresh window
    _greet(mw, S(50))                                 # the same number greets again: the welcome, and a question may follow
    assert len(mw.spawns) == 2


def test_health_reports_the_parsed_settings_and_the_touch_age(mw):
    h = mw._health_prewarm()
    assert h["enabled"] is True and h["per_hour"] == 12 and h["sender_cooldown_s"] == 900.0 and h["last_touch_age_s"] is None
    mw.BRIDGE_WATCH[mw._PREWARM_TOUCH_KEY] = time.time() - 42
    assert 40 <= mw._health_prewarm()["last_touch_age_s"] <= 60


# ── structure: the properties that are easy to lose in a later edit ───────────────────────────────────────────────
def _fn(name):
    tree = ast.parse(open(SRC, encoding="utf-8").read())
    return next(n for n in ast.walk(tree) if isinstance(n, (ast.FunctionDef, ast.AsyncFunctionDef)) and n.name == name)


def test_the_warmup_runs_in_a_thread_never_on_the_event_loop():
    src = ast.unparse(_fn("greet_and_send"))
    assert "asyncio.to_thread(_prewarm_sync" in src, "the blocking Dict/spawn calls must not run on the loop that sends the greeting"
    assert isinstance(_fn("_prewarm_sync"), ast.FunctionDef), "a plain function: an `async def` here would put the blocking calls back on the loop"


def test_the_spawn_takes_no_arguments_and_the_function_never_reads_user_text():
    fn = _fn("_prewarm_sync")
    assert [a.arg for a in fn.args.args] == ["sender", "settings"]
    calls = [n for n in ast.walk(fn) if isinstance(n, ast.Call) and ast.unparse(n.func).endswith("served_index_identity.spawn")]
    assert len(calls) == 1 and not calls[0].args and not calls[0].keywords


def test_the_warmup_is_started_before_the_first_contact_send_not_after():
    body = ast.unparse(_fn("greet_and_send"))
    assert body.index("to_thread") < body.index("_ensure_disclosure"), "started first, so it overlaps the first-contact send"
    assert "finally" in body and "_settle_prewarm" in body, "and it is always settled before the function returns, on every return path"


def test_the_tunables_are_committed_and_reported():
    import json
    j = json.load(open(os.path.join(_ROOT, "chike-whatsapp", "deploy_tunables.json"), encoding="utf-8"))
    assert (j["PREWARM_ENABLED"], j["PREWARM_PER_HOUR"], j["PREWARM_SENDER_COOLDOWN_S"]) == ("1", "12", "900")
