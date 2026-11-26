# -*- coding: utf-8 -*-
"""FUTA AT SCALE (2026-11-27). The first live FUTA took 7 min 46 s because the bridge ledger (3,534 rows) was read in full three times, and the function's 600 s timeout was
within ~2 minutes of being overrun. Now: an immediate acknowledgement before any scan, the ledger handled BY KEY through a send-time index, verification through the index, a
1800 s timeout, and a second NDIO swallowed instead of becoming a question.

The assertion that matters is a READ COUNT, not a stopwatch: with a 5,000-row ledger the deletion reads (almost) none of it. Plants: the same counter is shown to see 5,000 reads
when the ledger IS scanned; an ack sent after the purge fails the ordering check; a ledger row sent before the index existed is the documented limit."""
import ast
import os
import sys
import time

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _run, hc  # noqa: E402
from test_futa import mw, _futa_all, A, B, A_DIGITS, B_DIGITS  # noqa: E402,F401

N_LEDGER = 5000


class CountingLedger(dict):
    """A modal.Dict stand-in that counts every ROW it hands out (get, index, items) and every listing, so 'did not scan the ledger' is a number."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.row_reads, self.listings = 0, 0

    def get(self, k, default=None):
        self.row_reads += 1
        return super().get(k, default)

    def __getitem__(self, k):
        self.row_reads += 1
        return super().__getitem__(k)

    def items(self):
        self.listings += 1
        self.row_reads += len(self)
        return super().items()

    def keys(self):
        self.listings += 1
        return super().keys()

    def put(self, key, value, *, skip_if_exists=False):
        if skip_if_exists and key in self:
            return False
        self[key] = value
        return True


class KeyOnly(dict):
    """The index: counts value reads (there must be none) and key listings."""

    def __init__(self, *a, **k):
        super().__init__(*a, **k)
        self.value_reads, self.listings = 0, 0

    def get(self, k, default=None):
        self.value_reads += 1
        return super().get(k, default)

    def __getitem__(self, k):
        self.value_reads += 1
        return super().__getitem__(k)

    def items(self):
        self.listings += 1
        self.value_reads += len(self)
        return super().items()

    def keys(self):
        self.listings += 1
        return super().keys()

    def put(self, key, value, *, skip_if_exists=False):
        if skip_if_exists and key in self:
            return False
        self[key] = value
        return True


@pytest.fixture
def big(mw, monkeypatch):
    """A 5,000-row ledger of OTHER people's sends plus sender A's three indexed rows."""
    ledger, index = CountingLedger(), KeyOnly()
    other_owner = core.ledger_owner_hash(B, "salt")
    for i in range(N_LEDGER):
        ledger[f"OTHER-{i}"] = {"to": f"2557{i:08d}@s.whatsapp.net", "ts": 1, "rank": 3}
        index[core.ledger_index_key(other_owner, f"OTHER-{i}")] = 1.0
    a_owner = core.ledger_owner_hash(A, "salt")
    for j in range(3):
        ledger[f"MINE-{j}"] = {"to": A, "ts": 1, "rank": 3}
        index[core.ledger_index_key(a_owner, f"MINE-{j}")] = 1.0
    monkeypatch.setattr(mw, "BRIDGE_LEDGER", ledger)
    monkeypatch.setattr(mw, "LEDGER_INDEX", index)
    return mw, ledger, index


def test_a_deletion_reads_almost_none_of_a_5000_row_ledger(big):
    m, ledger, index = big
    ledger.row_reads = ledger.listings = index.value_reads = index.listings = 0
    out = _futa_all(m, A)
    assert out["status"] == "done", out
    assert ledger.listings == 0, "the ledger itself is never listed or iterated"
    assert ledger.row_reads <= 12, f"{ledger.row_reads} ledger rows were read (a scan would be {N_LEDGER}+): only the person's own 3 rows may be touched"
    assert index.value_reads == 0, "the index is KEY-ONLY: no value is ever read"
    assert 1 <= index.listings <= 6, f"index keys listed {index.listings} times"
    assert all(f"MINE-{j}" not in ledger for j in range(3)) and len(ledger) >= N_LEDGER, "the person's rows are gone and nobody else's were touched"
    assert not [k for k in index.keys() if str(k).startswith(core.ledger_owner_hash(A, "salt"))], "and their index keys are gone"


def test_PLANT_the_old_way_reads_every_row_and_the_same_counter_sees_it(big):
    m, ledger, index = big
    ledger.row_reads = 0
    list(core._safe_items(ledger))                       # what the pre-fix purge AND the pre-fix residue scan each did
    assert ledger.row_reads >= N_LEDGER, "the counter is not inert: a full scan reads all the rows"


def test_the_other_peoples_ledger_rows_and_index_keys_are_untouched(big):
    m, ledger, index = big
    before_other = {k for k in ledger if k.startswith("OTHER-")}
    _futa_all(m, A)
    assert {k for k in ledger if k.startswith("OTHER-")} == before_other
    assert sum(1 for k in index.keys() if str(k).endswith(tuple(f":OTHER-{i}" for i in (0, 4999)))) == 2


def test_a_ledger_row_sent_before_the_index_existed_is_the_documented_limit(big):
    m, ledger, index = big
    ledger["PRE-INDEX"] = {"to": A, "ts": 1, "rank": 3}                  # no index key: sent before this feature
    out = _futa_all(m, A)
    assert out["status"] == "done" and "PRE-INDEX" in ledger, "invisible to a key-based deletion; the 24 h prune removes it (runbook 6a)"


# ── the acknowledgement ──────────────────────────────────────────────────────────────────────────────────────
def _sent_when_each_scan_starts(mw, monkeypatch):
    """What had already been sent to the participant at the moment the first purge and the first residue scan began."""
    marks = {}
    real_purge, real_residue = core.futa_purge, core.futa_residue
    monkeypatch.setattr(hc, "futa_purge", lambda *a, **k: (marks.setdefault("purge", list(mw.sent)), real_purge(*a, **k))[1])
    monkeypatch.setattr(hc, "futa_residue", lambda *a, **k: (marks.setdefault("residue", list(mw.sent)), real_residue(*a, **k))[1])
    _futa_all(mw, A)
    return marks


def test_the_ack_is_sent_before_any_scan_and_the_final_message_after_verification(mw, monkeypatch):
    marks = _sent_when_each_scan_starts(mw, monkeypatch)
    assert core.FUTA_ACK_TEXT in marks["purge"], "the ack had ALREADY been sent when the first scan began"
    assert core.FUTA_DONE_TEXT not in marks["purge"] and core.FUTA_DONE_TEXT not in marks["residue"], "'Imekamilika' is NOT sent before verification"
    assert mw.sent == [core.FUTA_PROMPT_TEXT, core.FUTA_ACK_TEXT, core.FUTA_DONE_TEXT], mw.sent


def test_PLANT_when_the_ack_is_not_sent_in_time_the_same_observation_fails(mw, monkeypatch):
    """The pre-fix behaviour: nothing was said until the end. Swallow the ack (the participant never sees it) and the SAME observation reports it missing."""
    real = mw._send_once

    async def swallow_ack(to, text):
        if text == core.FUTA_ACK_TEXT:
            return True, None                           # 'sent' as far as the caller knows, but it never reaches mw.sent: the participant heard nothing
        return await real(to, text)
    monkeypatch.setattr(mw, "_send_once", swallow_ack)
    marks = _sent_when_each_scan_starts(mw, monkeypatch)
    assert core.FUTA_ACK_TEXT not in marks["purge"], "the check can fail"


def test_the_ack_text_is_exactly_the_founders(mw):
    assert core.FUTA_ACK_TEXT == "Sawa, ninafuta taarifa zako sasa. Itachukua dakika chache; nitakujulisha ikikamilika."


def test_a_failed_ack_never_stops_the_deletion(mw, monkeypatch):
    real = mw._send_once

    async def flaky(to, text):
        if text == core.FUTA_ACK_TEXT:
            return False, "bridge unreachable"
        return await real(to, text)
    monkeypatch.setattr(mw, "_send_once", flaky)
    out = _futa_all(mw, A)
    assert out["status"] == "done" and core.FUTA_DONE_TEXT in mw.sent


# ── idempotent and safe ──────────────────────────────────────────────────────────────────────────────────────
def test_a_second_ndio_while_the_deletion_runs_is_swallowed_not_run_twice(mw):
    mw.FUTA_PENDING[mw.h[A]] = {"ts": time.time()}
    mw.ARCHIVE_STATE[f"futa_running:{mw.h[A]}"] = {"ts": time.time()}          # a run is in flight
    n = len(mw.sent)
    assert _run(mw.futa_confirm.get_raw_f()(A)) == {"status": "already_running"}
    assert len(mw.sent) == n and mw.h[A] in mw.FUTA_PENDING, "no second ack, nothing deleted by the duplicate"


def test_a_stale_running_marker_from_a_crash_is_taken_over_after_30_minutes(mw):
    mw.FUTA_PENDING[mw.h[A]] = {"ts": time.time()}
    mw.ARCHIVE_STATE[f"futa_running:{mw.h[A]}"] = {"ts": time.time() - 2000}
    assert _run(mw.futa_confirm.get_raw_f()(A))["status"] == "done"
    assert f"futa_running:{mw.h[A]}" not in mw.ARCHIVE_STATE, "and the marker is cleared when the run ends"


def test_the_running_marker_is_cleared_even_when_the_run_raises(mw, monkeypatch):
    async def boom(hashes):
        raise RuntimeError("volume down")
    monkeypatch.setattr(mw, "_futa_volume_delete", boom)
    mw.FUTA_PENDING[mw.h[A]] = {"ts": time.time()}
    _run(mw.futa_confirm.get_raw_f()(A))
    assert f"futa_running:{mw.h[A]}" not in mw.ARCHIVE_STATE


# ── the safety net ───────────────────────────────────────────────────────────────────────────────────────────
def test_futa_confirm_has_the_1800_second_timeout():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read().splitlines()
    i = next(n for n, ln in enumerate(src) if ln.startswith("async def futa_confirm"))
    deco = src[i - 1]
    assert "timeout=1800" in deco and "timeout=600" not in deco, deco
    pre_fix = deco.replace("timeout=1800", "timeout=600")
    assert "timeout=1800" not in pre_fix, "plant: the pre-fix decorator fails the same check"


# ── send-time indexing ───────────────────────────────────────────────────────────────────────────────────────
class _Resp:
    def __init__(self, status, body):
        self.status_code, self._b = status, body

    def json(self):
        return self._b


def _fake_httpx(monkeypatch, body, status=200):
    import types
    calls = []

    class _Client:
        def __init__(self, *a, **k):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, headers=None, json=None):
            calls.append(json)
            return _Resp(status, body)
    mod = types.SimpleNamespace(AsyncClient=_Client, ConnectError=OSError, ConnectTimeout=OSError)
    monkeypatch.setitem(sys.modules, "httpx", mod)
    return calls


def test_every_participant_send_is_indexed_by_the_canonical_owner_hash_and_message_id(mw, monkeypatch):
    monkeypatch.setenv("BRIDGE_SEND_TOKEN", "t")
    _fake_httpx(monkeypatch, {"ok": True, "id": "MSG123", "status": "delivery_ack", "pending": False})
    for form in (A, "+255700000099", "0700000099", "255700000099:12@s.whatsapp.net"):
        mw.LEDGER_INDEX.clear()
        assert _run(mw._send_once_bridge(form, "x"))[0] is True
        assert list(mw.LEDGER_INDEX.keys()) == [core.ledger_index_key(core.ledger_owner_hash(A, "salt"), "MSG123")], form
        assert float(list(mw.LEDGER_INDEX.values())[0]) > 1e9, "the value is the send time"


def test_a_pending_receipt_send_is_indexed_too_and_a_failed_send_is_not(mw, monkeypatch):
    monkeypatch.setenv("BRIDGE_SEND_TOKEN", "t")
    mw.LEDGER_INDEX.clear()
    _fake_httpx(monkeypatch, {"ok": False, "id": "MSG9", "status": "sent", "pending": True})
    _run(mw._send_once_bridge(A, "x"))
    assert len(mw.LEDGER_INDEX) == 1
    mw.LEDGER_INDEX.clear()
    _fake_httpx(monkeypatch, {"ok": False, "error": "not_connected"}, status=503)
    _run(mw._send_once_bridge(A, "x"))
    assert len(mw.LEDGER_INDEX) == 0, "no message id, nothing to index"


def test_reviewer_sends_are_not_indexed(mw, monkeypatch):
    monkeypatch.setenv("BRIDGE_SEND_TOKEN", "t")
    mw.LEDGER_INDEX.clear()
    _fake_httpx(monkeypatch, {"ok": True, "id": "MSGR", "status": "delivery_ack", "pending": False})
    _run(mw._send_once_bridge("255700000011@s.whatsapp.net", "card"))                 # the roster member of the loaded app
    assert len(mw.LEDGER_INDEX) == 0, "the index is for participants; it would otherwise grow with every reviewer push"


def test_an_index_failure_never_fails_the_send(mw, monkeypatch):
    monkeypatch.setenv("BRIDGE_SEND_TOKEN", "t")
    _fake_httpx(monkeypatch, {"ok": True, "id": "MSGX", "status": "delivery_ack", "pending": False})

    class _Dead(dict):
        def put(self, *a, **k):
            raise RuntimeError("store down")
    monkeypatch.setattr(mw, "LEDGER_INDEX", _Dead())
    assert _run(mw._send_once_bridge(A, "x")) == (True, None)
