# -*- coding: utf-8 -*-
"""THE 2026-11-25 REMINDER STORM, REPRODUCED AND BOUNDED (2026-11-26).

What happened: MAX_RENOTIFIES=0 ("no cap") + RENOTIFY_AFTER_S=420 + a sweep that stamped `last_notified_at` only AFTER a slow send, so overlapping
sweeps each thought the item was still due. 20 unreviewed test items produced 4,264 reminders to one reviewer number in ~16 h.

These tests drive the REAL sweep (`sweep_review_queue`) on a fake clock, one sweep per simulated minute. Every plant must FAIL against the
2026-11-13 behaviour: the PLANT tests reinstate it (uncapped / no lock / no claim) and assert the breach, so a bound that cannot be breached
proves nothing (R26).
"""
import asyncio
import datetime as _dt
import importlib.util
import os
import sys
import time as _time
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402

START = _dt.datetime(2026, 11, 25, 12, 0, 0, tzinfo=_dt.timezone.utc)


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


class Clock:
    def __init__(self):
        self.t = START.timestamp()

    def advance(self, s):
        self.t += s


@pytest.fixture
def sim(monkeypatch):
    from conftest import isolate_modal_stores
    clock = Clock()

    class FakeDT(_dt.datetime):
        @classmethod
        def now(cls, tz=None):
            return cls.fromtimestamp(clock.t, tz=tz or _dt.timezone.utc)
    monkeypatch.setattr(_dt, "datetime", FakeDT)
    monkeypatch.setattr(core, "datetime", FakeDT)
    monkeypatch.setattr(_time, "time", lambda: clock.t)

    for k, v in {"SENDER_SALT": "s", "REVIEWER_ROSTER": "+255700000098:Prosper", "REVIEW_SIGNING_KEY": "k",
                 "REVIEW_D_URL": "https://d.example", "REVIEW_CLAIM_URL": "https://c.example", "REVIEW_ACT_URL": "https://a.example",
                 "RENOTIFY_AFTER_S": "420", "MAX_RENOTIFIES": "1", "SEND_CAP_PER_RECIPIENT_PER_HOUR": "20",
                 "SEND_CAP_GLOBAL_PER_HOUR": "60", "DIGEST_ONLY_ABOVE": "100000"}.items():
        monkeypatch.setenv(k, v)
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = core
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", core)
    spec = importlib.util.spec_from_file_location("chike_mw_storm", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    isolate_modal_stores(mw, monkeypatch)
    mw.clock = clock
    mw._real_send_once = mw._send_once
    mw.sent = []                                   # (simulated seconds since start, kind)

    def kind(text):
        return "digest" if "MUHTASARI" in text else ("reminder" if "KUPITIA TENA" in text else "card")

    async def fake_send(to, text):
        mw.sent.append((clock.t - START.timestamp(), kind(text)))
        return True, None
    monkeypatch.setattr(mw, "_send_once", fake_send)
    return mw


def _put_items(mw, n, status="pending"):
    ts = START.isoformat(timespec="seconds")
    items = []
    for i in range(n):
        it = {"review_id": f"{ts}-{i:08d}", "status": status, "sender": f"2557000{i:05d}@s.whatsapp.net", "sender_hash": f"{i:012d}",
              "sender_tail": f"{i:04d}", "question": f"swali {i}", "draft": "jibu", "engine_working": None, "facts": ["f"],
              "answer_path": "fact", "model_calls": 1, "guards": [], "held_at": ts, "ts_held": ts, "fallback": False}
        mw.REVIEW_QUEUE[it["review_id"]] = it
        items.append(it)
    return items


def _first_cards(mw, items):
    for it in items:
        sent = _run(mw._notify_reviewers(it))
        mw._mark_notified(it, sent)


def _sweep(mw):
    return _run(mw.sweep_review_queue.get_raw_f()())


def _simulate(mw, items, hours):
    _first_cards(mw, items)
    for _ in range(int(hours * 60)):
        mw.clock.advance(60)
        _sweep(mw)
    return {k: sum(1 for _, kk in mw.sent if kk == k) for k in ("card", "reminder", "digest")}


def test_20_unreviewed_for_12_hours_stays_within_20_cards_20_reminders_12_digests(sim):
    counts = _simulate(sim, _put_items(sim, 20), 12)
    assert counts["card"] == 20, counts
    assert counts["reminder"] <= 20 and counts["reminder"] >= 20, f"each item gets exactly ONE reminder (positive control): {counts}"
    assert counts["digest"] <= 12 and counts["digest"] >= 11, f"hourly digests only (positive control: they DO go out): {counts}"


def test_PLANT_the_2026_11_13_settings_breach_the_same_bound(sim, monkeypatch):
    """Uncapped (MAX_RENOTIFIES=0 as it was) + no lock + no claim: the same simulation must BLOW the bound, or the bound proves nothing."""
    monkeypatch.setattr(core, "effective_max_renotifies", lambda v: 10 ** 9)       # the old "0 = no cap"
    counts = _simulate(sim, _put_items(sim, 20), 12)
    assert counts["reminder"] > 20 * 10, f"uncapped reminders must exceed the bound by far: {counts}"


def test_zero_pending_sends_no_digest_in_12_hours(sim):
    for st in ("sent", "withheld", "edited", "auto_sent"):
        _put_items(sim, 0)
    items = _put_items(sim, 5, status="sent")
    assert items
    for _ in range(12 * 60):
        sim.clock.advance(60)
        _sweep(sim)
    assert sim.sent == [], "nothing pending -> nothing sent: no digest, no reminder"


def test_a_digest_stops_the_hour_after_the_last_draft_is_decided(sim):
    items = _put_items(sim, 2)
    _first_cards(sim, items)
    for _ in range(90):
        sim.clock.advance(60)
        _sweep(sim)
    assert any(k == "digest" for _, k in sim.sent)
    for it in items:
        sim.REVIEW_QUEUE[it["review_id"]] = dict(sim.REVIEW_QUEUE[it["review_id"]], status="sent")
    n_before = len(sim.sent)
    for _ in range(180):
        sim.clock.advance(60)
        _sweep(sim)
    assert len(sim.sent) == n_before


def _slow_notify(mw, counter):
    async def slow(item, *, renotify=False):
        await asyncio.sleep(0.05)               # the network await during which overlapping sweeps used to see the item as still due
        counter.append(item["review_id"])
        return 1
    return slow


async def _three_overlapping(mw):
    return await asyncio.gather(*[mw.sweep_review_queue.get_raw_f()() for _ in range(3)])


def test_overlapping_sweeps_never_double_send_a_reminder(sim, monkeypatch):
    notified = []
    monkeypatch.setattr(sim, "_notify_reviewers", _slow_notify(sim, notified))
    items = _put_items(sim, 4)
    sim.clock.advance(8 * 60)                    # past RENOTIFY_AFTER_S: every item is due
    res = _run(_three_overlapping(sim))
    assert sorted(notified) == sorted(i["review_id"] for i in items), "positive control: every due item was reminded exactly once"
    assert sum(1 for r in res if r.get("skipped") == "overlap") == 2, "two of the three sweeps were turned away by the lock"


def test_the_atomic_claim_alone_also_prevents_a_double_send(sim, monkeypatch):
    """Defence in depth: with the LOCK defeated, the per-(item, reminder-number) claim still holds."""
    notified = []
    monkeypatch.setattr(sim, "_notify_reviewers", _slow_notify(sim, notified))
    monkeypatch.setattr(sim, "_sweep_lock_acquire", lambda token, ttl_s=300.0: True)
    items = _put_items(sim, 4)
    sim.clock.advance(8 * 60)
    _run(_three_overlapping(sim))
    assert sorted(notified) == sorted(i["review_id"] for i in items)


def test_PLANT_without_lock_or_claim_overlapping_sweeps_DO_double_send(sim, monkeypatch):
    notified = []
    monkeypatch.setattr(sim, "_notify_reviewers", _slow_notify(sim, notified))
    monkeypatch.setattr(sim, "_sweep_lock_acquire", lambda token, ttl_s=300.0: True)
    monkeypatch.setattr(sim, "_stamp_renotify_claim", lambda item: sim._fresh_item(item))      # the old behaviour: no claim, no pre-send stamp
    _put_items(sim, 4)
    sim.clock.advance(8 * 60)
    _run(_three_overlapping(sim))
    assert len(notified) > 4, "the planted old behaviour must double-send, or the two tests above prove nothing"


def test_the_stamp_is_written_BEFORE_the_send(sim, monkeypatch):
    seen = {}

    async def spy(item, *, renotify=False):
        seen["stored"] = dict(sim.REVIEW_QUEUE[item["review_id"]])
        return 1
    monkeypatch.setattr(sim, "_notify_reviewers", spy)
    _put_items(sim, 1)
    sim.clock.advance(8 * 60)
    _sweep(sim)
    assert seen["stored"]["renotify_count"] == 1 and seen["stored"]["last_notified_at"], "already recorded when the send began"


def test_a_stale_lock_from_a_dead_sweep_is_stolen_and_a_live_one_is_not(sim):
    assert sim._sweep_lock_acquire("a") is True
    assert sim._sweep_lock_acquire("b") is False, "a live lock is respected"
    sim.clock.advance(301)
    assert sim._sweep_lock_acquire("c") is True, "a lock older than the TTL (a dead sweep) is stolen"
    sim._sweep_lock_release("a")                 # a stale owner releasing must not free c's lock
    assert sim._sweep_lock_acquire("d") is False


def test_the_sweep_fails_closed_when_the_lock_store_is_broken(sim, monkeypatch):
    class Broken(dict):
        def put(self, *a, **k):
            raise RuntimeError("down")
    monkeypatch.setattr(sim, "BRIDGE_WATCH", Broken())
    _put_items(sim, 2)
    sim.clock.advance(8 * 60)
    assert _sweep(sim).get("skipped") == "overlap" and sim.sent == []


def test_with_the_real_ceiling_no_rolling_hour_exceeds_20_sends_to_the_reviewer(sim, monkeypatch):
    """The whole stack: the REAL _send_once (ceiling gate) with only the raw transport faked. 20 unreviewed items -> 20 cards fill the per-recipient
    cap in the first minute; nothing further goes out to the reviewer until the window rolls, and the cap alert is raised."""
    monkeypatch.setenv("SEND_CAP_REVIEWER_PER_RECIPIENT_PER_HOUR", "20")    # the reviewer class default is 40 (scale audit); this test pins the ENFORCEMENT at its own value
    transport, alerts = [], []

    async def raw(to, text):
        transport.append(sim.clock.t - START.timestamp())
        return True, None
    monkeypatch.setattr(sim, "_send_once", sim._real_send_once)
    monkeypatch.setattr(sim, "TRANSPORT", "bridge")
    monkeypatch.setattr(sim, "_send_once_bridge", raw)
    monkeypatch.setattr(sim, "_ping_healthcheck", lambda kind, body="", url_env="HEALTHCHECK_PING_URL": (alerts.append(body) or (True, None)))
    items = _put_items(sim, 20)
    _first_cards(sim, items)
    for _ in range(12 * 60):
        sim.clock.advance(60)
        _sweep(sim)
    assert len(transport) >= 20, "positive control: the cards DID go out"
    for t in transport:
        assert sum(1 for u in transport if t <= u < t + 3600) <= 20, "no rolling hour carries more than 20 sends to the reviewer"
    assert any("CAP" in b for b in alerts), "the cap alert was raised"
