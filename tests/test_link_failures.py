"""A reviewer link that fails must say WHY, and must never say "not found" about a draft that exists (2026-11-12).

Four real links (Q2, Q3 and their re-sends) answered {"status":"not found"} while their drafts sat stored, pending and
notified. Measured: the 404s took ~75 ms, i.e. they failed AUTHENTICATION before any queue read; the page had two
different failures behind one sentence. These tests pin the three outcomes and the diagnostic -- including that no
credential value ever reaches the log.
"""
import importlib.util
import os
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hc_linkfail", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
hc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc)

KEY = "test-key"


def _load_mw(monkeypatch):
    from conftest import isolate_modal_stores
    for k, v in {"REVIEW_D_URL": "https://d.example", "REVIEW_CLAIM_URL": "https://c.example",
                 "REVIEW_ACT_URL": "https://a.example"}.items():
        monkeypatch.setenv(k, v)
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = hc
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", hc)
    spec = importlib.util.spec_from_file_location("chike_mw_linkfail", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    isolate_modal_stores(mw, monkeypatch)
    monkeypatch.setenv("SENDER_SALT", "salt")
    monkeypatch.setenv("REVIEWER_ROSTER", "+255700000011:Prosper")
    monkeypatch.setenv("REVIEW_SIGNING_KEY", KEY)
    return mw


RID = "2026-11-12T00:41:28+00:00-b5908217"


def _store(mw, rid=RID):
    mw.REVIEW_QUEUE[rid] = {"review_id": rid, "ts_held": "2026-11-12T00:41:28+00:00", "question": "q", "draft": "Ndiyo.",
                            "status": "pending", "sender_tail": "5913", "sender_hash": "abc", "facts": ["F"],
                            "engine_working": "W", "answer_path": "engine:vat_registration"}


def _creds(mw, rid=RID):
    number = mw._settings().roster[0][0]
    return hc.reviewer_id(KEY, number), hc.review_token(KEY, rid, number)


def _call(mw, **kw):
    resp = mw._d_page(kw.get("r"), kw.get("v"), kw.get("t"))
    return resp.status_code, resp.body.decode("utf-8")


def test_a_bad_token_on_an_EXISTING_draft_does_not_say_not_found(monkeypatch, capsys):
    mw = _load_mw(monkeypatch)
    _store(mw)
    v, t = _creds(mw)
    status, body = _call(mw, r=RID, v=v, t="0" * 32)
    assert status == 404
    low = body.lower()
    assert "not found" not in low and "haipatikani" not in low and "status" not in low
    assert "HAIMAANISHI rasimu imepotea" in body and "DOES NOT MEAN THE DRAFT IS LOST" in body


def test_a_wrong_token_and_an_unknown_id_look_identical_so_the_page_is_no_oracle(monkeypatch):
    mw = _load_mw(monkeypatch)
    _store(mw)
    v, t = _creds(mw)
    exists = _call(mw, r=RID, v=v, t="0" * 32)
    unknown = _call(mw, r="2026-11-12T09:09:09+00:00-deadbeef", v=v, t="0" * 32)
    assert exists == unknown, "the response must not reveal which drafts exist"


def test_the_failure_is_logged_as_SHAPES_never_values(monkeypatch, capsys):
    mw = _load_mw(monkeypatch)
    _store(mw)
    v, t = _creds(mw)
    bad_t = t[:20]                                              # a token cut short in transit
    _call(mw, r=RID, v=v, t=bad_t)
    out = capsys.readouterr().out
    assert "reason=auth_failed" in out
    assert '"t_len": 20' in out and '"t_is_hex": true' in out and '"v_is_a_roster_handle": true' in out
    assert '"r_known_to_store": true' in out, "the log must say the draft EXISTS even though the page must not"
    for secret in (t, bad_t, v, KEY):
        assert secret not in out, "a credential value reached the log"


def test_the_diagnostic_tells_apart_the_ways_a_link_can_arrive_damaged(monkeypatch, capsys):
    mw = _load_mw(monkeypatch)
    _store(mw)
    v, t = _creds(mw)
    _call(mw, r=RID, v="0" * 10, t=t)                           # a handle that is not on the roster
    assert '"v_is_a_roster_handle": false' in capsys.readouterr().out
    _call(mw, r=RID.replace("+", " "), v=v, t="zz" + t[2:])     # '+' decoded to space is fine; a non-hex token is not
    out = capsys.readouterr().out
    assert '"t_is_hex": false' in out
    _call(mw, r=RID, v=v, t=None)
    assert '"t_present": false' in capsys.readouterr().out
    _call(mw, r=None, v=v, t=t)
    assert '"r_present": false' in capsys.readouterr().out


def test_a_valid_link_for_a_draft_that_is_not_in_the_store_may_say_so(monkeypatch, capsys):
    """Authenticated, and the store genuinely holds no such id: the ONE case that may say the draft is missing."""
    mw = _load_mw(monkeypatch)
    v, t = _creds(mw)                                           # nothing stored
    status, body = _call(mw, r=RID, v=v, t=t)
    assert status == 404 and "Rasimu haipatikani" in body
    assert "reason=authenticated_but_no_such_draft" in capsys.readouterr().out


def test_a_queue_read_error_is_a_temporary_problem_not_not_found(monkeypatch, capsys):
    mw = _load_mw(monkeypatch)
    v, t = _creds(mw)

    class _Broken(dict):
        def __getitem__(self, k):
            raise RuntimeError("modal store unreachable")
    monkeypatch.setattr(mw, "REVIEW_QUEUE", _Broken())
    status, body = _call(mw, r=RID, v=v, t=t)
    assert status == 503 and "HAIJAPOTEA" in body and "NOT lost" in body
    assert "not found" not in body.lower()
    assert "reason=store_error" in capsys.readouterr().out


def test_a_valid_link_still_renders_the_draft(monkeypatch):
    mw = _load_mw(monkeypatch)
    _store(mw)
    v, t = _creds(mw)
    status, body = _call(mw, r=RID, v=v, t=t)
    assert status == 200 and "Ndiyo." in body and "engine:vat_registration" in body


# -- the stale registry entry that raised KeyError on every reconcile run, for ever ---------------------
def test_an_orphaned_pending_registry_entry_is_dropped_not_retried_for_ever(monkeypatch, capsys):
    mw = _load_mw(monkeypatch)
    mw.PENDING_ROWS["3EB00D9663105287A749CE"] = "2026-11/2026-11-11T205637+0000-b5908217c09e-f2a979.json"   # no such row
    out1 = mw.reconcile_receipts.get_raw_f()()
    assert out1["orphaned"] == 1 and "3EB00D9663105287A749CE" not in mw.PENDING_ROWS
    assert "KeyError" not in capsys.readouterr().out
    out2 = mw.reconcile_receipts.get_raw_f()()
    assert out2["orphaned"] == 0, "dropped once, not re-reported every run"


def test_a_real_pending_row_is_still_reconciled_and_an_unreceipted_one_still_waits(monkeypatch):
    mw = _load_mw(monkeypatch)
    row = {"ts": "2026-11-12T00:00:00+00:00", "sender_hash": "abc", "send_state": "pending_receipt",
           "send_error": "PENDING_RECEIPT: id=3EB0REAL status=server_ack", "send_ok": False}
    fname = hc.transcript_filename(row)
    mw.TRANSCRIPTS[fname] = row
    mw.PENDING_ROWS["3EB0REAL"] = fname
    mw.BRIDGE_LEDGER["3EB0REAL"] = {"rank": 4, "ts": 1000, "receipt_ts": 1046}
    out = mw.reconcile_receipts.get_raw_f()()
    assert out["reconciled"] == 1 and mw.TRANSCRIPTS[fname]["send_state"] == "delivered"
    mw.TRANSCRIPTS[fname] = dict(row, send_error="PENDING_RECEIPT: id=3EB0WAIT status=server_ack")
    mw.PENDING_ROWS["3EB0WAIT"] = fname
    out2 = mw.reconcile_receipts.get_raw_f()()
    assert out2["waiting"] == 1 and "3EB0WAIT" in mw.PENDING_ROWS
