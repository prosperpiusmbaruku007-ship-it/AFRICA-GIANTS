# -*- coding: utf-8 -*-
"""PARALLEL REVIEWER PUSHES, NO RECEIPT WAIT (founder, 2026-11-28, B-a). The reviewer cards used to go one reviewer at a time, each waiting for WhatsApp's delivery receipt, so N reviewers cost N receipt
waits (measured: the hold+notify step was 10-34 s on the latest builds). Now: batches of at most 4 in parallel (the bridge's pacer refuses a send queued longer than ~10 s), and a card push asks the bridge not to
wait for the receipt. Each card's WhatsApp message id is recorded for reply-to-approve.

Planted: concurrency really happens (and is capped), the no-wait hint is set for a card and ONLY a card (and never leaks into a sibling or the caller), ids do not cross between concurrent pushes, a
push that raises still propagates after the whole batch was attempted (the pinned fail-closed contract), a failed push is not counted as delivered, and a model-failure card has no reply mapping."""
import asyncio
import os
import sys
import time
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _load_mw as _load_mw_real, _run  # noqa: E402

PARTICIPANT = "255700000099@s.whatsapp.net"


def roster_env(n):
    return ",".join(f"+2557000000{10 + i}:R{i}" for i in range(n))


def make_item(draft="Jibu la mfano.", **kw):
    row = {"ts": "2026-11-28T10:00:00+00:00", "sender_hash": "abcd1234ef", "sender_tail": "0099", "question": "Swali?", "build": "t", "model_latency_ms": 1}
    it = core.review_item(row=row, sender=PARTICIPANT, draft=draft, engine_working=None, facts=["F"], review_id="2026-11-28T10:00:00+00:00-abcd1234", model_calls=1, guards=[])
    it.update(kw)
    return it


@pytest.fixture
def mw(monkeypatch):
    m = _load_mw_real(monkeypatch)
    monkeypatch.setenv("REVIEWER_ROSTER", roster_env(3))
    m.log = {"in_flight": 0, "max_in_flight": 0, "flags": [], "to": []}
    m.delay = 0.2

    async def fake_send(to, text):
        m.log["in_flight"] += 1
        m.log["max_in_flight"] = max(m.log["max_in_flight"], m.log["in_flight"])
        m.log["flags"].append(m._NO_RECEIPT_WAIT.get())
        m.log["to"].append(to)
        m._LAST_SEND_ID.set("MSG-" + to.split("@")[0])
        await asyncio.sleep(m.delay)
        m.log["in_flight"] -= 1
        return True, None
    monkeypatch.setattr(m, "_send_once", fake_send)
    return m


def test_the_cards_go_out_in_parallel_not_one_after_another(mw):
    t0 = time.monotonic()
    n = _run(mw._notify_reviewers(make_item()))
    took = time.monotonic() - t0
    assert n == 3 and mw.log["max_in_flight"] == 3, mw.log
    assert took < 0.45, f"3 pushes of 0.2 s took {took:.2f}s: they ran one after another (sequential would be 0.6 s)"


def test_PLANT_parallelism_is_capped_at_the_batch_size_but_every_reviewer_is_still_pushed(mw, monkeypatch):
    monkeypatch.setenv("REVIEWER_ROSTER", roster_env(6))
    n = _run(mw._notify_reviewers(make_item()))
    assert n == 6 and len(set(mw.log["to"])) == 6, "all six reviewers got a card"
    assert mw.log["max_in_flight"] == mw._NOTIFY_PARALLEL_MAX == 4, "never more than the bridge's pacing bound allows"


def test_a_card_push_asks_not_to_wait_for_the_receipt_and_the_hint_does_not_leak(mw):
    _run(mw._notify_reviewers(make_item()))
    assert mw.log["flags"] == [True, True, True], "every card push sets the no-wait hint"
    assert mw._NO_RECEIPT_WAIT.get() is False, "and it never leaks into the caller's context"


def test_each_cards_message_id_is_recorded_against_its_own_reviewer_and_draft(mw):
    it = make_item()
    _run(mw._notify_reviewers(it))
    assert len(mw.REVIEW_PUSHES) == 3
    for mid, rec in mw.REVIEW_PUSHES.items():
        who = mid.replace("MSG-", "") + "@s.whatsapp.net"
        assert rec["reviewer"] == who, "concurrent pushes must not read each other's message id"
        assert rec["review_id"] == it["review_id"] and rec["draft_sha"] == core.draft_digest(it["draft"]) and rec["kind"] == "card"


def test_a_model_failure_card_gets_no_reply_mapping(mw):
    _run(mw._notify_reviewers(make_item(draft="Samahani, tatizo.", fallback=True)))
    assert len(mw.REVIEW_PUSHES) == 0, "there is nothing to approve by reply on a card with no draft"


def test_a_failed_push_is_not_counted_and_a_pending_one_is(mw, monkeypatch):
    async def mixed(to, text):
        mw._LAST_SEND_ID.set("MSG-" + to.split("@")[0])
        if to.endswith("010@s.whatsapp.net"):
            return False, "bridge HTTP 502: send_threw"
        if to.endswith("011@s.whatsapp.net"):
            return False, f"{core.PENDING_RECEIPT}: id=A status=server_ack"
        return True, None
    monkeypatch.setattr(mw, "_send_once", mixed)
    assert _run(mw._notify_reviewers(make_item())) == 2, "delivered + accepted-pending count; a clean failure does not"


def test_PLANT_a_push_that_raises_still_lets_the_others_go_and_then_propagates(mw, monkeypatch):
    async def one_raises(to, text):
        if to.endswith("011@s.whatsapp.net"):
            raise ValueError("unsafe link")
        mw.log["to"].append(to)
        return True, None
    monkeypatch.setattr(mw, "_send_once", one_raises)
    with pytest.raises(ValueError):
        _run(mw._notify_reviewers(make_item()))
    assert len(mw.log["to"]) == 2, "the other two reviewers were still pushed"


def test_a_failure_to_record_the_card_id_never_fails_the_push(mw, monkeypatch):
    class Broken(dict):
        def __setitem__(self, *a):
            raise OSError("dict down")
    monkeypatch.setattr(mw, "REVIEW_PUSHES", Broken())
    assert _run(mw._notify_reviewers(make_item())) == 3


# ── the bridge call itself ────────────────────────────────────────────────────────────────────────────────
class _Resp:
    def __init__(self, status=200, body=None):
        self.status_code, self._b = status, body

    def json(self):
        return self._b


def _fake_httpx(posted, body):
    mod = types.ModuleType("httpx")

    class ConnectError(Exception):
        pass

    class ConnectTimeout(Exception):
        pass

    class AsyncClient:
        def __init__(self, timeout=None):
            pass

        async def __aenter__(self):
            return self

        async def __aexit__(self, *a):
            return False

        async def post(self, url, headers=None, json=None):
            posted.append(json)
            return _Resp(200, body)
    mod.ConnectError, mod.ConnectTimeout, mod.AsyncClient = ConnectError, ConnectTimeout, AsyncClient
    return mod


def test_the_bridge_payload_carries_the_hint_only_for_a_card_and_exposes_the_message_id(mw, monkeypatch):
    posted = []
    monkeypatch.setitem(sys.modules, "httpx", _fake_httpx(posted, {"ok": False, "id": "WA123", "status": "sent", "pending": True}))
    monkeypatch.setenv("BRIDGE_SEND_TOKEN", "t")
    ok, detail = _run(mw._send_once_bridge("255700000010@s.whatsapp.net", "x"))
    assert posted[-1] == {"to": "255700000010@s.whatsapp.net", "text": "x"}, "an ordinary send has no hint: it waits for the receipt as before"

    async def card():
        mw._NO_RECEIPT_WAIT.set(True)
        r = await mw._send_once_bridge("255700000010@s.whatsapp.net", "x")
        return r, mw._LAST_SEND_ID.get()
    (ok2, detail2), mid = _run(card())
    assert posted[-1]["wait_receipt"] is False and mid == "WA123"
    assert ok2 is False and core.is_pending_receipt(detail2), "accepted-but-pending, so the existing handling applies and nothing is resent"
