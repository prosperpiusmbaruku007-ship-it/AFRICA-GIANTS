# -*- coding: utf-8 -*-
"""THE DIGEST RULE (founder, 2026-11-26): a digest only once some pending item has waited >= 60 min since its card, at most once per hour, never at 0.
Plants 1 and 2 must FAIL against the previous code (digest while >=1 pending): `test_PLANT_todays_rule...` reinstates it and shows both plants breached."""
import asyncio

import pytest

from test_reminder_storm import sim, core, START, _put_items, _first_cards, _sweep, _run  # noqa: F401  (sim is the fake-clock fixture)


def _minutes(mw, n):
    for _ in range(n):
        mw.clock.advance(60)
        _sweep(mw)


def _digests(mw):
    return [round(t / 60) for t, k in mw.sent if k == "digest"]      # simulated MINUTES since start


def _decide(mw, items, status="sent"):
    for it in items:
        mw.REVIEW_QUEUE[it["review_id"]] = dict(mw.REVIEW_QUEUE[it["review_id"]], status=status)


# 1. no digest in the first 59 minutes of an unreviewed queue
def test_1_no_digest_in_the_first_59_minutes(sim):
    _first_cards(sim, _put_items(sim, 3))
    _minutes(sim, 59)
    assert _digests(sim) == []
    assert any(k == "reminder" for _, k in sim.sent), "positive control: the sweep WAS running (the one reminder went at ~7 min)"


# 2. an item decided at minute 50 never produces a digest
def test_2_an_item_decided_at_minute_50_never_produces_a_digest(sim):
    items = _put_items(sim, 2)
    _first_cards(sim, items)
    _minutes(sim, 50)
    _decide(sim, items)
    _minutes(sim, 180)
    assert _digests(sim) == []


# 3. positive control: still pending at minute 61 -> exactly one digest
def test_3_an_item_still_pending_at_minute_61_gets_exactly_one_digest(sim):
    _first_cards(sim, _put_items(sim, 2))
    _minutes(sim, 61)
    assert _digests(sim) == [60]


# 4. at most once per hour; overlapping sweeps send one
def test_4a_12_hours_20_items_at_most_12_digests(sim):
    _first_cards(sim, _put_items(sim, 20))
    _minutes(sim, 12 * 60)
    d = _digests(sim)
    assert 11 <= len(d) <= 12 and d[0] == 60, d
    assert all(b - a >= 60 for a, b in zip(d, d[1:])), "never two inside an hour"


def test_4b_three_overlapping_sweeps_at_the_trigger_minute_send_one_digest(sim):
    _first_cards(sim, _put_items(sim, 2))
    _minutes(sim, 59)
    sim.clock.advance(60)

    async def three():
        return await asyncio.gather(*[sim.sweep_review_queue.get_raw_f()() for _ in range(3)])
    _run(three())
    assert _digests(sim) == [60] and len([1 for _, k in sim.sent if k == "digest"]) == 1


# 5. a fresh item next to an old one: triggered by the old one, lists both
def test_5_a_fresh_item_next_to_an_old_one_is_listed_and_the_old_one_triggers(sim):
    old = _put_items(sim, 1)
    _first_cards(sim, old)
    _minutes(sim, 55)
    fresh = _put_items(sim, 1)
    fresh[0]["review_id"] += "-fresh"
    sim.REVIEW_QUEUE[fresh[0]["review_id"]] = dict(fresh[0], ts_held=_now_iso(sim), held_at=_now_iso(sim))
    texts = []
    orig = sim._send_once

    async def spy(to, text):
        texts.append(text)
        return await orig(to, text)
    sim._send_once = spy
    _minutes(sim, 8)
    dig = [t for t in texts if "MUHTASARI" in t]
    assert len(dig) == 1 and "rasimu 2" in dig[0], dig


def _now_iso(mw):
    import datetime as dt
    return dt.datetime.fromtimestamp(mw.clock.t, dt.timezone.utc).isoformat(timespec="seconds")


# 6. 0 pending -> no digest
def test_6_zero_pending_no_digest(sim):
    items = _put_items(sim, 3, status="sent")
    assert items
    _minutes(sim, 180)
    assert sim.sent == []


# 7. fail-closed on an item with no usable timestamp
def test_7_an_item_without_a_usable_timestamp_does_not_trigger():
    now = core.datetime.now(core.timezone.utc)
    assert core.digest_trigger([{"status": "pending"}], now) is False
    assert core.digest_trigger([{"status": "pending", "ts_held": "not a date"}], now) is False
    old = (now - core.timedelta(hours=2)).isoformat()
    assert core.digest_trigger([{"status": "pending", "ts_held": old}], now) is True, "positive control"
    assert core.digest_trigger([{"status": "sent", "ts_held": old}], now) is False, "a decided item never triggers"


# 8. the one reminder is unaffected
def test_8_the_one_7_minute_reminder_still_goes_per_item(sim):
    _first_cards(sim, _put_items(sim, 4))
    _minutes(sim, 30)
    assert len([1 for _, k in sim.sent if k == "reminder"]) == 4 and _digests(sim) == []


# the tunable can never bring the old noise back
def test_a_mistyped_wait_cannot_shorten_it_below_a_minute():
    assert core.parse_digest_min_wait("0") == 3600.0 and core.parse_digest_min_wait("junk") == 3600.0 and core.parse_digest_min_wait(None) == 3600.0
    assert core.parse_digest_min_wait("120") == 120.0


# PLANT: the previous rule (digest while >= 1 pending) breaches plants 1 AND 2
def test_PLANT_todays_rule_fails_plants_1_and_2(sim, monkeypatch):
    monkeypatch.setattr(core, "digest_trigger", lambda items, now=None, min_wait_s=3600: bool(items))
    items = _put_items(sim, 3)
    _first_cards(sim, items)
    _minutes(sim, 5)
    assert _digests(sim) != [], "plant 1 breached: a digest inside the first hour (the live 07:14:53 one)"
    _decide(sim, items)


def test_PLANT_todays_rule_fails_plant_2_an_item_decided_at_50_min_still_got_a_digest(sim, monkeypatch):
    monkeypatch.setattr(core, "digest_trigger", lambda items, now=None, min_wait_s=3600: bool(items))
    items = _put_items(sim, 2)
    _first_cards(sim, items)
    _minutes(sim, 50)
    _decide(sim, items)
    _minutes(sim, 180)
    assert _digests(sim) != [], "plant 2 breached: under the old rule a digest was sent although every item was cleared inside the hour"
