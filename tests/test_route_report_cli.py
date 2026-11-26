# -*- coding: utf-8 -*-
"""ITEM D: the per-route review report, printed beside the answer-path summary (scripts/answer_path_summary.py). Measurement only, text-free.

Plants: archived history is ADDED to the hot counts (so archiving cannot make a route look cleaner than it is); a route with nothing reviewed prints n/a, never
0.0%; an unreadable archive is announced; test items are counted, not hidden; and the report contains no question text or sender.
"""
import importlib.util
import io
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_archive_core import item, Spy, NOW  # noqa: E402

_spec = importlib.util.spec_from_file_location("answer_path_summary", os.path.join(_ROOT, "scripts", "answer_path_summary.py"))
cli = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(cli)


def _hot(i, status, route="engine:paye", **kw):
    return item(i, status, route=route, days_ago=0, **kw)


def _run(argv, capsys):
    rc = cli.main(argv)
    return rc, capsys.readouterr().out


@pytest.fixture
def files(tmp_path):
    rows = [{"kind": "question", "answer_trace": {"cls": "engine", "routes": ["paye"], "model_calls": 0, "guard_fired": False}}]
    (tmp_path / "rows.json").write_text(json.dumps(rows), encoding="utf-8")
    return tmp_path


def test_the_report_prints_beside_the_answer_path_summary(files, capsys):
    hot = [_hot(1, "sent"), _hot(2, "edited"), _hot(3, "withheld"), _hot(4, "sent", route="engine:rent_wht"), _hot(5, "pending")]
    (files / "items.json").write_text(json.dumps(hot), encoding="utf-8")
    rc, out = _run(["--file", str(files / "rows.json"), "--reviews", str(files / "items.json")], capsys)
    assert rc == 0 and "answer paths:" in out and "review outcomes per route" in out
    paye = [ln for ln in out.splitlines() if ln.strip().startswith("paye")][0].split()
    assert paye[1:7] == ["3", "1", "1", "1", "0", "1"], paye           # reviewed 3, unchanged 1, edited 1, withheld 1, auto 0, pending 1
    assert "33.3%" in out


def test_archived_history_is_added_so_archiving_cannot_make_a_route_look_cleaner(files, capsys, tmp_path):
    store = Spy(tmp_path / "vol")
    old = [item(i, "edited", days_ago=9) for i in range(1, 4)]            # three EDITED drafts, now only in the archive
    core.archive_run(review_items={i["review_id"]: i for i in old}, transcripts={}, store=store, signing_key="k", now=NOW)
    (files / "items.json").write_text(json.dumps([_hot(10, "sent")]), encoding="utf-8")
    agg_dir = os.path.join(store.root, "archive", "aggregates")
    _, with_archive = _run(["--file", str(files / "rows.json"), "--reviews", str(files / "items.json"), "--archive-dir", agg_dir], capsys)
    _, hot_only = _run(["--file", str(files / "rows.json"), "--reviews", str(files / "items.json")], capsys)
    assert "25.0%" in with_archive and "100.0%" in hot_only, "with the archive: 1 unchanged of 4 reviewed; hot only would have said 100%"
    assert "1 archived day(s)" in with_archive


def test_a_route_with_nothing_reviewed_prints_na_never_a_zero_rate(files, capsys):
    (files / "items.json").write_text(json.dumps([_hot(1, "pending", route="engine:vat")]), encoding="utf-8")
    _, out = _run(["--file", str(files / "rows.json"), "--reviews", str(files / "items.json")], capsys)
    import re
    section = out.split("review outcomes per route")[1]
    assert "n/a (nothing reviewed)" in section and not re.search(r"(?<![\d.])0\.0%", section)


def test_test_items_are_counted_and_the_report_holds_no_text_or_sender(files, capsys):
    items = [_hot(1, "sent", test_sender=True), _hot(2, "sent", sh="cccccccccccc")]            # a DIFFERENT sender: not the test sender's hash
    (files / "items.json").write_text(json.dumps(items), encoding="utf-8")
    _, out = _run(["--file", str(files / "rows.json"), "--reviews", str(files / "items.json")], capsys)
    assert "1 test excluded" in out
    for forbidden in ("SWALI", "@s.whatsapp.net", items[0]["sender_hash"], "jibu"):
        assert forbidden not in out


def test_without_reviews_the_report_is_skipped_loudly_not_silently(files, capsys):
    rc, out = _run(["--file", str(files / "rows.json")], capsys)
    assert rc == 0 and "per-route review report skipped" in out


def test_an_unreadable_archive_is_announced_in_the_output(monkeypatch, capsys):
    class _Vol:
        @staticmethod
        def listdir(path):
            raise RuntimeError("volume not found")

    import types
    fake_modal = types.SimpleNamespace(Volume=types.SimpleNamespace(from_name=lambda n: _Vol))
    monkeypatch.setitem(sys.modules, "modal", fake_modal)
    aggs, note = cli._volume_aggregates()
    assert aggs == [] and "NOT included" in note and "RuntimeError" in note


def test_the_render_has_a_row_per_route_and_handles_an_empty_queue():
    assert "(no review items)" in cli.render_routes(core.route_report([]))
    out = cli.render_routes(core.route_report([_hot(1, "sent"), _hot(2, "sent", route="engine:sdl")]))
    assert "paye" in out and "sdl" in out


# ── 2026-11-26: older rows carry no test flag but share their sender's hash ─────────────────────────────────────
def test_an_unflagged_item_from_a_test_senders_hash_is_excluded_and_counted():
    flagged = _hot(1, "sent", test_sender=True)                                     # sender H1, flagged
    old_unflagged = _hot(2, "edited")                                               # SAME sender H1, written before the flag existed
    other = _hot(3, "sent", sh="cccccccccccc")                                      # a real participant
    th = core.test_hashes_from([flagged, old_unflagged, other])
    assert th == {flagged["sender_hash"]}
    rep = core.route_report([flagged, old_unflagged, other], test_hashes=th)
    assert rep["excluded_test"] == 2 and rep["routes"]["paye"]["approved_unchanged"] == 1 and rep["routes"]["paye"]["edited"] == 0


def test_PLANT_without_the_hashes_the_unflagged_item_is_counted_as_a_real_participant():
    flagged, old_unflagged = _hot(1, "sent", test_sender=True), _hot(2, "edited")
    rep = core.route_report([flagged, old_unflagged])                               # the pre-fix call
    assert rep["excluded_test"] == 1 and rep["routes"]["paye"]["edited"] == 1, "the bug: the tester's older edit is reported as a real one"


def test_the_cli_applies_the_hashes_it_finds_on_flagged_records(files, capsys):
    items = [_hot(1, "sent", test_sender=True), _hot(2, "edited"), _hot(3, "sent", sh="cccccccccccc")]
    (files / "items.json").write_text(json.dumps(items), encoding="utf-8")
    _, out = _run(["--file", str(files / "rows.json"), "--reviews", str(files / "items.json")], capsys)
    assert "2 test excluded" in out, out


def test_the_archive_aggregate_excludes_an_unflagged_item_from_a_test_sender_hash(tmp_path):
    store = Spy(tmp_path / "vol")
    unflagged = item(1, "edited", days_ago=9)                                        # no test flag, sender hash H1
    core.archive_run(review_items={unflagged["review_id"]: unflagged}, transcripts={}, store=store, signing_key="k", now=NOW,
                     test_hashes={unflagged["sender_hash"]})
    ag = core.read_aggregates(store)[0]
    assert ag["excluded_test"] == 1 and ag["routes"] == {}, "counted as test, not as a real edit"
