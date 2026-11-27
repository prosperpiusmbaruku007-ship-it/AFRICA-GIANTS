# -*- coding: utf-8 -*-
"""Question-to-answer legs (founder, 2026-11-28), from stored rows. Planted so the report cannot silently invent a leg or mix populations:

  * a leg exists only where the question row and the review item JOIN EXACTLY; a miss is COUNTED as unjoined, never filled in;
  * auto-sent items are excluded (their wait is a 15-minute policy, not a reviewer's speed) and COUNTED;
  * test senders are excluded and COUNTED (R39: an exclusion that cannot be seen is a shrinking count);
  * an empty population reports None, never 0.0 (R39); percentiles are exact on a known set;
  * the cold/warm split follows the row's own flag, and a model failure (fallback) is not an answered question."""
import os
import sys

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402

H = "h1"


def iso(sec):
    import datetime as dt
    return (dt.datetime(2026, 11, 20, 12, 0, 0, tzinfo=dt.timezone.utc) + dt.timedelta(seconds=sec)).isoformat(timespec="seconds")


def pair(i, model_s, total_s, wait_s, cold=False, status="sent", sender=H, fallback=False, joined=True):
    held = 1000 * i
    ts = iso(held)
    item = {"review_id": f"r{i}", "sender_hash": sender, "status": status, "ts_held": ts, "decided_ts": iso(held + wait_s), "fallback": fallback}
    row = {"kind": "question", "sender_hash": sender, "ts": ts if joined else iso(held + 1), "model_latency_ms": int(model_s * 1000),
           "total_latency_ms": int(total_s * 1000), "cold_start_suspected": cold}
    return item, row


def build(*specs, **kw):
    items, rows = [], []
    for s in specs:
        a, b = pair(*s[0], **s[1]) if isinstance(s[0], tuple) else pair(*s)
        items.append(a)
        rows.append(b)
    return items, rows


def test_known_set_gives_exact_legs_and_percentiles():
    # three warm answers: model 5/10/15 s, total 8/20/30 s, reviewer wait 100/200/300 s
    items, rows = build((1, 5, 8, 100), (2, 10, 20, 200), (3, 15, 30, 300))
    rep = core.latency_report(items, rows)
    a = rep["all"]
    assert rep["answered_sent"] == 3 and rep["unjoined"] == 0
    assert a["model_s"]["p50"] == 10.0 and a["model_s"]["max"] == 15.0
    assert a["hold_notify_s"]["p50"] == 10.0, "20 s total - 10 s model"
    assert a["question_to_draft_s"]["p50"] == 20.0
    assert a["draft_to_decision_s"]["p50"] == 200.0
    assert a["question_to_decision_s"]["p50"] == 220.0
    assert a["question_to_decision_s"]["n"] == 3
    assert a["draft_to_decision_s"]["p90"] == 280.0, "linear interpolation: 200 + (300-200)*0.8"


def test_PLANT_a_question_that_does_not_join_is_counted_and_gives_no_leg():
    items, rows = build((1, 5, 8, 100), ((2, 10, 20, 200), {"joined": False}))
    rep = core.latency_report(items, rows)
    assert rep["answered_sent"] == 2 and rep["unjoined"] == 1
    assert rep["all"]["model_s"]["n"] == 1, "the unjoined question contributes to NO leg: no number is guessed for it"


def test_auto_sent_items_are_excluded_and_counted():
    items, rows = build((1, 5, 8, 100), ((2, 10, 20, 900), {"status": "auto_sent"}))
    rep = core.latency_report(items, rows)
    assert rep["auto_sent_excluded"] == 1 and rep["answered_sent"] == 1
    assert rep["all"]["draft_to_decision_s"]["n"] == 1 and rep["all"]["draft_to_decision_s"]["max"] == 100.0


def test_test_senders_are_excluded_by_hash_and_counted_and_include_test_restores_them():
    items, rows = build((1, 5, 8, 100), ((2, 10, 20, 200), {"sender": "tst"}))
    rep = core.latency_report(items, rows, test_hashes={"tst"})
    assert rep["excluded_test"] == 1 and rep["answered_sent"] == 1
    assert core.latency_report(items, rows, test_hashes={"tst"}, include_test=True)["answered_sent"] == 2


def test_nothing_measured_reports_None_never_zero():
    rep = core.latency_report([], [])
    for leg in rep["all"].values():
        assert leg == {"n": 0, "p50": None, "p90": None, "max": None}


def test_cold_and_warm_follow_the_rows_own_flag():
    items, rows = build(((1, 70, 80, 100), {"cold": True}), (2, 5, 8, 100), (3, 6, 9, 100))
    rep = core.latency_report(items, rows)
    assert rep["cold"]["model_s"]["n"] == 1 and rep["cold"]["model_s"]["p50"] == 70.0
    assert rep["warm"]["model_s"]["n"] == 2 and rep["warm"]["model_s"]["p50"] == 5.5


def test_a_model_failure_is_not_an_answered_question():
    items, rows = build(((1, 5, 8, 100), {"fallback": True}), (2, 5, 8, 100))
    rep = core.latency_report(items, rows)
    assert rep["answered_sent"] == 1


def test_PLANT_an_edited_item_was_delivered_so_it_is_an_answer_and_its_slow_wait_counts():
    items, rows = build((1, 5, 8, 100), ((2, 5, 8, 4000), {"status": "edited"}))
    rep = core.latency_report(items, rows)
    assert rep["answered_sent"] == 2
    assert rep["all"]["draft_to_decision_s"]["max"] == 4000.0, "dropping edits would hide exactly the slow reviews"


def test_withheld_and_pending_items_are_not_answers():
    items, rows = build(((1, 5, 8, 100), {"status": "withheld"}), ((2, 5, 8, 100), {"status": "pending"}))
    assert core.latency_report(items, rows)["answered_sent"] == 0


def test_it_says_what_it_does_not_measure():
    assert any("delivered" in x for x in core.latency_report([], [])["not_measured"])


def test_the_summary_script_renders_it_and_prints_every_leg():
    import importlib.util
    spec = importlib.util.spec_from_file_location("aps_t", os.path.join(_ROOT, "scripts", "answer_path_summary.py"))
    m = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(m)
    items, rows = build((1, 5, 8, 100))
    out = m.render_latency(core.latency_report(items, rows))
    for label in ("model call", "hold + notify reviewers", "question -> draft ready", "draft -> reviewer decision", "question -> decision", "NOT MEASURED"):
        assert label in out, label
    assert "[cold start suspected]" in out and "[warm]" in out
