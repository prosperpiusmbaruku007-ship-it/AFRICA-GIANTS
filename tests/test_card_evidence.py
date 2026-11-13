"""The review card's evidence, the greeting, the pending-question reply and the cohort ceiling (2026-11-12).

FOUND BY READING ONE ANSWER: "Ndiyo, unapaswa kujiandikisha kwa ajili ya VAT." arrived with `engine_working: null`
and `facts: []`, and measurement showed ALL 7 real queue items had the same: the reviewer had never been shown the
evidence the review design rests on. `ChikeModel.run` returned only {'reply': ...}. These tests pin the whole chain.
"""
import ast
import asyncio
import importlib.util
import os
import sys
import types

import pytest

from chike import answer_trace
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location("hc_card", os.path.join(_ROOT, "chike-whatsapp", "handler_core.py"))
hc = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(hc)


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


class _Says(ModelBackend):
    def generate(self, prompt, params=None):
        return "Ndiyo, hiyo ni sahihi."


def _engine_reply(q):
    return Orchestrator(_Silent(), retriever=lambda x: [], ooc_phrases=[], in_scope_phrases=[]).answer(q)


# ── the trace: which SOURCE answered, the working, the facts ───────────────────────────────────
def test_an_engine_answer_reports_the_engine_and_its_working():
    t = answer_trace.trace(_engine_reply("Nina wafanyakazi 12, mishahara yote kwa mwezi ni milioni 6. SDL nitalipa kiasi gani?"))
    assert t["path"] == "engine:sdl" and t["working"] and "210,000" in t["working"] and t["facts"] == []


def test_the_vat_engine_answer_is_labelled_as_the_engine():
    t = answer_trace.trace(_engine_reply("Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima kujisajili VAT?"))
    assert t["path"] == "engine:vat_registration"


def test_a_clarification_from_an_engine_is_labelled_ask():
    t = answer_trace.trace(_engine_reply("Mauzo yangu ya mwaka yamezidi TZS 100 milioni, je ni lazima kusajili VAT?"))
    assert t["path"] == "engine:vat_registration:ask"


def test_a_model_answer_reports_the_FACTS_it_was_given_and_no_engine():
    facts = ["Fact A: NSSF ni 20%.", "Fact B: SDL ni 3.5%."]
    orch = Orchestrator(_Says(), retriever=lambda q: facts, ooc_phrases=[], in_scope_phrases=[])
    t = answer_trace.trace(orch.answer("Faini ya kuchelewa kulipa NSSF ni kiasi gani?"))
    assert t["path"] == "fact" and t["working"] is None
    assert set(t["facts"]) == set(facts), t


def test_an_empty_reply_traces_without_raising():
    class R:
        sub_answers, refused = (), True
    assert answer_trace.trace(R()) == {"working": None, "facts": [], "path": "refusal", "model_calls": None, "guards": []}


# ── the wiring, on the deployed files' structure ──────────────────────────────────────────────
def test_run_returns_the_trace_not_just_the_reply():
    src = open(os.path.join(_ROOT, "chike-inference", "modal_app.py"), encoding="utf-8").read()
    seg = src[src.index("if PIPELINE == 'v16':"):src.index("from chike import pipeline_v15")]
    assert "trace(reply)" in seg and "out.update(trace(reply))" in seg and "return out" in seg
    assert "return {'reply': reply.text}" not in seg, "the bare-reply return is the defect"


def _mw_src():
    return open(os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"), encoding="utf-8").read()


def test_the_handler_captures_path_working_and_facts_and_puts_them_on_the_item_and_row():
    src = _mw_src()
    assert 'captured["path"] = result.get("path")' in src
    assert 'item["answer_path"] = captured.get("path")' in src
    assert 'row["answer_path"] = captured.get("path")' in src
    assert src.count("_path_html(it)") >= 3          # defined once, shown on BOTH cards


# ── the plainest phrasing of the question: WAS a known routing gap, now closed ───────────────────
# This was a strict-xfail until the VAT cue list learned the first-person subjunctive (2026-11-12). It is an
# ordinary passing test now -- and strict=True is why it could not be forgotten: the day the cues were fixed it
# would have failed as an XPASS until the marker was removed. The probes and sweep live in tests/test_vat_phrasing.py.
def test_first_person_vat_registration_reaches_the_engine():
    t = answer_trace.trace(_engine_reply("Mauzo yangu ni milioni 250 kwa mwaka. Je, ni lazima nijisajili VAT"))
    assert t["path"].startswith("engine:vat_registration")
    assert t["working"] is None or "250,000,000" in t["working"] or t["path"] == "engine:vat_registration"


# ── the greeting ─────────────────────────────────────────────────────────────────────────────────
def test_the_welcome_no_longer_calls_chike_an_adviser():
    """The disclosure says answers are 'si ushauri rasmi'; a welcome calling Chike 'mshauri wako' contradicts it."""
    assert "mshauri" not in hc.WELCOME.lower() and "adviser" not in hc.WELCOME.lower()
    assert "msaidizi wako wa maswali ya biashara" in hc.WELCOME
    assert "assistant for business questions" in hc.WELCOME
    assert "msaidizi" in hc.DISCLOSURE_TEXT          # the two now describe Chike the same way


def test_the_pending_notice_is_brief_and_says_the_answer_is_coming():
    assert len(hc.PENDING_NOTICE) < 220 and "bado linaandaliwa" in hc.PENDING_NOTICE
    assert "Karibu" not in hc.PENDING_NOTICE and "Kodi —" not in hc.PENDING_NOTICE, "no menu"


# ── a pending question, against the real wiring with the Modal Dicts stubbed ──────────────────────
def _load_mw(monkeypatch):
    from conftest import isolate_modal_stores
    pkg = types.ModuleType("chike_whatsapp")
    pkg.handler_core = hc
    monkeypatch.setitem(sys.modules, "chike_whatsapp", pkg)
    monkeypatch.setitem(sys.modules, "chike_whatsapp.handler_core", hc)
    spec = importlib.util.spec_from_file_location("chike_mw_card", os.path.join(_ROOT, "chike-whatsapp", "modal_whatsapp.py"))
    mw = importlib.util.module_from_spec(spec)
    spec.loader.exec_module(mw)
    names = isolate_modal_stores(mw, monkeypatch)
    assert "INFLIGHT" in names
    monkeypatch.setenv("SENDER_SALT", "salt")
    return mw


def _run(coro):
    loop = asyncio.new_event_loop()
    try:
        return loop.run_until_complete(coro)
    finally:
        loop.close()


SENDER = "255700000011@s.whatsapp.net"
OTHER = "255700000022@s.whatsapp.net"


def _settings():
    return hc.Settings(send_attempts=1, send_retry_delay_s=0, sender_salt="salt")


def test_no_question_pending_means_the_ordinary_welcome(monkeypatch):
    mw = _load_mw(monkeypatch)
    assert mw._has_pending_question(SENDER, _settings()) is False


def test_a_question_in_flight_is_pending_until_it_goes_stale(monkeypatch):
    import time
    mw = _load_mw(monkeypatch)
    s = _settings()
    mw._mark_inflight(SENDER, s)
    assert mw._has_pending_question(SENDER, s) is True
    assert mw._has_pending_question(OTHER, s) is False, "another participant's question is not mine"
    mw.INFLIGHT[mw._sender_key(SENDER, s)] = {"ts": time.time() - 3 * 3600}
    assert mw._has_pending_question(SENDER, s) is False, "a stale marker (a crash) must not pin the notice for ever"
    mw._mark_inflight(SENDER, s)
    mw._clear_inflight(SENDER, s)
    assert mw._has_pending_question(SENDER, s) is False


def test_a_draft_waiting_in_review_is_pending_and_a_decided_one_is_not(monkeypatch):
    mw = _load_mw(monkeypatch)
    s = _settings()
    key = mw._sender_key(SENDER, s)
    mw.REVIEW_QUEUE["r1"] = {"review_id": "r1", "sender_hash": key, "status": "pending"}
    assert mw._has_pending_question(SENDER, s) is True
    mw.REVIEW_QUEUE["r1"] = {"review_id": "r1", "sender_hash": key, "status": "sent"}
    assert mw._has_pending_question(SENDER, s) is False
    mw.REVIEW_QUEUE["r2"] = {"review_id": "r2", "sender_hash": mw._sender_key(OTHER, s), "status": "pending"}
    assert mw._has_pending_question(SENDER, s) is False


def _greet(mw, monkeypatch, sender=SENDER):
    sent = []

    async def fake_send(to, text):
        sent.append(text)
        return True, None
    monkeypatch.setattr(mw, "_send_once", fake_send)
    row = _run(mw.greet_and_send.get_raw_f()(sender))
    return sent, row


def test_a_greeting_while_a_question_is_pending_gets_the_brief_notice_not_the_menu(monkeypatch):
    mw = _load_mw(monkeypatch)
    monkeypatch.setenv("DISCLOSURE", "off")                    # isolate this behaviour from the disclosure
    mw._mark_inflight(SENDER, mw._settings())
    sent, _ = _greet(mw, monkeypatch)
    assert sent == [hc.PENDING_NOTICE], sent
    kinds = [r.get("kind") for r in mw.TRANSCRIPTS.values()]
    assert "greeting_pending" in kinds and "greeting" not in kinds


def test_a_greeting_with_nothing_pending_still_gets_the_welcome(monkeypatch):
    mw = _load_mw(monkeypatch)
    monkeypatch.setenv("DISCLOSURE", "off")
    sent, _ = _greet(mw, monkeypatch)
    assert sent == [hc.WELCOME]


def test_the_disclosure_still_comes_first_even_when_the_greeting_is_the_pending_notice(monkeypatch):
    mw = _load_mw(monkeypatch)
    mw._mark_inflight(SENDER, mw._settings())
    sent, _ = _greet(mw, monkeypatch)
    assert sent == [hc.DISCLOSURE_TEXT, hc.PENDING_NOTICE], [s[:30] for s in sent]


# ── the cohort ceiling: 15 declared, one reviewer, and /health says so honestly ─────────────────
def test_a_ceiling_of_15_with_one_reviewer_reports_false_and_the_real_capacity():
    c = hc.cohort_capacity(15, 1)
    assert c["within_review_capacity"] is False
    assert c["sized_for_reviewers"] == 5 and c["review_capacity_participants"] == 3
    assert "CEILING of 15" in c["capacity_note"] and "OVER" in c["capacity_note"]
    assert "3 participants" in c["capacity_note"] and "add reviewers before growing" in c["capacity_note"]


def test_the_health_cohort_keeps_the_gap_between_the_cap_and_the_capacity_visible(monkeypatch):
    mw = _load_mw(monkeypatch)
    monkeypatch.setenv("COHORT_SIZE", "15")
    monkeypatch.setenv("REVIEWER_ROSTER", "+255700000011:Prosper")
    monkeypatch.setenv("REVIEW_SIGNING_KEY", "k")
    monkeypatch.setattr(mw, "_participants_split", lambda: (2, 0))
    c = mw._cohort_health()
    assert c["declared_size"] == 15 and c["within_review_capacity"] is False
    assert c["review_capacity_participants"] == 3 and c["seen_exceeds_review_capacity"] is False
    monkeypatch.setattr(mw, "_participants_split", lambda: (4, 0))
    assert mw._cohort_health()["seen_exceeds_review_capacity"] is True, "serving more people than one reviewer can review"
