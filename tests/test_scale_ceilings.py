# -*- coding: utf-8 -*-
"""SCALE CEILINGS AND DIGEST-ONLY MODE (item B, 2026-11-26 scale audit).

* Participant and reviewer sends are separate CLASSES with their own ceilings, so a participant flood cannot starve a card and a card storm cannot
  starve a participant. Participant per-recipient 20/h, participant global 150/h (warn at 75), reviewer per-recipient 40/h.
* Above DIGEST_ONLY_ABOVE (8) pending drafts, new cards are not pushed one by one and the sweeper stops re-notifying; the existing HOURLY digest
  carries them (cadence deliberately unchanged), listing up to 10.
* The queue-depth alert fires on pending > 10 or oldest > 45 min, 07:00-22:00 EAT only.

Plants (R26): every limb has a positive control, and the separation / mode tests are shown to FAIL against the old single-class / always-card behaviour.
"""
import asyncio
import datetime as dt
import importlib.util
import os
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _load_mw as _load_mw_real, _run, hc as _mw_core  # noqa: E402   (_mw_core: the handler_core copy the loaded module really calls)
from test_reminder_storm import sim, _put_items, _first_cards, _sweep, START  # noqa: E402,F401  (the storm test's real-sweep simulation)

REV1, REV2 = "255700000011", "255700000022"


@pytest.fixture
def mw(monkeypatch):
    m = _load_mw_real(monkeypatch)
    monkeypatch.setenv("REVIEWER_ROSTER", f"+{REV1}:Prosper,+{REV2}:Amina")
    monkeypatch.setenv("SEND_CAP_PER_RECIPIENT_PER_HOUR", "20")
    monkeypatch.setenv("SEND_CAP_GLOBAL_PER_HOUR", "150")
    monkeypatch.delenv("SEND_CAP_REVIEWER_PER_RECIPIENT_PER_HOUR", raising=False)
    m.transport_calls, m.alerts = [], []

    async def raw(to, text):
        m.transport_calls.append(to)
        return True, None
    monkeypatch.setattr(m, "TRANSPORT", "bridge")
    monkeypatch.setattr(m, "_send_once_bridge", raw)
    monkeypatch.setattr(m, "_ping_healthcheck", lambda kind, body="", url_env="HEALTHCHECK_PING_URL": (m.alerts.append((kind, body)) or (True, None)))
    return m


def _send(m, to, n=1):
    return [_run(m._send_once(to, "x")) for _ in range(n)]


def _participant(i):
    return f"2557100{i:05d}@s.whatsapp.net"


# ── ceilings: the two classes ────────────────────────────────────────────────────────────────────────────────
def test_reviewer_per_recipient_cap_is_40_and_the_participant_cap_stays_20(mw):
    r = _send(mw, f"{REV1}@s.whatsapp.net", 41)
    assert all(ok for ok, _ in r[:40]) and r[40][0] is False, "40 pushes to a reviewer pass, the 41st is refused"
    p = _send(mw, _participant(1), 21)
    assert all(ok for ok, _ in p[:20]) and p[20][0] is False, "participant per-recipient is still 20"


def test_a_participant_flood_cannot_consume_reviewer_capacity(mw):
    res = [_run(mw._send_once(_participant(i), "x")) for i in range(151)]
    assert all(ok for ok, _ in res[:150]) and res[150][0] is False, "positive control: the participant class is full at 150"
    assert _run(mw._send_once(f"{REV1}@s.whatsapp.net", "card"))[0] is True, "a card still reaches the reviewer"


def test_PLANT_with_one_shared_class_the_flood_DOES_starve_the_reviewer(mw, monkeypatch):
    monkeypatch.setattr(_mw_core, "is_reviewer_number", lambda to, roster: False)  # the 2026-11-26 behaviour: everyone counted together (patched on the module the gate calls)
    for i in range(150):
        _run(mw._send_once(_participant(i), "x"))
    assert _run(mw._send_once(f"{REV1}@s.whatsapp.net", "card"))[0] is False, "the separation test can fail"


def test_a_reviewer_card_storm_cannot_consume_participant_capacity(mw):
    _send(mw, f"{REV1}@s.whatsapp.net", 40)
    _send(mw, f"{REV2}@s.whatsapp.net", 40)
    res = [_run(mw._send_once(_participant(i), "x")) for i in range(150)]
    assert all(ok for ok, _ in res), "all 150 participant sends still go out after 80 reviewer pushes"


def test_a_number_not_on_the_roster_is_a_participant_the_fail_safe_class(mw):
    r = _send(mw, "255799999999@s.whatsapp.net", 21)
    assert r[19][0] is True and r[20][0] is False, "an unlisted number gets the participant per-recipient cap of 20, not the reviewer's 40"


def test_each_reviewer_has_their_own_per_recipient_count(mw):
    a = _send(mw, f"{REV1}@s.whatsapp.net", 40)
    b = _send(mw, f"{REV2}@s.whatsapp.net", 40)
    assert all(ok for ok, _ in a) and all(ok for ok, _ in b), "two reviewers each get 40: 80 reviewer pushes in the hour"


def test_a_phone_jid_and_a_bare_number_are_the_same_reviewer():
    roster = [("+255700000011", "P")]
    assert core.is_reviewer_number("255700000011@s.whatsapp.net", roster) and core.is_reviewer_number("255700000011", roster)
    assert not core.is_reviewer_number("255700000099", roster) and not core.is_reviewer_number("", roster)
    assert not core.is_reviewer_number("255700000011", [])


def test_warning_fires_at_75_of_150_and_not_at_74(mw):
    for i in range(74):
        _run(mw._send_once(_participant(i), "x"))
    assert not [b for k, b in mw.alerts if "WARNING" in b], "74 of 150 is under 50%"
    _run(mw._send_once(_participant(74), "x"))
    w = [b for k, b in mw.alerts if "WARNING" in b]
    assert w and "participant" in w[0], f"the 75th send (50%) raises the warning, naming its class: {mw.alerts}"


def test_the_reviewer_class_warns_at_20_of_40(mw):
    _send(mw, f"{REV1}@s.whatsapp.net", 20)
    assert [b for k, b in mw.alerts if "WARNING" in b and "reviewer" in b]


def test_caps_cannot_be_switched_off_by_a_typo():
    assert core.parse_reviewer_cap("0") == 40 and core.parse_reviewer_cap("junk") == 40 and core.parse_reviewer_cap(None) == 40
    assert core.parse_reviewer_cap("25") == 25                                    # positive control
    assert core.parse_digest_only_above("0") == 8 and core.parse_digest_only_above("x") == 8 and core.parse_digest_only_above("3") == 3


def test_health_reports_both_classes(mw, monkeypatch):
    d = mw._health_send_ceiling()
    assert d["per_recipient_per_hour"] == 20 and d["global_per_hour"] == 150 and d["reviewer_per_recipient_per_hour"] == 40 and d["digest_only_above"] == 8


# ── digest-only mode ─────────────────────────────────────────────────────────────────────────────────────────
def test_notify_mode_boundary_is_strictly_above_8():
    assert core.notify_mode(8, 8) == "card" and core.notify_mode(9, 8) == "digest_only"
    assert core.notify_mode(None, 8) == "card" and core.notify_mode("junk", 8) == "card"    # an unreadable count never silences a card


def _capture(sim, monkeypatch):
    texts = []

    async def fake_send(to, text):
        sim.sent.append((sim.clock.t - START.timestamp(), "digest" if "MUHTASARI" in text else ("reminder" if "KUPITIA TENA" in text else "card")))
        texts.append(text)
        return True, None
    monkeypatch.setattr(sim, "_send_once", fake_send)
    return texts


def _count(sim, kind):
    return sum(1 for _, k in sim.sent if k == kind)


def test_at_8_pending_each_unclaimed_draft_is_still_re_notified(sim, monkeypatch):
    monkeypatch.setenv("DIGEST_ONLY_ABOVE", "8")
    items = _put_items(sim, 8)
    _first_cards(sim, items)
    sim.clock.advance(8 * 60)
    _sweep(sim)
    assert _count(sim, "reminder") == 8, "positive control: at the threshold the old behaviour holds"


def test_at_9_pending_the_sweeper_stops_re_notifying(sim, monkeypatch):
    monkeypatch.setenv("DIGEST_ONLY_ABOVE", "8")
    items = _put_items(sim, 9)
    _first_cards(sim, items)
    sim.clock.advance(8 * 60)
    _sweep(sim)
    assert _count(sim, "reminder") == 0, "digest-only: no per-card reminders while more than 8 are pending"


def test_PLANT_without_the_mode_the_same_9_ARE_re_notified(sim, monkeypatch):
    monkeypatch.setenv("DIGEST_ONLY_ABOVE", "100000")                              # mode effectively off: the pre-change behaviour
    items = _put_items(sim, 9)
    _first_cards(sim, items)
    sim.clock.advance(8 * 60)
    _sweep(sim)
    assert _count(sim, "reminder") == 9, "the 9-pending test above can fail"


def test_overload_digest_lists_up_to_10_names_the_mode_and_stays_hourly(sim, monkeypatch):
    monkeypatch.setenv("DIGEST_ONLY_ABOVE", "8")
    texts = _capture(sim, monkeypatch)
    _first_cards(sim, _put_items(sim, 12))
    for _ in range(12 * 60):
        sim.clock.advance(60)
        _sweep(sim)
    digests = [t for t in texts if "MUHTASARI" in t]
    assert 11 <= len(digests) <= 12, f"hourly cadence is unchanged by the mode (founder's rule): {len(digests)}"
    assert "FOLENI NI KUBWA" in digests[0], "the digest says it is carrying the backlog"
    assert digests[0].count("• ...") == 10 and "…na 2 zaidi" in digests[0], "up to 10 listed, the rest counted"


def test_a_normal_digest_is_unchanged_and_lists_5(sim, monkeypatch):
    monkeypatch.setenv("DIGEST_ONLY_ABOVE", "100000")
    texts = _capture(sim, monkeypatch)
    _first_cards(sim, _put_items(sim, 7))
    for _ in range(90):
        sim.clock.advance(60)
        _sweep(sim)
    digests = [t for t in texts if "MUHTASARI" in t]
    assert digests and "FOLENI" not in digests[0] and digests[0].count("• ...") == 5


def _drive_hold(mw, monkeypatch, n_pending_before):
    for i in range(n_pending_before):
        ts = (dt.datetime.now(dt.timezone.utc) - dt.timedelta(minutes=5)).isoformat(timespec="seconds")
        mw.REVIEW_QUEUE[f"{ts}-pre{i:04d}"] = {"review_id": f"{ts}-pre{i:04d}", "status": "pending", "ts_held": ts, "sender_tail": "0000",
                                              "question": "q", "draft": "d", "answer_path": "fact", "model_calls": 1}
    pushes = []

    async def fake_send(to, text):
        pushes.append(text)
        return True, None
    monkeypatch.setattr(mw, "_send_once", fake_send)

    class _Remote:
        @staticmethod
        async def aio(message):
            return {"reply": "Ndiyo.", "working": "W", "facts": ["F"], "path": "engine:vat_registration"}

    class _Model:
        run = types.SimpleNamespace(remote=_Remote)
    monkeypatch.setattr(mw, "ChikeModel", _Model)
    _run(mw.answer_and_send.get_raw_f()("255700000099@s.whatsapp.net", "Swali jipya"))
    new = [i for i in mw.REVIEW_QUEUE.values() if not str(i["review_id"]).endswith(tuple(f"pre{k:04d}" for k in range(n_pending_before)))]
    assert len(new) == 1
    return new[0], pushes


def test_the_REAL_hold_path_pushes_a_card_at_the_threshold(mw, monkeypatch):
    item, pushes = _drive_hold(mw, monkeypatch, 7)                                # this draft is the 8th pending: not above 8
    assert item["notify_mode"] == "card" and len(pushes) >= 1


def test_the_REAL_hold_path_pushes_NO_card_above_the_threshold_but_stores_the_draft(mw, monkeypatch):
    item, pushes = _drive_hold(mw, monkeypatch, 8)                                # this draft is the 9th pending
    assert item["notify_mode"] == "digest_only" and item["status"] == "pending", "held and reviewable, never dropped"
    assert pushes == [], "no per-card push in digest-only mode"


# ── queue-depth alert ────────────────────────────────────────────────────────────────────────────────────────
def _items(n, age_min, now):
    ts = (now - dt.timedelta(minutes=age_min)).isoformat(timespec="seconds")
    return [{"review_id": str(i), "status": "pending", "ts_held": ts} for i in range(n)]


NOON_EAT = dt.datetime(2026, 11, 26, 9, 0, tzinfo=dt.timezone.utc)                 # 12:00 EAT
NIGHT_EAT = dt.datetime(2026, 11, 26, 22, 30, tzinfo=dt.timezone.utc)              # 01:30 EAT


def test_alert_depth_boundary_is_strictly_above_10():
    assert core.queue_depth_alert(_items(10, 1, NOON_EAT), NOON_EAT) is None
    assert "11 drafts pending" in core.queue_depth_alert(_items(11, 1, NOON_EAT), NOON_EAT)


def test_alert_age_boundary_is_strictly_above_45_minutes():
    assert core.queue_depth_alert(_items(1, 45, NOON_EAT), NOON_EAT) is None
    assert "oldest pending draft is 46 min" in core.queue_depth_alert(_items(1, 46, NOON_EAT), NOON_EAT)


def test_alert_is_silent_overnight_and_covers_the_whole_07_to_22_EAT_window():
    assert core.queue_depth_alert(_items(30, 600, NIGHT_EAT), NIGHT_EAT) is None, "01:30 EAT: an overnight wait is normal"
    at = lambda h: dt.datetime(2026, 11, 26, h, 0, tzinfo=dt.timezone.utc)         # noqa: E731  (UTC hour h = EAT h+3)
    bad = _items(30, 600, at(4))
    assert core.queue_depth_alert(bad, at(3, )) is None and core.queue_depth_alert(bad, at(4)) is not None     # 06:00 EAT silent, 07:00 EAT alerts
    assert core.queue_depth_alert(_items(30, 600, at(18)), at(18)) is not None and core.queue_depth_alert(_items(30, 600, at(19)), at(19)) is None  # 21:00 yes, 22:00 no


def test_alert_ignores_decided_drafts_and_survives_a_bad_timestamp():
    items = _items(12, 1, NOON_EAT) + [{"review_id": "d", "status": "sent", "ts_held": "2020-01-01T00:00:00+00:00"}, {"review_id": "b", "status": "pending", "ts_held": "junk"}]
    assert "13 drafts pending" in core.queue_depth_alert(items, NOON_EAT)          # the decided one is not counted; the junk one is, and does not crash


def test_the_sweeper_raises_the_queue_alert_once_per_hour(sim, monkeypatch):
    alerts = []
    monkeypatch.setattr(sim, "_ping_healthcheck", lambda kind, body="", url_env="HEALTHCHECK_PING_URL": (alerts.append(body) or (True, None)))
    monkeypatch.setenv("DIGEST_ONLY_ABOVE", "100000")
    _put_items(sim, 12)                                                            # sim clock starts 15:00 EAT, inside the window
    for _ in range(50):
        sim.clock.advance(60)
        _sweep(sim)
    q = [b for b in alerts if "REVIEW QUEUE" in b]
    assert len(q) == 1 and "12 drafts pending" in q[0], f"one alert, not one per minute: {alerts}"
