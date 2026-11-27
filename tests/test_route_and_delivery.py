# -*- coding: utf-8 -*-
"""THE ROUTE ON EVERY REVIEW ITEM, AND A PER-ROW DELIVERY STAMP (founder, 2026-11-28, items 5a/5b).

5a. Archived items carried no route (36 of 36 on 2026-11-27: they predate `answer_path`), so per-route outcomes from real participants could not be computed. Now every item gets an explicit `route` at hold time,
and `archive_record` derives one for anything lacking it. A LEGACY item with no path says "unknown": it is never back-filled by running today's router over its question (today's router is not the route taken then).
5b. Every decided send records `send_returned_ts` and `send_ms`, and the timing report gains a decision -> delivered leg that counts legacy rows without a stamp and un-receipted sends instead of estimating them."""
import json
import os
import sys
import time
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _load_mw as _load_mw_real, _run  # noqa: E402
from test_archive_core import Spy, item as archive_item, NOW as ANOW  # noqa: E402


# ── 5a: stamp_route ─────────────────────────────────────────────────────────────────────────────────────
def test_stamp_route_single_multi_and_unknown():
    assert core.stamp_route({"answer_path": "engine:paye"})["route"] == "engine:paye"
    assert core.stamp_route({"answer_path": "engine:paye"})["routes"] == ["engine:paye"]
    multi = core.stamp_route({"answer_trace": {"routes": ["fact", "engine:vat"]}})
    assert multi["routes"] == ["fact", "engine:vat"] and multi["route"] == "engine:vat+fact", "a stable, sorted combination for a multi-part question"
    assert core.stamp_route({})["route"] == "unknown" and core.stamp_route({})["routes"] == ["unknown"]


def test_PLANT_a_legacy_item_is_archived_as_unknown_never_rederived_from_its_question():
    legacy = {"review_id": "r1", "sender": "255700000099@s.whatsapp.net", "sender_hash": "h", "status": "sent",
              "question": "Mshahara wa 800,000, PAYE ni kiasi gani? (a question today's router WOULD route to the PAYE engine)", "draft": "d"}
    rec = core.archive_record("review", legacy, "signing-key")
    assert rec["route"] == "unknown" and rec["routes"] == ["unknown"]
    assert "sender" not in rec, "and the archive record is still scrubbed of the participant's number"


def test_an_item_that_has_a_path_is_archived_with_it_and_an_existing_route_is_not_overwritten():
    rec = core.archive_record("review", {"review_id": "r", "sender_hash": "h", "answer_path": "engine:rent_wht", "draft": "d"}, "k")
    assert rec["route"] == "engine:rent_wht"
    kept = core.archive_record("review", {"review_id": "r", "sender_hash": "h", "answer_path": "fact", "route": "engine:custom", "routes": ["engine:custom"], "draft": "d"}, "k")
    assert kept["route"] == "engine:custom", "an explicit route is never re-derived"


def test_only_review_records_are_stamped_not_transcripts():
    rec = core.archive_record("transcript", {"ts": "t", "sender_hash": "h", "kind": "question", "question": "q"}, "k")
    assert "route" not in rec


@pytest.fixture
def mw(monkeypatch):
    m = _load_mw_real(monkeypatch)
    monkeypatch.setenv("REVIEWER_ROSTER", "+255700000011:Prosper")
    m.sent = []

    async def fake_send(to, text):
        m.sent.append((to, text))
        return True, None
    monkeypatch.setattr(m, "_send_once", fake_send)
    return m


def test_a_held_item_carries_an_explicit_route_from_the_moment_it_is_held(mw, monkeypatch):
    class _Remote:
        @staticmethod
        async def aio(message):
            return {"reply": "Ndiyo.", "working": "W", "facts": ["F"], "path": "engine:vat_registration", "model_calls": 0, "guards": []}

    class _Model:
        run = types.SimpleNamespace(remote=_Remote)
    monkeypatch.setattr(mw, "ChikeModel", _Model)
    monkeypatch.setenv("DISCLOSURE", "off")
    _run(mw.answer_and_send.get_raw_f()("255700000099@s.whatsapp.net", "Je, nahitaji kusajili VAT?"))
    items = list(mw.REVIEW_QUEUE.values())
    assert len(items) == 1
    assert items[0]["route"] == "engine:vat_registration" and items[0]["routes"] == ["engine:vat_registration"]


def test_the_archive_run_writes_the_route_into_the_archived_file(mw, monkeypatch, tmp_path):
    import datetime as dt
    mw.vol = Spy(tmp_path / "vol")
    monkeypatch.setattr(mw, "_archive_store", lambda: mw.vol)
    monkeypatch.setattr(mw, "_ping_healthcheck", lambda *a, **k: (True, None))
    shift = dt.datetime.now(dt.timezone.utc) - ANOW
    old = archive_item(1, "sent", days_ago=9)
    for k in ("decided_ts", "ts_held"):
        old[k] = (dt.datetime.fromisoformat(old[k]) + shift).isoformat(timespec="seconds")
    for k in ("answer_path", "answer_trace", "route", "routes"):
        old.pop(k, None)
    mw.REVIEW_QUEUE[old["review_id"]] = old
    out = mw.run_archive.get_raw_f()()
    assert out["review_archived"] == 1
    files = [os.path.join(dp, f) for dp, _, fs in os.walk(mw.vol.root) for f in fs if "review" in dp.replace("\\", "/")]
    assert files, "an archived review file exists"
    rec = json.load(open(files[0], encoding="utf-8"))
    assert rec["route"] == "unknown" and rec["routes"] == ["unknown"], "the archived record carries an explicit route"


# ── 5b: the delivery stamp ─────────────────────────────────────────────────────────────────────────────
def test_the_auto_send_path_records_the_delivery_stamp_too():
    from test_review_timeout import _load_mw as _load_timeout_mw, _aged, _sweep
    mp = pytest.MonkeyPatch()
    try:
        m, sent = _load_timeout_mw(mp)
        it = _aged(m, 16)
        _sweep(m)
        stored = m.REVIEW_QUEUE[it["review_id"]]
        assert stored["status"] == "auto_sent" and stored["send_state"] == "delivered"
        assert stored["send_returned_ts"] and isinstance(stored["send_ms"], int) and stored["send_ms"] >= 0
    finally:
        mp.undo()


def _decided(decided, returned, state="delivered", status="sent", send_ms=800, **kw):
    import datetime as dt
    base = dt.datetime(2026, 11, 28, 10, 0, 0, tzinfo=dt.timezone.utc)
    d = {"review_id": f"r{decided}", "sender_hash": "h", "status": status, "ts_held": base.isoformat(), "decided_ts": (base + dt.timedelta(seconds=decided)).isoformat(),
         "send_state": state, "fallback": False}
    if returned is not None:
        d["send_returned_ts"] = (base + dt.timedelta(seconds=decided + returned)).isoformat()
        d["send_ms"] = send_ms
    d.update(kw)
    return d


def test_the_delivery_leg_is_exact_on_a_known_set():
    items = [_decided(100, 3), _decided(200, 5), _decided(300, 9, status="edited")]
    dv = core.latency_report(items, [])["delivery"]
    assert dv["decision_to_delivered_s"]["n"] == 3 and dv["decision_to_delivered_s"]["p50"] == 5.0 and dv["decision_to_delivered_s"]["max"] == 9.0
    assert dv["send_call_s"]["n"] == 3 and dv["send_call_s"]["p50"] == 0.8
    assert dv["no_stamp_legacy"] == 0 and dv["not_delivered"] == 0


def test_PLANT_a_legacy_item_without_a_stamp_is_counted_not_estimated():
    dv = core.latency_report([_decided(100, 3), _decided(200, None)], [])["delivery"]
    assert dv["decision_to_delivered_s"]["n"] == 1 and dv["no_stamp_legacy"] == 1


def test_PLANT_a_send_that_was_not_receipted_is_counted_not_timed():
    dv = core.latency_report([_decided(100, 3), _decided(200, 30, state="pending_receipt"), _decided(300, 1, state="failed")], [])["delivery"]
    assert dv["decision_to_delivered_s"]["n"] == 1 and dv["not_delivered"] == 2, "a 30 s accept-but-pending send must not be reported as a 30 s delivery"


def test_auto_sent_and_withheld_items_do_not_enter_the_delivery_leg():
    dv = core.latency_report([_decided(100, 3, status="auto_sent"), _decided(100, 3, status="withheld"), _decided(100, 3, fallback=True)], [])["delivery"]
    assert dv["decision_to_delivered_s"]["n"] == 0 and dv["no_stamp_legacy"] == 0 and dv["not_delivered"] == 0


def test_an_empty_delivery_leg_is_None_not_zero():
    d = core.latency_report([], [])["delivery"]["decision_to_delivered_s"]
    assert d == {"n": 0, "p50": None, "p90": None, "max": None}


def test_the_summary_prints_the_delivery_line():
    import importlib.util
    spec = importlib.util.spec_from_file_location("aps_d", os.path.join(_ROOT, "scripts", "answer_path_summary.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    out = m.render_latency(core.latency_report([_decided(100, 3), _decided(200, None)], []))
    assert "[delivery] decision -> delivered n=1" in out and "1 legacy without a stamp" in out


# ── the card-push map is pruned ─────────────────────────────────────────────────────────────────────────
def test_prune_review_pushes_removes_old_keeps_young_and_unreadable():
    now = 2_000_000_000.0
    pushes = {"old": {"ts": now - 15 * 86400}, "young": {"ts": now - 86400}, "boundary": {"ts": now - 14 * 86400}, "bad": {"ts": "??"}, "none": None}
    out = core.prune_review_pushes(pushes, now)
    assert set(pushes) == {"young", "boundary", "bad", "none"} and out == {"pushes_pruned": 1, "pushes_kept_bad_ts": 2}, "strictly older than 14 days goes; an unreadable stamp is kept, never guessed"


def test_the_archive_run_prunes_the_push_map_and_reports_it(mw, monkeypatch, tmp_path):
    mw.vol = Spy(tmp_path / "vol")
    monkeypatch.setattr(mw, "_archive_store", lambda: mw.vol)
    monkeypatch.setattr(mw, "_ping_healthcheck", lambda *a, **k: (True, None))
    mw.REVIEW_PUSHES["old"] = {"ts": time.time() - 20 * 86400}
    mw.REVIEW_PUSHES["new"] = {"ts": time.time() - 60}
    out = mw.run_archive.get_raw_f()()
    assert out["pushes_pruned"] == 1 and set(mw.REVIEW_PUSHES.keys()) == {"new"}
