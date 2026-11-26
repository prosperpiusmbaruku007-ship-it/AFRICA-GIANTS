# -*- coding: utf-8 -*-
"""THE DURABLE ARCHIVE (pure core + item F + item D's report), 2026-11-26.

The contract each test pins (and plants):
  F  a decided review item leaves the hot Dict ONLY after its archive file is COMMITTED and READ BACK identical, and an aggregate that counts it is
     committed too. Every failure on the way keeps the Dict copy. Pending / recent / unparseable items never move.
  PII  the participant's number is never written; a reviewer's number becomes a handle; a phone address anywhere else FAILS CLOSED (kept in the Dict).
  DELETE  deleting a sender removes their files from the archive and leaves a text-free tombstone; a residue scan proves it, and the scan is shown able to
     find residue (a naive delete that skips the archive).
  D  per-route outcomes (approved unchanged / edited / withheld / auto-sent / pending), None not 0.0 when nothing was reviewed, test items counted not hidden.
"""
import datetime as dt
import json
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402

UTC = dt.timezone.utc
NOW = dt.datetime(2026, 11, 26, 12, 0, tzinfo=UTC)
KEY = "signing-key"
H1, H2 = "aaaaaaaaaaaa", "bbbbbbbbbbbb"
REVIEWER_JID = "255700000011@s.whatsapp.net"


def item(i, status="sent", route="engine:paye", days_ago=5, sh=H1, **kw):
    ts = (NOW - dt.timedelta(days=days_ago)).isoformat(timespec="seconds")
    d = {"review_id": f"{ts}-{sh[:8]}-{i}", "status": status, "sender": f"2557{i:08d}@s.whatsapp.net", "sender_hash": sh, "sender_tail": "0000",
         "question": f"SWALI-{i}", "draft": "jibu", "final": "jibu", "decided_ts": ts, "decided_by": REVIEWER_JID, "decided_by_name": "P",
         "claimed_by": REVIEWER_JID, "decision_latency_s": 60, "answer_path": route, "ts_held": ts,
         "answer_trace": {"cls": "engine", "routes": [route.split(":")[-1]]}}
    d.update(kw)
    return d


class Spy(core.ArchiveStore):
    """Records the order of every effect, and can be made to fail or lie."""

    def __init__(self, root, **kw):
        super().__init__(root, commit=lambda: self.events.append("commit"), reload=lambda: self.events.append("reload"))
        self.events, self.fail_write, self.fail_commit, self.lie_on_read = [], False, False, False

    def write(self, rel, data):
        if self.fail_write:
            raise OSError("disk full")
        self.events.append("write")
        super().write(rel, data)

    def commit(self):
        if self.fail_commit:
            raise OSError("commit failed")
        super().commit()

    def read(self, rel):
        data = super().read(rel)
        if self.lie_on_read and data is not None and "/review/" in rel.replace("\\", "/"):
            return data + b" "                                  # what a torn or truncated write looks like on read-back
        return data


@pytest.fixture
def store(tmp_path):
    return Spy(tmp_path / "vol")


def _run(store, items, transcripts=None, now=NOW, removed=None):
    removed = [] if removed is None else removed
    rm = lambda rid: (store.events.append("remove"), removed.append(rid))   # noqa: E731
    out = core.archive_run(review_items=dict(items), transcripts=transcripts or {}, store=store, signing_key=KEY, now=now, remove_review=rm)
    return out, removed


def _all_text(store):
    out = []
    for dp, _, fs in os.walk(store.root):
        for f in fs:
            p = os.path.join(dp, f)
            out.append((p, open(p, "rb").read().decode("utf-8", "replace")))
    return out


# ── F: move before remove ────────────────────────────────────────────────────────────────────────────────────
def test_a_decided_old_item_is_archived_then_removed_and_the_order_is_proved(store):
    it = item(1)
    out, removed = _run(store, {it["review_id"]: it})
    assert removed == [it["review_id"]] and out["review_archived"] == 1 and out["review_removed"] == 1
    ev = store.events
    assert ev.index("remove") > max(i for i, e in enumerate(ev) if e == "commit") - 0, "removal only after the last commit"
    first_commit = ev.index("commit")
    assert ev.index("write") < first_commit < ev.index("remove"), f"write -> commit -> remove, got {ev}"
    rel = core.archive_relpath("review", H1, it["review_id"])
    assert json.loads(store.read(rel))["question"] == "SWALI-1", "the content (the corpus) is kept"


@pytest.mark.parametrize("it", [item(1, status="pending"), item(2, days_ago=1), item(3, status="sent", decided_ts="not a date", ts_held="also not")],
                         ids=["pending", "decided-yesterday", "unparseable-timestamp"])
def test_pending_recent_and_unparseable_items_never_move(store, it):
    out, removed = _run(store, {it["review_id"]: it})
    assert removed == [] and out["review_archived"] == 0 and not store.exists("archive")


def test_PLANT_a_write_failure_keeps_the_item_in_the_dict(store):
    it = item(1)
    store.fail_write = True
    removed = []
    with pytest.raises(OSError):
        _run(store, {it["review_id"]: it}, removed=removed)
    assert removed == [], "nothing was removed after a failed write"


def test_PLANT_a_commit_failure_keeps_the_item_in_the_dict(store):
    it = item(1)
    store.fail_commit = True
    removed = []
    with pytest.raises(OSError):
        _run(store, {it["review_id"]: it}, removed=removed)
    assert removed == []


def test_PLANT_a_readback_mismatch_keeps_the_item_and_says_so(store):
    it = item(1)
    store.lie_on_read = True
    out, removed = _run(store, {it["review_id"]: it})
    assert removed == [] and out["review_kept_failed"] == 1 and out["review_removed"] == 0


def test_PLANT_an_aggregate_failure_keeps_every_item(store, monkeypatch):
    its = [item(1), item(2)]
    monkeypatch.setattr(core, "_merge_aggregate", lambda *a, **k: (_ for _ in ()).throw(RuntimeError("boom")))
    out, removed = _run(store, {i["review_id"]: i for i in its})
    assert removed == [] and out.get("aggregate_failed") is True and out["review_kept_failed"] == 2


def test_positive_control_the_same_run_without_a_failure_removes_both(store):
    its = [item(1), item(2)]
    out, removed = _run(store, {i["review_id"]: i for i in its})
    assert sorted(removed) == sorted(i["review_id"] for i in its)


def test_a_rerun_after_a_crash_between_commit_and_removal_removes_without_double_counting(store):
    it = item(1)
    _run(store, {it["review_id"]: it}, removed=[])                       # first run: archived + counted (the Dict removal "failed": we re-offer the item)
    out, removed = _run(store, {it["review_id"]: it})                    # second run sees it again
    assert removed == [it["review_id"]] and out["review_already_present"] == 1 and out["review_archived"] == 0
    ag = core.read_aggregates(store)
    assert len(ag) == 1 and ag[0]["routes"]["paye"]["approved_unchanged"] == 1, "counted once, not twice"


def test_a_file_that_changed_since_it_was_archived_is_kept_in_the_dict_and_never_overwritten(store):
    it = item(1)
    _run(store, {it["review_id"]: it})
    edited = dict(it, final="a later edit")
    out, removed = _run(store, {it["review_id"]: edited})
    assert removed == [] and out["review_changed_since_archive"] == 1
    assert json.loads(store.read(core.archive_relpath("review", H1, it["review_id"])))["final"] == "jibu"


# ── PII ──────────────────────────────────────────────────────────────────────────────────────────────────────
def test_the_participants_number_is_never_written_and_reviewers_become_handles(store):
    it = item(1)
    _run(store, {it["review_id"]: it})
    blob = " ".join(t for _, t in _all_text(store))
    assert "@s.whatsapp.net" not in blob and "2557" not in blob.replace(H1, "") and REVIEWER_JID.split("@")[0] not in blob
    rec = json.loads(store.read(core.archive_relpath("review", H1, it["review_id"])))
    assert rec["decided_by_handle"] == core.reviewer_handle(KEY, REVIEWER_JID) and "sender" not in rec and "decided_by" not in rec


def test_PLANT_a_phone_address_in_an_unexpected_field_fails_closed_and_stays_in_the_dict(store):
    leaky = item(1, extra_note="forwarded from 255799000111@s.whatsapp.net")
    out, removed = _run(store, {leaky["review_id"]: leaky})
    assert removed == [] and out["review_kept_leak"] == 1 and not store.exists("archive/review")
    clean = item(2)
    out2, removed2 = _run(store, {clean["review_id"]: clean})
    assert removed2 == [clean["review_id"]], "positive control: a clean item in the same run archives"


def test_paths_cannot_escape_the_archive(store):
    assert core.archive_relpath("review", "../../etc", "../../x").startswith("archive/review/_unattributed/")
    rel = core.archive_relpath("review", H1, "../../x")
    assert rel.count("/") == 3 and "\\" not in rel, rel          # archive/review/<hash>/<one file name>: every separator in the id was replaced
    with pytest.raises(ValueError):
        store.write("../outside.json", b"x")
    with pytest.raises(ValueError):
        core.archive_relpath("nonsense", H1, "x")


# ── transcripts ──────────────────────────────────────────────────────────────────────────────────────────────
def _row(days_ago, sh=H1):
    return {"ts": (NOW - dt.timedelta(days=days_ago)).isoformat(timespec="seconds"), "kind": "question", "sender_hash": sh, "sender_tail": "1111", "question": "q"}


def test_transcripts_are_archived_once_old_enough_and_are_never_removed(store):
    out, _ = _run(store, {}, transcripts={"2026-11/old.json": _row(5), "2026-11/new.json": _row(1)})
    assert out["transcripts_archived"] == 1
    assert store.exists(core.archive_relpath("transcript", H1, "2026-11/old.json")) and not store.exists(core.archive_relpath("transcript", H1, "2026-11/new.json"))


# ── tombstones and deletion ──────────────────────────────────────────────────────────────────────────────────
def _residue(store, sender_hash):
    """Every file under the archive whose PATH or CONTENT mentions this sender, excluding the tombstone (which exists to remember the deletion)."""
    found = []
    for p, text in _all_text(store):
        if os.sep + "tombstones" + os.sep in p:
            continue
        if sender_hash in p or sender_hash in text:
            found.append(p)
    return found


def _seed_two_senders(store):
    a, b = item(1, sh=H1), item(2, sh=H2)
    _run(store, {a["review_id"]: a, b["review_id"]: b}, transcripts={"2026-11/a.json": _row(5, H1), "2026-11/b.json": _row(5, H2)})
    return a, b


def test_deleting_a_sender_removes_every_archived_file_and_touches_nobody_else(store):
    a, b = _seed_two_senders(store)
    assert _residue(store, H1), "positive control: before deletion the residue scan DOES find the sender"
    out = core.delete_sender_archive(store, H1, NOW)
    assert out["verified_gone"] is True and out["removed_dirs"] == 2
    assert _residue(store, H1) == [], f"a deleted sender is gone from the archive: {_residue(store, H1)}"
    assert store.exists(core.archive_relpath("review", H2, b["review_id"])) and store.exists(core.archive_relpath("transcript", H2, "2026-11/b.json"))


def test_PLANT_a_naive_delete_that_skips_the_archive_leaves_residue_the_scan_finds(store):
    _seed_two_senders(store)
    # the 'delete' a Dict-only implementation would do: nothing under the archive is touched
    assert _residue(store, H1), "the residue scan is not inert: it reports what a naive delete leaves behind"


def test_the_deleted_sender_cannot_come_back_through_a_later_archive_run(store):
    a, _ = _seed_two_senders(store)
    core.delete_sender_archive(store, H1, NOW)
    again = item(9, sh=H1)                                                # a lingering hot copy that an in-flight run had already read
    out, removed = _run(store, {again["review_id"]: again}, transcripts={"2026-11/late.json": _row(5, H1)})
    assert removed == [again["review_id"]] and out["review_tombstoned_dropped"] == 1 and out["transcripts_archived"] == 0
    assert _residue(store, H1) == []


def test_the_tombstone_is_text_free_and_pruned_after_90_days(store):
    core.write_tombstone(store, H1, NOW)
    assert json.loads(store.read(core.tombstone_rel(H1))) == {"deleted_at": NOW.isoformat(timespec="seconds"), "sender_hash": H1}
    assert core.prune_tombstones(store, NOW + dt.timedelta(days=89)) == 0 and core.is_tombstoned(store, H1)
    assert core.prune_tombstones(store, NOW + dt.timedelta(days=91)) == 1 and not core.is_tombstoned(store, H1)


def test_a_non_hash_cannot_be_deleted_or_tombstoned(store):
    with pytest.raises(ValueError):
        core.delete_sender_archive(store, "../..", NOW)
    assert core.is_tombstoned(store, "../..") is False


# ── aggregates (text-free) and item D ────────────────────────────────────────────────────────────────────────
def test_aggregates_count_per_route_and_reviewer_and_hold_no_text_no_sender_no_id(store):
    its = [item(1, "sent"), item(2, "edited"), item(3, "withheld"), item(4, "sent", route="engine:sdl"), item(5, "auto_sent", reviewer=None)]
    its[4].pop("decided_by"), its[4].pop("claimed_by")
    _run(store, {i["review_id"]: i for i in its})
    ag = core.read_aggregates(store)
    assert len(ag) == 1
    paye = ag[0]["routes"]["paye"]
    assert paye["approved_unchanged"] == 1 and paye["edited"] == 1 and paye["withheld"] == 1 and ag[0]["routes"]["sdl"]["approved_unchanged"] == 1
    assert ag[0]["routes"]["paye"]["auto_sent"] == 1
    raw = open(os.path.join(store.root, "archive", "aggregates", os.listdir(os.path.join(store.root, "archive", "aggregates"))[0]), encoding="utf-8").read()
    for forbidden in ("SWALI", H1, "@", "2026-11-21T12:00:00+00:00-aaaaaaaa"):
        assert forbidden not in raw, f"{forbidden!r} leaked into a text-free aggregate"
    assert core.reviewer_handle(KEY, REVIEWER_JID) in ag[0]["per_reviewer"]


def test_test_items_are_counted_not_hidden_in_the_aggregate(store):
    t = item(1, test_sender=True)
    _run(store, {t["review_id"]: t})
    ag = core.read_aggregates(store)[0]
    assert ag["excluded_test"] == 1 and ag["routes"] == {}


def test_route_report_merges_hot_items_and_archived_days_and_never_reports_a_zero_rate_on_nothing(store):
    hot = [item(10, "sent", days_ago=0), item(11, "edited", days_ago=0), item(12, "pending", days_ago=0), item(13, "sent", days_ago=0, route="engine:rent_wht")]
    old = item(1, "sent", days_ago=9)
    _run(store, {old["review_id"]: old})
    rep = core.route_report(hot, core.read_aggregates(store))
    paye = rep["routes"]["paye"]
    assert paye["approved_unchanged"] == 2 and paye["edited"] == 1 and paye["pending"] == 1 and paye["reviewed"] == 3 and paye["unchanged_rate"] == 0.667
    assert rep["archived_days"] == 1
    only_pending = core.route_report([item(20, "pending", days_ago=0, route="engine:vat")])
    assert only_pending["routes"]["vat"]["unchanged_rate"] is None, "None, never 0.0: nothing has been reviewed"


def test_route_report_excludes_and_counts_test_items():
    rep = core.route_report([item(1, days_ago=0, test_sender=True), item(2, days_ago=0)])
    assert rep["excluded_test"] == 1 and rep["routes"]["paye"]["approved_unchanged"] == 1
    assert core.route_report([item(1, days_ago=0, test_sender=True)], include_test=True)["routes"]["paye"]["approved_unchanged"] == 1


def test_parse_archive_hot_days_cannot_be_zeroed_by_a_typo():
    assert core.parse_archive_hot_days("0") == 3 and core.parse_archive_hot_days("junk") == 3 and core.parse_archive_hot_days("7") == 7
