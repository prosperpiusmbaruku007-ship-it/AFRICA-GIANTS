# -*- coding: utf-8 -*-
"""FUTA: DELETION ON REQUEST (item E, 2026-11-26), through the REAL handler functions.

The founder's condition: a deleted sender must be gone from BOTH stores, the hot Dicts and the archive Volume, with plants that prove it. Proved here by one
residue scan over every Dict store and every archive file, run before (it must find the sender: the scan is not inert), and after (it must find nothing),
beside the other sender, who must still be there in full. Plants: a Dict-only delete leaves archive residue the scan reports; a failed Volume delete is
queued and finished by the daily archiver; confirmation is required, and expires; the number-less purge cannot delete anyone else's records.
"""
import json
import os
import sys
import time
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _load_mw as _load_mw_real, _run, hc  # noqa: E402
from test_archive_core import item, Spy, NOW  # noqa: E402

A = "255700000099@s.whatsapp.net"
B = "255799000111@s.whatsapp.net"
A_DIGITS, B_DIGITS = "255700000099", "255799000111"


@pytest.fixture
def mw(monkeypatch, tmp_path):
    m = _load_mw_real(monkeypatch)
    m.vol = Spy(tmp_path / "vol")
    monkeypatch.setattr(m, "_archive_store", lambda: m.vol)
    m.sent = []

    async def fake_send(to, text):
        m.sent.append(text)
        return True, None
    monkeypatch.setattr(m, "_send_once", fake_send)

    async def vol_delete(hashes):
        return m.archive_delete_senders.get_raw_f()(list(hashes))
    monkeypatch.setattr(m, "_futa_volume_delete", vol_delete)
    monkeypatch.setattr(m, "_ping_healthcheck", lambda *a, **k: (True, None))
    m.h = {A: core.sender_ids(A, "salt")[0], B: core.sender_ids(B, "salt")[0]}
    for s in (A, B):
        _seed(m, s)
    return m


def _seed(m, jid):
    """Records for one sender in EVERY store, plus archive files for older decided items and transcripts."""
    h = m.h[jid] if hasattr(m, "h") and jid in m.h else core.sender_ids(jid, "salt")[0]
    tk1, tk2 = f"2026-11/{h}-1.json", f"2026-11/{h}-2.json"
    m.TRANSCRIPTS[tk1] = {"ts": "2026-11-25T10:00:00+00:00", "kind": "question", "sender_hash": h, "sender_tail": "9999", "question": f"SWALI-{h}"}
    m.TRANSCRIPTS[tk2] = {"ts": "2026-11-26T10:00:00+00:00", "kind": "question", "sender_hash": h, "sender_tail": "9999", "question": "q2",
                          "send_error": "PENDING_RECEIPT: id=MSG" + h[:4]}
    m.PENDING_ROWS["MSG" + h[:4]] = tk2
    rid = f"2026-11-26T09:00:00+00:00-{h[:8]}"
    m.REVIEW_QUEUE[rid] = {"review_id": rid, "status": "pending", "sender": jid, "sender_hash": h, "sender_tail": "9999", "question": "hot", "ts_held": "2026-11-26T09:00:00+00:00"}
    m.AUTOSEND["auto:" + rid] = "t"
    m.AUTOSEND["hold:" + rid] = "t"
    m.DISCLOSURES[h] = {"state": "delivered"}
    m.DAILY_LIMIT[f"2026-11-26:{h}:1"] = "t"
    m.DAILY_LIMIT[f"2026-11-26:{h}:hint"] = 1
    m.DAILY_LIMIT[f"2026-11-26:{h}:notice"] = "1"
    m.INFLIGHT[h] = {"ts": 1.0}
    m.BRIDGE_LEDGER["LEDGER-" + h[:4]] = {"to": jid, "ts": 1, "status": "delivered", "rank": 3}
    m.LEDGER_INDEX[core.ledger_index_key(core.ledger_owner_hash(jid, "salt"), "LEDGER-" + h[:4])] = time.time()      # what _send_once_bridge records at send time
    old = item(1, "sent", days_ago=9, sh=h)
    core.archive_run(review_items={old["review_id"]: old}, transcripts={f"2026-11/{h}-old.json": {"ts": "2026-11-20T10:00:00+00:00", "kind": "question",
                     "sender_hash": h, "question": "archived q"}}, store=m.vol, signing_key="k", now=NOW)


def _dict_stores(m):
    return m._futa_stores()


def _archive_residue(m, h, digits):
    needles = {h, digits}
    out = []
    for dp, _, fs in os.walk(m.vol.root):
        for f in fs:
            p = os.path.join(dp, f)
            if os.sep + "tombstones" + os.sep in p:
                continue
            text = open(p, "rb").read().decode("utf-8", "replace")
            if any(n in p or n in text for n in needles):
                out.append(p)
    return out


def all_residue(m, jid):
    h, digits = m.h[jid], jid.split("@")[0]
    lh = [core.ledger_owner_hash(jid, "salt")]
    ids = core.ledger_ids_for(list(m.LEDGER_INDEX.keys()), lh)
    return {"dicts": core.futa_residue(_dict_stores(m), [h], digits, lh, ids), "archive": _archive_residue(m, h, digits)}


def _futa_all(m, jid):
    _run(m.futa_request.get_raw_f()(jid))
    return _run(m.futa_confirm.get_raw_f()(jid))


# ── classification and dispatch ─────────────────────────────────────────────────────────────────────────────
@pytest.mark.parametrize("text,expected", [("FUTA", True), ("futa", True), (" Futa! ", True), ("nifute", False), ("futa akaunti", False),
                                           ("Habari", False), ("NDIO", False)])
def test_only_the_exact_word_futa_is_a_deletion_request(text, expected):
    assert core.futa_word(text) is expected
    assert core.futa_confirm_word("NDIO") and core.futa_confirm_word("ndiyo.") and not core.futa_confirm_word("ndio sawa")


def _webhook(mw, monkeypatch, text, sender=A):
    calls = []
    for name in ("futa_request", "futa_confirm", "answer_and_send", "greet_and_send"):
        monkeypatch.setitem(mw.__dict__, name, types.SimpleNamespace(spawn=lambda *a, _n=name, **k: calls.append(_n)))
    mw.webhook.get_raw_f()({"event": "messages.received", "data": {"messages": {"key": {"remoteJid": sender, "fromMe": False}, "conversation": text}}})
    return calls


def test_the_webhook_routes_futa_to_the_request_and_ndio_to_the_confirmation_only_when_one_is_pending(mw, monkeypatch):
    assert _webhook(mw, monkeypatch, "FUTA") == ["futa_request"]
    assert _webhook(mw, monkeypatch, "NDIO") == ["answer_and_send"], "NDIO with nothing pending is an ordinary message: nothing is deleted"
    mw.FUTA_PENDING[mw.h[A]] = {"ts": time.time()}
    assert _webhook(mw, monkeypatch, "NDIO") == ["futa_confirm"]
    assert _webhook(mw, monkeypatch, "PAYE ni nini?") == ["answer_and_send"] and _webhook(mw, monkeypatch, "Habari") == ["greet_and_send"]


def test_a_pending_request_does_not_make_other_senders_ndio_a_confirmation(mw, monkeypatch):
    mw.FUTA_PENDING[mw.h[A]] = {"ts": time.time()}
    assert _webhook(mw, monkeypatch, "NDIO", sender=B) == ["answer_and_send"]


# ── step 1 deletes nothing; confirmation is required and expires ─────────────────────────────────────────────
def test_the_request_asks_for_confirmation_and_deletes_nothing(mw):
    before = all_residue(mw, A)
    assert before["dicts"] and before["archive"], "positive control: the scan finds the sender in the Dicts AND the archive before any deletion"
    n_rows = len(mw.TRANSCRIPTS)
    _run(mw.futa_request.get_raw_f()(A))
    assert mw.sent == [core.FUTA_PROMPT_TEXT] and mw.h[A] in mw.FUTA_PENDING
    assert all_residue(mw, A)["dicts"] and all_residue(mw, A)["archive"] and len(mw.TRANSCRIPTS) == n_rows


def test_PLANT_a_confirmation_with_no_request_deletes_nothing(mw):
    out = _run(mw.futa_confirm.get_raw_f()(A))
    assert out == {"status": "expired"} and all_residue(mw, A)["dicts"] and mw.sent == []


def test_PLANT_a_confirmation_after_ten_minutes_deletes_nothing(mw):
    mw.FUTA_PENDING[mw.h[A]] = {"ts": time.time() - 700}
    assert _run(mw.futa_confirm.get_raw_f()(A)) == {"status": "expired"} and all_residue(mw, A)["dicts"]


# ── the deletion: gone from both stores, the other sender untouched ──────────────────────────────────────────
def test_a_confirmed_deletion_removes_the_sender_from_every_dict_and_the_archive_and_nobody_else(mw):
    b_before = all_residue(mw, B)
    out = _futa_all(mw, A)
    assert out["status"] == "done"
    after = all_residue(mw, A)
    assert after == {"dicts": [], "archive": []}, f"a deleted sender is gone from BOTH stores: {after}"
    assert all_residue(mw, B) == b_before and b_before["dicts"] and b_before["archive"], "the other sender is untouched, in full"
    assert mw.sent[-1] == core.FUTA_DONE_TEXT and mw.sent[0] == core.FUTA_PROMPT_TEXT


def test_every_store_actually_lost_records_not_just_the_obvious_one(mw):
    counts = _futa_all(mw, A)["counts"]
    for name in ("transcripts", "review", "pending_rows", "disclosures", "daily", "inflight", "autosend", "bridge_ledger", "ledger_index", "futa_pending"):
        assert counts[name] >= 1, f"{name}: nothing was deleted, so the purge does not reach it ({counts})"


def test_PLANT_a_dict_only_delete_leaves_archive_residue_and_the_scan_reports_it(mw):
    core.futa_purge(_dict_stores(mw), [mw.h[A]], A_DIGITS, [core.ledger_owner_hash(A, "salt")])      # what an implementation that forgot the Volume would do
    r = all_residue(mw, A)
    assert r["dicts"] == [] and r["archive"], "the archive scan is not inert: it finds exactly what the naive delete leaves"


def test_a_tombstone_is_left_and_stops_a_lingering_copy_coming_back(mw):
    _futa_all(mw, A)
    assert core.is_tombstoned(mw.vol, mw.h[A])
    ghost = item(7, "sent", days_ago=9, sh=mw.h[A])                         # a copy an in-flight run had read before the deletion
    live = dict(ghost)
    mw.REVIEW_QUEUE[ghost["review_id"]] = live
    import datetime as dt
    shift = dt.datetime.now(dt.timezone.utc) - NOW
    for k in ("decided_ts", "ts_held"):
        live[k] = (dt.datetime.fromisoformat(live[k]) + shift).isoformat(timespec="seconds")
    mw.run_archive.get_raw_f()()
    assert ghost["review_id"] not in mw.REVIEW_QUEUE and all_residue(mw, A) == {"dicts": [], "archive": []}


def test_the_deletion_log_and_the_aggregates_hold_no_text_no_hash_no_number(mw):
    _futa_all(mw, A)
    logs = [v for k, v in mw.ARCHIVE_STATE.items() if str(k).startswith("futa:")]
    assert len(logs) == 1 and logs[0]["verified"] is True
    blob = json.dumps(logs[0])
    for forbidden in (mw.h[A], A_DIGITS, "@s.whatsapp.net", "SWALI"):
        assert forbidden not in blob
    # the aggregates were counted from the archived records of both senders, and carry nothing of either
    agg = os.path.join(mw.vol.root, "archive", "aggregates")
    for f in os.listdir(agg):
        text = open(os.path.join(agg, f), encoding="utf-8").read()
        assert mw.h[A] not in text and mw.h[B] not in text and "SWALI" not in text


def test_the_flow_writes_no_transcript_row_for_the_sender(mw):
    _futa_all(mw, A)
    assert not [r for r in mw.TRANSCRIPTS.values() if isinstance(r, dict) and r.get("sender_hash") == mw.h[A]], "deleting must not create a new record of them"
    assert any(r.get("sender_hash") == mw.h[B] for r in mw.TRANSCRIPTS.values() if isinstance(r, dict))


# ── failure: queued, finished by the daily archiver ──────────────────────────────────────────────────────────
def test_PLANT_a_failed_archive_deletion_says_incomplete_queues_a_retry_and_the_daily_run_finishes_it(mw, monkeypatch):
    async def boom(hashes):
        raise OSError("volume unavailable")
    monkeypatch.setattr(mw, "_futa_volume_delete", boom)
    out = _futa_all(mw, A)
    assert out["status"] == "incomplete" and mw.sent[-1] == core.FUTA_INCOMPLETE_TEXT and core.FUTA_DONE_TEXT not in mw.sent
    assert f"futa_retry:{mw.h[A]}" in mw.ARCHIVE_STATE and all_residue(mw, A)["dicts"] == [] and all_residue(mw, A)["archive"], "Dicts purged, archive still to do"
    summary = mw.run_archive.get_raw_f()()
    assert summary["futa_retries_done"] == 1 and f"futa_retry:{mw.h[A]}" not in mw.ARCHIVE_STATE
    assert all_residue(mw, A) == {"dicts": [], "archive": []} and core.is_tombstoned(mw.vol, mw.h[A])


def test_the_participant_is_never_told_done_when_residue_remains(mw, monkeypatch):
    real_purge = core.futa_purge
    monkeypatch.setattr(hc, "futa_purge", lambda stores, hashes, digits, ledger_hashes=(): {k: 0 for k in real_purge(stores, [], "")})   # a purge that deletes nothing
    out = _futa_all(mw, A)
    assert out["status"] == "incomplete" and core.FUTA_DONE_TEXT not in mw.sent, "the verification, not the purge's own report, decides what the participant is told"


# ── the purge cannot reach anyone else ──────────────────────────────────────────────────────────────────────
def test_a_purge_with_no_usable_identifier_deletes_nothing(mw):
    before = {n: len(list(d.keys())) for n, d in _dict_stores(mw).items()}
    counts = core.futa_purge(_dict_stores(mw), ["not-a-hash", "", None], "")
    assert sum(counts.values()) == 0 and {n: len(list(d.keys())) for n, d in _dict_stores(mw).items()} == before
    counts2 = core.futa_purge(_dict_stores(mw), [], "1234")                  # a short digit string must not match anything either
    assert sum(counts2.values()) == 0
    assert sum(core.futa_purge(_dict_stores(mw), [mw.h[A]], A_DIGITS).values()) > 0, "positive control: a real identifier does delete"


def test_archive_deletion_waits_for_the_single_writer_lock_then_proceeds(mw, monkeypatch):
    mw.ARCHIVE_STATE["lock"] = {"token": "the-daily-archiver", "ts": time.time()}
    monkeypatch.setattr(time, "sleep", lambda s: mw.ARCHIVE_STATE.pop("lock", None))      # the archiver finishes while we wait
    res = mw.archive_delete_senders.get_raw_f()([mw.h[A]])
    assert res["ok"] is True and _archive_residue(mw, mw.h[A], A_DIGITS) == []


def test_archive_deletion_gives_up_cleanly_if_the_lock_never_frees(mw, monkeypatch):
    import itertools
    tick = itertools.count(0, 100)
    monkeypatch.setattr(mw, "_archive_lock_acquire", lambda token, ttl_s=0: False)
    monkeypatch.setattr(time, "sleep", lambda s: None)
    monkeypatch.setattr(time, "time", lambda: next(tick))
    assert mw.archive_delete_senders.get_raw_f()([mw.h[A]]) == {"ok": False, "error": "archiver busy"}
