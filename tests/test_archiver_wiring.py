# -*- coding: utf-8 -*-
"""THE ARCHIVER, THROUGH THE REAL `run_archive` (2026-11-26): the single Volume writer, the move-before-remove item F, the bridge-auth keep-alive, the
dead-man ping, the daily spawn from the reconcile tick, and /health.

Plants (R26): a failure anywhere keeps the Dict copy AND pings /fail (never /ok); the auth keep-alive is OBSERVED reading every key (a counting Dict), and a
no-op replacement is shown to fail the same assertion; a held lock means nothing is written.
"""
import datetime as dt
import os
import sys
import time

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _load_mw as _load_mw_real, hc  # noqa: E402  (hc: the handler_core copy the loaded app uses)
from test_archive_core import item, Spy, NOW  # noqa: E402,F401

UTC = dt.timezone.utc


class CountingDict(dict):
    """A modal.Dict stand-in that records which keys were READ (get / index): the only way to see that a keep-alive actually touches them."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.reads = []

    def get(self, k, default=None):
        self.reads.append(k)
        return super().get(k, default)

    def __getitem__(self, k):
        self.reads.append(k)
        return super().__getitem__(k)

    def put(self, key, value, *, skip_if_exists=False):
        if skip_if_exists and key in self:
            return False
        self[key] = value
        return True


@pytest.fixture
def mw(monkeypatch, tmp_path):
    m = _load_mw_real(monkeypatch)
    m.vol = Spy(tmp_path / "vol")
    monkeypatch.setattr(m, "_archive_store", lambda: m.vol)
    monkeypatch.setattr(m, "BRIDGE_AUTH", CountingDict({f"auth-{i}": f"v{i}" for i in range(5)}))
    m.pings, m.ping_labels = [], []
    monkeypatch.setattr(m, "_ping_healthcheck", lambda kind, body="", url_env="HEALTHCHECK_PING_URL", user_agent=None:
                        (m.pings.append((kind, url_env)) or m.ping_labels.append(user_agent) or (True, None)))
    # seed: an old decided item (must move), a pending one and a recent decided one (must stay)
    m.old = item(1, "sent", days_ago=9)
    m.pend = item(2, "pending", days_ago=9)
    m.recent = item(3, "sent", days_ago=0)
    for it in (m.old, m.pend, m.recent):
        m.REVIEW_QUEUE[it["review_id"]] = it
    return m


def _live_now(m):
    """Seed timestamps are relative to NOW (2026-11-26 12:00Z); the function uses the real clock, so rebase the three seeded items onto it."""
    shift = dt.datetime.now(UTC) - NOW
    for it in (m.old, m.pend, m.recent):
        for k in ("decided_ts", "ts_held"):
            it[k] = (dt.datetime.fromisoformat(it[k]) + shift).isoformat(timespec="seconds")
        m.REVIEW_QUEUE[it["review_id"]] = it


def test_the_real_run_moves_old_decided_items_and_leaves_pending_and_recent(mw):
    _live_now(mw)
    out = mw.run_archive.get_raw_f()()
    assert mw.old["review_id"] not in mw.REVIEW_QUEUE and mw.pend["review_id"] in mw.REVIEW_QUEUE and mw.recent["review_id"] in mw.REVIEW_QUEUE
    assert mw.vol.exists(core.archive_relpath("review", mw.old["sender_hash"], mw.old["review_id"]))
    assert out["review_removed"] == 1 and out["review_archived"] == 1
    ev = mw.vol.events
    assert "commit" in ev and ev.index("write") < ev.index("commit")


def test_the_hot_scan_is_smaller_after_the_run(mw):
    _live_now(mw)
    before = len(mw._queue_items())
    mw.run_archive.get_raw_f()()
    assert before == 3 and len(mw._queue_items()) == 2, "the sweeper and /health now scan only the hot items"


def test_the_bridge_auth_keep_alive_is_observed_reading_every_key(mw):
    _live_now(mw)
    mw.BRIDGE_AUTH.reads.clear()
    out = mw.run_archive.get_raw_f()()
    assert out["auth_keys_touched"] == 5 and set(mw.BRIDGE_AUTH.reads) == {f"auth-{i}" for i in range(5)}


def test_PLANT_without_the_touch_the_same_assertion_fails(mw, monkeypatch):
    _live_now(mw)
    monkeypatch.setattr(mw, "_touch_auth_keys", lambda: 0)
    mw.BRIDGE_AUTH.reads.clear()
    mw.run_archive.get_raw_f()()
    assert set(mw.BRIDGE_AUTH.reads) != {f"auth-{i}" for i in range(5)}, "the control can fail: no touch, no reads"


def test_a_success_pings_ok_to_the_ARCHIVE_check_and_records_the_run(mw):
    _live_now(mw)
    mw.run_archive.get_raw_f()()
    assert mw.pings == [("ok", "HEALTHCHECK_ARCHIVE_URL")], "the dead-man check, not the bridge or canary one"
    assert mw.ping_labels == ["chike-archive"], "and labelled as itself, not as the bridge watcher"
    assert mw.ARCHIVE_STATE["last"]["ok"] is True and "lock" not in mw.ARCHIVE_STATE, "recorded, and the lock was released"


def test_PLANT_a_failed_run_pings_FAIL_keeps_the_item_records_the_error_and_releases_the_lock(mw):
    _live_now(mw)
    mw.vol.fail_write = True
    with pytest.raises(OSError):
        mw.run_archive.get_raw_f()()
    assert mw.pings == [("fail", "HEALTHCHECK_ARCHIVE_URL")] and mw.old["review_id"] in mw.REVIEW_QUEUE
    assert mw.ARCHIVE_STATE["last_error"]["error_class"] == "OSError" and "lock" not in mw.ARCHIVE_STATE
    assert "last" not in mw.ARCHIVE_STATE, "a failed run is never recorded as the last good one"


def test_PLANT_a_commit_failure_after_the_write_still_keeps_the_item(mw):
    _live_now(mw)
    mw.vol.fail_commit = True
    with pytest.raises(OSError):
        mw.run_archive.get_raw_f()()
    assert mw.old["review_id"] in mw.REVIEW_QUEUE and mw.pings[-1][0] == "fail"


def test_a_held_lock_means_nothing_is_written_and_nothing_is_pinged(mw):
    _live_now(mw)
    mw.ARCHIVE_STATE["lock"] = {"token": "someone-else", "ts": time.time()}
    out = mw.run_archive.get_raw_f()()
    assert out == {"skipped": "locked"} and mw.old["review_id"] in mw.REVIEW_QUEUE and mw.pings == [] and not mw.vol.exists("archive")
    assert mw.ARCHIVE_STATE["lock"]["token"] == "someone-else", "it did not steal a live lock"


def test_a_stale_lock_is_stolen(mw):
    _live_now(mw)
    mw.ARCHIVE_STATE["lock"] = {"token": "dead", "ts": time.time() - 4000}
    assert mw.run_archive.get_raw_f()().get("review_removed") == 1


# ── the daily spawn, and /health ────────────────────────────────────────────────────────────────────────────
def _stub_run_archive(mw, monkeypatch):
    calls = []

    class _F:
        @staticmethod
        def spawn():
            calls.append(1)
    monkeypatch.setattr(mw, "run_archive", _F)
    return calls


def _ts(h, m):
    return dt.datetime(2026, 11, 27, h, m, tzinfo=UTC).timestamp()


def test_the_tick_spawns_the_archiver_once_inside_the_window_and_never_outside(mw, monkeypatch):
    calls = _stub_run_archive(mw, monkeypatch)
    assert mw._maybe_spawn_archive(_ts(1, 19)) is None and mw._maybe_spawn_archive(_ts(1, 50)) is None and calls == []
    assert mw._maybe_spawn_archive(_ts(1, 25)) == "2026-11-27" and calls == [1]
    assert mw._maybe_spawn_archive(_ts(1, 30)) is None and calls == [1], "a second tick the same day does not spawn a second run"
    assert mw._maybe_spawn_archive(dt.datetime(2026, 11, 28, 1, 25, tzinfo=UTC).timestamp()) == "2026-11-28", "the next day does"


def test_the_window_boundaries_and_the_overdue_rule():
    assert not core.archive_due(_ts(1, 19), False) and core.archive_due(_ts(1, 20), False) and core.archive_due(_ts(1, 49), False) and not core.archive_due(_ts(1, 50), False)
    assert not core.archive_due(_ts(1, 30), True), "already claimed"
    assert core.archive_overdue(None, 1e9) and core.archive_overdue("junk", 1e9)
    assert not core.archive_overdue(1e9 - 35 * 3600, 1e9) and core.archive_overdue(1e9 - 37 * 3600, 1e9)


def test_the_reconcile_tick_spawns_the_archiver_and_no_cron_slot_was_taken():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    code = [ln for ln in src.splitlines() if not ln.strip().startswith("#")]
    assert any("_maybe_spawn_archive(now)" in ln for ln in code), "the tick must call it"
    assert sum(1 for ln in code if "schedule=_sched(" in ln) == 4, "still four scheduled functions (the workspace limit is 5; the archiver rides the tick)"


def test_health_reports_never_ran_then_the_last_run_and_whether_the_dead_man_is_configured(mw, monkeypatch):
    monkeypatch.delenv("HEALTHCHECK_ARCHIVE_URL", raising=False)
    h = mw._archive_health()
    assert h["last_ok_age_s"] is None and h["overdue"] is True and h["dead_man_configured"] is False
    _live_now(mw)
    mw.run_archive.get_raw_f()()
    monkeypatch.setenv("HEALTHCHECK_ARCHIVE_URL", "https://hc-ping.example/SECRET-UUID")
    h2 = mw._archive_health()
    assert h2["overdue"] is False and h2["last_ok_age_s"] < 60 and h2["dead_man_configured"] is True
    assert "SECRET-UUID" not in str(h2), "the check URL is a credential: /health says configured, never the value"
    assert mw.health.get_raw_f()()["archive"]["overdue"] is False, "and it is part of the real /health payload"
