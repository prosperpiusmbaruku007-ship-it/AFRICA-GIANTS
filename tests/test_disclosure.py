"""The participant disclosure (runbook 8a) is AUTOMATIC: sent once to each new sender, before the ack,
recorded in their row, never twice (founder, 2026-11-12).

"A disclosure that depends on me remembering will eventually be skipped, and dropping it voids the R7
reading." Every property below is planted: the happy path, the race, and each way the send can go wrong.
"""
import ast
import asyncio
import importlib.util
import os
import re
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "hc_disclosure", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
hc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc)

FOUNDERS_TEXT = (
    "Karibu kwenye majaribio ya Chike. Chike ni msaidizi wa maswali ya kodi na sheria za biashara Tanzania. "
    "Kwa sasa ni jaribio linalosimamiwa: kila jibu linasomwa na mtu kabla ya kutumwa kwako, hivyo jibu "
    "linaweza kuchukua muda — wakati mwingine saa kadhaa. Majibu ni mwongozo, si ushauri rasmi wa kisheria; "
    "kwa maamuzi muhimu, thibitisha na TRA au mamlaka husika. Usitume taarifa binafsi zisizo za lazima. "
    "Asante kwa kutusaidia kuiboresha Chike.")
SENDER = "255700000011@s.whatsapp.net"


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


def _settings():
    return hc.Settings(send_attempts=1, send_retry_delay_s=0, sender_salt="salt")


class _World:
    """An in-memory stand-in for the Dict + the transport, recording ORDER."""

    def __init__(self, send_result=(True, None), send_delay=0.0, claim_raises=False,
                 finish_raises=False, send_raises=False):
        self.store, self.events, self.sent = {}, [], []
        self.send_result, self.send_delay = send_result, send_delay
        self.claim_raises, self.finish_raises, self.send_raises = claim_raises, finish_raises, send_raises

    async def send_once(self, to, text):
        self.events.append("send")
        self.sent.append((to, text))
        if self.send_delay:
            await asyncio.sleep(self.send_delay)
        if self.send_raises:
            raise RuntimeError("transport down")
        return self.send_result

    def claim(self, k, v):
        if self.claim_raises:
            raise RuntimeError("store down")
        self.events.append("claim")
        if k in self.store:
            return False
        self.store[k] = v
        return True

    def peek(self, k):
        return self.store.get(k)

    def finish(self, k, v):
        if self.finish_raises:
            raise RuntimeError("store down")
        self.events.append("finish")
        self.store[k] = v

    def release(self, k):
        self.events.append("release")
        self.store.pop(k, None)

    def ensure(self, sender=SENDER):
        return hc.ensure_disclosure(sender, self.send_once, self.claim, self.peek, self.finish,
                                    self.release, _settings(), "testbuild")


# ── the text ──────────────────────────────────────────────────────────────────────────────
def test_the_disclosure_is_verbatim_the_founders_text():
    assert hc.DISCLOSURE_TEXT == FOUNDERS_TEXT


def test_the_runbook_copy_and_the_code_cannot_drift_apart():
    md = open(os.path.join(_ROOT, "chike-whatsapp", "SUPERVISED_PILOT_RUNBOOK.md"), encoding="utf-8").read()
    assert "> " + hc.DISCLOSURE_TEXT in md, "runbook 8a no longer matches DISCLOSURE_TEXT"


# ── once, recorded, before the send is confirmed ─────────────────────────────────────────
def test_a_first_message_sends_the_disclosure_once_and_records_it():
    w = _World()
    out = _run(w.ensure())
    assert w.sent == [(SENDER, hc.DISCLOSURE_TEXT)]
    assert out["disclosure_state"] == "delivered" and out["disclosure_ts"]
    assert w.events == ["claim", "send", "finish"], "the claim must be taken BEFORE the send"
    key = hc.sender_ids(SENDER, "salt")[0]
    assert w.store[key]["state"] == "delivered" and SENDER not in str(w.store), "no raw number stored"


def test_the_second_message_never_sends_it_again():
    w = _World()
    _run(w.ensure())
    out = _run(w.ensure())
    assert len(w.sent) == 1
    assert out["disclosure_state"] == "already" and out["disclosure_state"] in hc.DISCLOSURE_OK


def test_two_messages_arriving_together_send_exactly_one_disclosure():
    """The race the atomic claim exists for: both spawns start before either send finishes."""
    w = _World(send_delay=0.05)

    async def both():
        return await asyncio.gather(w.ensure(), w.ensure())
    a, b = _run(both())
    assert len(w.sent) == 1, w.sent
    assert sorted([a["disclosure_state"], b["disclosure_state"]]) == ["already", "delivered"]
    # the LOSER waited for the winner's send to settle: its finish came before the loser returned
    assert w.events.count("send") == 1 and "finish" in w.events


def test_two_different_senders_are_each_told_once():
    w = _World()
    _run(w.ensure("255700000011@s.whatsapp.net"))
    _run(w.ensure("255700000022@s.whatsapp.net"))
    _run(w.ensure("255700000022@s.whatsapp.net"))
    assert [t for t, _ in w.sent] == ["255700000011@s.whatsapp.net", "255700000022@s.whatsapp.net"]


# ── every way the send can go wrong ──────────────────────────────────────────────────────
def test_pending_receipt_counts_as_sent_and_is_never_repeated():
    """Accepted-not-receipted: a resend could duplicate a message that is on its way."""
    w = _World(send_result=(False, "PENDING_RECEIPT: id=3EB0ABC status=server_ack"))
    out = _run(w.ensure())
    assert out["disclosure_state"] == "pending_receipt" and out["disclosure_state"] in hc.DISCLOSURE_OK
    _run(w.ensure())
    assert len(w.sent) == 1


def test_a_clean_failure_releases_the_claim_so_the_next_message_retries():
    w = _World(send_result=(False, "bridge not connected (connecting)"))
    out = _run(w.ensure())
    assert out["disclosure_state"] == "failed" and out["disclosure_state"] not in hc.DISCLOSURE_OK
    assert "release" in w.events
    w.send_result = (True, None)
    out2 = _run(w.ensure())
    assert out2["disclosure_state"] == "delivered" and len(w.sent) == 2      # nothing had reached them


def test_a_transport_exception_is_a_clean_failure_not_a_crash():
    w = _World(send_raises=True)
    out = _run(w.ensure())
    assert out["disclosure_state"] == "failed" and "release" in w.events


def test_when_the_store_cannot_be_read_nothing_is_sent():
    """A missing disclosure is FLAGGED; a duplicate one cannot be unsent."""
    w = _World(claim_raises=True)
    out = _run(w.ensure())
    assert out["disclosure_state"] == "unknown" and w.sent == []


def test_losing_the_record_after_a_successful_send_does_not_trigger_a_resend(monkeypatch):
    monkeypatch.setattr(hc, "_DISCLOSURE_WAIT_S", 0.3)
    monkeypatch.setattr(hc, "_DISCLOSURE_POLL_S", 0.1)
    w = _World(finish_raises=True)
    out = _run(w.ensure())
    assert out["disclosure_state"] == "delivered" and len(w.sent) == 1
    _run(w.ensure())
    assert len(w.sent) == 1, "the claim is still held ('sending'), so a later message must not resend"


def test_a_STALE_sending_claim_does_not_make_a_participant_wait(monkeypatch):
    """A crash between claim and send leaves 'sending' for ever. Waiting on it would delay every later
    message from that participant; it must be passed immediately, still never resent."""
    import time
    from datetime import datetime, timedelta, timezone
    w = _World()
    key = hc.sender_ids(SENDER, "salt")[0]
    w.store[key] = {"state": "sending", "ts": (datetime.now(timezone.utc) - timedelta(minutes=10)).isoformat()}
    t0 = time.monotonic()
    out = _run(w.ensure())
    assert time.monotonic() - t0 < 2.0, "waited on a stale claim"
    assert out["disclosure_state"] == "already" and w.sent == []


# ── the flag: ON unless explicitly off, so a typo cannot drop it ──────────────────────────
@pytest.mark.parametrize("v,expected", [
    (None, True), ("", True), ("1", True), ("true", True), ("yes", True), ("ture", True), ("onn", True),
    ("0", False), ("false", False), ("FALSE", False), ("no", False), ("off", False), (" Off ", False)])
def test_the_flag_is_on_unless_explicitly_off(v, expected):
    assert hc.parse_disclosure_flag(v) is expected


def test_settings_default_to_disclosing():
    assert hc.Settings().disclosure_enabled is True


# ── the wiring, asserted on the deployed file's structure ────────────────────────────────
def _mw_tree():
    src = open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()
    return src, ast.parse(src)


def _fn(tree, name):
    return next(n for n in ast.walk(tree) if isinstance(n, ast.AsyncFunctionDef) and n.name == name)


def _first_call_line(fn, attr_or_name):
    lines = []
    for n in ast.walk(fn):
        if isinstance(n, ast.Call):
            f = n.func
            nm = f.attr if isinstance(f, ast.Attribute) else getattr(f, "id", None)
            if nm == attr_or_name:
                lines.append(n.lineno)
    return min(lines) if lines else None


def test_the_disclosure_runs_BEFORE_the_acks_in_both_entry_points():
    """`core.deliver` / `deliver_greeting` are what send the acks, so the disclosure call must precede them
    in the source of BOTH spawned functions -- an answer path with the disclosure and a greeting path
    without it would tell some participants and not others."""
    _, tree = _mw_tree()
    for fn_name, ack_call in (("answer_and_send", "deliver"), ("greet_and_send", "deliver_greeting")):
        fn = _fn(tree, fn_name)
        d, a = _first_call_line(fn, "_ensure_disclosure"), _first_call_line(fn, ack_call)
        assert d is not None and a is not None and d < a, (fn_name, d, a)


def test_a_reviewer_retry_does_not_send_the_disclosure_again():
    src, tree = _mw_tree()
    body = ast.get_source_segment(src, _fn(tree, "answer_and_send"))
    assert re.search(r"disclosure_enabled\s+and\s+not\s+retry_of", body)


def test_the_outcome_is_recorded_in_the_row_and_on_the_review_card():
    src, tree = _mw_tree()
    for name in ("answer_and_send", "greet_and_send"):
        assert "row.update(disclosure)" in ast.get_source_segment(src, _fn(tree, name)), name
    assert 'item["disclosure_state"]' in src and "def _disclosure_banner" in src


# ── integration against the real wiring, with the Modal Dict stubbed ──────────────────────
def _load_mw(monkeypatch):
    from conftest import isolate_modal_stores
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = hc
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", hc)
    spec = importlib.util.spec_from_file_location(
        "chike_mw_disclosure", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    names = isolate_modal_stores(mw, monkeypatch)
    assert "DISCLOSURES" in names, "the disclosure store must be one the isolation helper covers"
    return mw


def test_the_real_wiring_claims_atomically_and_sends_once(monkeypatch):
    mw = _load_mw(monkeypatch)
    sent = []

    async def fake_send(to, text):
        sent.append(text)
        return True, None
    monkeypatch.setattr(mw, "_send_once", fake_send)
    monkeypatch.setenv("SENDER_SALT", "salt")
    s = hc.Settings(send_attempts=1, send_retry_delay_s=0, sender_salt="salt")
    a = _run(mw._ensure_disclosure(SENDER, s))
    b = _run(mw._ensure_disclosure(SENDER, s))
    assert a["disclosure_state"] == "delivered" and b["disclosure_state"] == "already"
    assert sent == [hc.DISCLOSURE_TEXT]
    h = mw._disclosure_health()
    assert h["enabled"] is True and h["participants_told"] == 1 and h["stuck_sending"] == 0


def test_health_reports_the_parsed_flag_and_a_typo_stays_on(monkeypatch):
    mw = _load_mw(monkeypatch)
    monkeypatch.setenv("DISCLOSURE", "ture")
    assert mw._disclosure_health()["enabled"] is True
    monkeypatch.setenv("DISCLOSURE", "off")
    assert mw._disclosure_health()["enabled"] is False


def test_the_review_card_warns_only_when_the_disclosure_did_not_land(monkeypatch):
    mw = _load_mw(monkeypatch)
    assert "DISCLOSURE NOT DELIVERED" in mw._disclosure_banner({"disclosure_state": "failed"})
    assert "DISCLOSURE NOT DELIVERED" in mw._disclosure_banner({"disclosure_state": "unknown"})
    for ok in ("delivered", "pending_receipt", "already", None):
        assert mw._disclosure_banner({"disclosure_state": ok}) == ""
