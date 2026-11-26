# -*- coding: utf-8 -*-
"""BRIDGE-LEDGER-PRUNE-1 (2026-11-27). The bridge node forgets a ledger row after 24 h in memory, but the Dict copy was never deleted (3,534 rows against ~2,400 in the
last 24 h). The daily archiver now prunes rows older than 24 h, and the send-time index with them.

Plants (R26): the boundary is tested on BOTH sides (23 h kept, 25 h removed, exactly 24 h kept); a row with no readable timestamp is KEPT, never guessed at; a row still awaited by
the receipt reconciler is kept; a prune failure is visible in the run summary and never fails the archive."""
import os
import sys
import time

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _load_mw as _load_mw_real  # noqa: E402
from test_archive_core import Spy  # noqa: E402

H = 3600.0
NOW = 1_800_000_000.0


def _ledger(**ages_h):
    return {k: {"to": "x", "ts": NOW - a * H, "rank": 3} for k, a in ages_h.items()}


def test_a_row_at_23_hours_is_kept_and_at_25_hours_is_removed():
    led = _ledger(r23=23, r25=25, r1=1)
    out = core.prune_bridge_ledger(led, {}, NOW)
    assert set(led) == {"r23", "r1"} and out["ledger_pruned"] == 1 and out["ledger_kept_young"] == 2


def test_the_boundary_exactly_24_hours_is_kept_and_a_second_over_is_removed():
    led = {"exact": {"ts": NOW - 24 * H}, "over": {"ts": NOW - 24 * H - 1}}
    core.prune_bridge_ledger(led, {}, NOW)
    assert set(led) == {"exact"}, "strictly older than 24 h is removed; exactly 24 h is kept"


def test_a_row_with_no_readable_timestamp_is_kept_and_counted_never_guessed_at():
    led = {"missing": {"to": "x"}, "junk": {"ts": "yesterday"}, "none": None, "int_str": {"ts": str(int(NOW - 30 * H))}}
    out = core.prune_bridge_ledger(led, {}, NOW)
    assert out["ledger_kept_bad_ts"] == 3 and out["ledger_pruned"] == 1, out        # the numeric-string ts IS parseable (and 30 h old), so it goes
    assert set(led) == {"missing", "junk", "none"}


def test_a_row_still_awaited_by_the_receipt_reconciler_is_kept_even_when_old():
    led = _ledger(pending=40, gone=40)
    out = core.prune_bridge_ledger(led, {}, NOW, protect={"pending"})
    assert set(led) == {"pending"} and out["ledger_kept_protected"] == 1 and out["ledger_pruned"] == 1


def test_the_index_is_pruned_by_the_same_rule_and_unreadable_entries_are_kept():
    idx = {"o:old": NOW - 30 * H, "o:young": NOW - 2 * H, "o:bad": "??", "o:exact": NOW - 24 * H}
    out = core.prune_bridge_ledger({}, idx, NOW)
    assert set(idx) == {"o:young", "o:bad", "o:exact"} and out["index_pruned"] == 1 and out["index_kept_bad_ts"] == 1


def test_an_empty_ledger_is_fine_and_nothing_else_is_touched():
    out = core.prune_bridge_ledger({}, {}, NOW)
    assert out["ledger_pruned"] == 0 and out["index_pruned"] == 0


def test_a_big_backlog_is_cleared_in_one_pass_and_the_young_rows_survive():
    led = {f"old{i}": {"ts": NOW - 72 * H} for i in range(3000)}
    led.update({f"new{i}": {"ts": NOW - 1 * H} for i in range(500)})
    out = core.prune_bridge_ledger(led, {}, NOW)
    assert out["ledger_pruned"] == 3000 and len(led) == 500 and all(k.startswith("new") for k in led)


# ── through the REAL daily run ────────────────────────────────────────────────────────────────────────────────
@pytest.fixture
def mw(monkeypatch, tmp_path):
    m = _load_mw_real(monkeypatch)
    m.vol = Spy(tmp_path / "vol")
    monkeypatch.setattr(m, "_archive_store", lambda: m.vol)
    monkeypatch.setattr(m, "_ping_healthcheck", lambda *a, **k: (True, None))
    now = time.time()
    m.BRIDGE_LEDGER["R23"] = {"to": "x", "ts": now - 23 * H}
    m.BRIDGE_LEDGER["R25"] = {"to": "x", "ts": now - 25 * H}
    m.BRIDGE_LEDGER["PENDING-OLD"] = {"to": "x", "ts": now - 50 * H}
    m.PENDING_ROWS["PENDING-OLD"] = "2026-11/some-row.json"
    m.LEDGER_INDEX["o:R23"] = now - 23 * H
    m.LEDGER_INDEX["o:R25"] = now - 25 * H
    return m


def test_the_daily_run_prunes_the_ledger_and_the_index_and_reports_it(mw):
    out = mw.run_archive.get_raw_f()()
    assert set(mw.BRIDGE_LEDGER.keys()) == {"R23", "PENDING-OLD"}, "23 h kept, 25 h removed, the awaited row kept"
    assert set(mw.LEDGER_INDEX.keys()) == {"o:R23"}
    assert out["ledger_pruned"] == 1 and out["ledger_kept_protected"] == 1 and out["index_pruned"] == 1


def test_the_prune_summary_reaches_health(mw):
    mw.run_archive.get_raw_f()()
    assert mw._archive_health()["last_summary"]["ledger_pruned"] == 1


def test_PLANT_a_prune_failure_is_visible_and_never_fails_or_blocks_the_archive(mw, monkeypatch):
    def boom(*a, **k):
        raise RuntimeError("dict down")
    monkeypatch.setattr(core, "prune_bridge_ledger", boom)                      # core here is the module the loaded app calls only if shared; patch both ways below
    import test_evidence_guard as teg
    monkeypatch.setattr(teg.hc, "prune_bridge_ledger", boom)
    out = mw.run_archive.get_raw_f()()
    assert out.get("ledger_prune_error") == "RuntimeError" and "ledger_pruned" not in out
    assert mw.ARCHIVE_STATE["last"]["ok"] is True, "the archive itself still succeeded and was recorded"
    assert set(mw.BRIDGE_LEDGER.keys()) == {"R23", "R25", "PENDING-OLD"}, "and nothing was deleted"
