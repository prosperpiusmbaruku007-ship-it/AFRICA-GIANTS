# -*- coding: utf-8 -*-
"""THE FIRST-CONTACT MESSAGE (founder amendment to the R7 disclosure reading, 2026-11-27).

ONE message for every NEW number, whatever it sends first, replacing the separate disclosure AND the welcome for that number:
  * greeting first -> that message only;   * question first -> that message, then the normal answer flow;   * existing numbers -> unchanged.

Tests both ways. The LIMB table is the point: every limb of the V1 disclosure must still be in the new text, pinned by the new text's own wording, so a later edit cannot drop
a limb silently. The planted test shows the checker reports a limb that is removed."""
import os
import sys
import types

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, _ROOT)
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as core  # noqa: E402
from test_evidence_guard import _load_mw as _load_mw_real, _run, hc, _real_run, _Silent  # noqa: E402
from chike import routing  # noqa: E402
from chike.orchestrator import Orchestrator  # noqa: E402

FOUNDERS_FIRST_CONTACT = "\n".join([
    "Habari, karibu! 👋", "",
    "Mimi ni *Chike*, msaidizi (AI) wa Africa Giants. Ninajibu kwa Kiswahili maswali ya kodi na kanuni za biashara Tanzania.", "",
    "*Ukiwa nami:*",
    "💡 Unajua kiasi halisi cha kulipa: PAYE, NSSF, SDL, VAT",
    "⏰ Unajua tarehe za mwisho, unaepuka faini",
    "📋 Unajua usajili na leseni unazohitaji: TRA, BRELA, NSSF, OSHA", "",
    "*Jaribu kuuliza, kwa mfano:*",
    "• Mshahara wa TZS 800,000, PAYE ni kiasi gani?",
    "• Leseni ya biashara inadumu muda gani?", "",
    "*Kabla hujaanza:*",
    "• Chike yuko katika hatua za mwanzo: majibu mengi husomwa na mtu kabla ya kukufikia, kwa hiyo jibu linaweza kuchukua muda, wakati mwingine saa kadhaa.",
    "• Majibu ni mwongozo, si ushauri rasmi wa kisheria. Kwa maamuzi makubwa, thibitisha na TRA au mamlaka husika.",
    "• Usitume nywila, namba za benki wala taarifa binafsi zisizo za lazima.",
    "• Maswali yako hutusaidia kuiboresha Chike. Kufuta taarifa zako, tuma FUTA.", "",
    "Uliza swali lako 👇"])

# (limb, the phrase in the V1 disclosure, the phrase that carries it in the first-contact message)
LIMBS = [
    ("what Chike is: an assistant for tax and business-law questions", "msaidizi wa maswali ya kodi na sheria za biashara", "msaidizi (AI) wa Africa Giants"),
    ("early-stage / supervised pilot", "jaribio linalosimamiwa", "hatua za mwanzo"),
    ("a person reads most answers", "yanasomwa na mtu", "husomwa na mtu"),
    ("latency is real: sometimes hours", "wakati mwingine saa kadhaa", "wakati mwingine saa kadhaa"),
    ("guidance, not formal legal advice", "si ushauri rasmi wa kisheria", "si ushauri rasmi wa kisheria"),
    ("confirm important answers with TRA or the authority", "thibitisha na TRA au mamlaka husika", "thibitisha na TRA au mamlaka husika"),
    ("no unnecessary personal data", "taarifa binafsi zisizo za lazima", "taarifa binafsi zisizo za lazima"),
    ("no passwords", "nywila", "nywila"),
    ("no bank numbers", "namba za benki", "namba za benki"),
    ("their messages help improve Chike", "kuiboresha Chike", "kuiboresha Chike"),
]
NEW_LIMB = ("how to delete their records", "tuma FUTA")


def missing_limbs(text):
    return [name for name, _v1, new in LIMBS if new not in text] + ([NEW_LIMB[0]] if NEW_LIMB[1] not in text else [])


# ── the text ─────────────────────────────────────────────────────────────────────────────────────────────────
def test_the_first_contact_message_is_the_founders_text_verbatim():
    assert hc.FIRST_CONTACT_TEXT == FOUNDERS_FIRST_CONTACT
    assert hc.DISCLOSURE_TEXT is hc.FIRST_CONTACT_TEXT, "the message every code path sends once IS the first-contact message"


def test_every_limb_of_the_v1_disclosure_is_still_present_by_the_new_texts_own_wording():
    for name, v1_phrase, new_phrase in LIMBS:
        assert v1_phrase in hc.LEGACY_DISCLOSURE_TEXT_V1, f"table error: {v1_phrase!r} is not in the V1 text ({name})"
    assert missing_limbs(hc.FIRST_CONTACT_TEXT) == []


def test_PLANT_removing_any_one_limb_is_reported_by_name():
    for name, _v1, new_phrase in LIMBS:
        broken = hc.FIRST_CONTACT_TEXT.replace(new_phrase, "")
        assert name in missing_limbs(broken), f"the limb check cannot see the loss of: {name}"
    assert "how to delete their records" in missing_limbs(hc.FIRST_CONTACT_TEXT.replace("tuma FUTA", "")), "nor the FUTA instruction"


def test_the_v1_text_is_pinned_as_never_sent_history():
    assert "jaribio linalosimamiwa" in hc.LEGACY_DISCLOSURE_TEXT_V1 and hc.LEGACY_DISCLOSURE_TEXT_V1 != hc.DISCLOSURE_TEXT


def test_swahili_only_no_gn_codes_no_links_and_fits_a_whatsapp_message():
    low = hc.FIRST_CONTACT_TEXT.lower()
    for needle in ("hello", "welcome", "your ", "i am", "beta", "fahamu biashara", "gn 487a", "gn 605a", "http", "wa.me"):
        assert needle not in low, needle
    assert len(hc.FIRST_CONTACT_TEXT) < 4096


def test_it_advertises_only_verified_routes():
    ex = [ln[2:].strip() for ln in hc.FIRST_CONTACT_TEXT.splitlines() if ln.startswith("• ") and ln.endswith("?")]
    assert ex == ["Mshahara wa TZS 800,000, PAYE ni kiasi gani?", "Leseni ya biashara inadumu muda gani?"]
    run = _real_run(Orchestrator(_Silent(), retriever=lambda x: [], ooc_phrases=[], in_scope_phrases=[]))
    assert run(ex[0])["path"] == "engine:paye"
    out = run(ex[1])
    assert out["path"] == "engine:fixed_statement" and "miezi 12" in out["reply"] and "business_licence_validity" in routing.fixed_statement_topics(ex[1])


def test_the_returning_user_welcome_is_unchanged_and_still_exists():
    assert hc.WELCOME.startswith("Habari, karibu! 👋") and "majibu mengi hukaguliwa kwanza" in hc.WELCOME and "FUTA" not in hc.WELCOME


# ── the flows, through the REAL handlers ─────────────────────────────────────────────────────────────────────
NEW = "255700000099@s.whatsapp.net"


@pytest.fixture
def mw(monkeypatch):
    m = _load_mw_real(monkeypatch)
    monkeypatch.delenv("DISCLOSURE", raising=False)                # ON (the default): _load_mw sets it off for its own tests
    m.sent, m.model_calls = [], []

    async def fake_send(to, text):
        m.sent.append(text)
        return True, None
    monkeypatch.setattr(m, "_send_once", fake_send)

    class _Remote:
        @staticmethod
        async def aio(message):
            m.model_calls.append(message)
            return {"reply": "Ndiyo.", "working": "W", "facts": ["F"], "path": "engine:vat_registration"}

    class _Model:
        run = types.SimpleNamespace(remote=_Remote)
    monkeypatch.setattr(m, "ChikeModel", _Model)
    return m


def _greet(m, sender=NEW):
    return _run(m.greet_and_send.get_raw_f()(sender))


def _ask(m, text="Swali", sender=NEW):
    return _run(m.answer_and_send.get_raw_f()(sender, text))


def test_greeting_first_sends_the_first_contact_message_only(mw):
    out = _greet(mw)
    assert mw.sent == [core.FIRST_CONTACT_TEXT], "ONE message: no separate disclosure, no welcome after it"
    assert out["send_ok"] is True and mw.model_calls == [] and len(mw.REVIEW_QUEUE) == 0
    row = [r for r in mw.TRANSCRIPTS.values() if r.get("kind") == "greeting"][0]
    assert row["reply"] == "FIRST_CONTACT" and row["disclosure_state"] == "delivered" and row["reply_chars"] == len(core.FIRST_CONTACT_TEXT)


def test_a_question_first_sends_the_first_contact_message_then_the_normal_flow(mw):
    _ask(mw, "Mshahara wa TZS 800,000, PAYE ni kiasi gani?")
    assert mw.sent[0] == core.FIRST_CONTACT_TEXT, "the message comes BEFORE anything else"
    assert len(mw.model_calls) == 1 and len(mw.REVIEW_QUEUE) == 1, "and the question then goes through the normal flow (model, then held for review)"
    assert core.FIRST_CONTACT_TEXT not in mw.sent[1:], "never twice"
    assert core.WELCOME not in mw.sent, "no separate welcome for a question-first number"


def test_a_second_greeting_from_the_same_number_gets_the_welcome_not_the_message_again(mw):
    _greet(mw)
    mw.sent.clear()
    _greet(mw)
    assert mw.sent == [core.WELCOME], "now an existing number: the returning-user welcome"


def test_a_question_after_a_greeting_does_not_repeat_it(mw):
    _greet(mw)
    mw.sent.clear()
    _ask(mw)
    assert core.FIRST_CONTACT_TEXT not in mw.sent and len(mw.model_calls) == 1


def test_an_existing_number_is_unchanged_greeting_gets_the_welcome(mw):
    key = core.sender_ids(NEW, "salt")[0]
    mw.DISCLOSURES[key] = {"state": "delivered", "ts": "2026-11-10T10:00:00+00:00"}              # told long ago, under the V1 disclosure
    _greet(mw)
    assert mw.sent == [core.WELCOME] and core.FIRST_CONTACT_TEXT not in mw.sent


def test_an_existing_number_asking_a_question_gets_no_first_contact_message(mw):
    mw.DISCLOSURES[core.sender_ids(NEW, "salt")[0]] = {"state": "delivered", "ts": "2026-11-10T10:00:00+00:00"}
    _ask(mw)
    assert core.FIRST_CONTACT_TEXT not in mw.sent and core.DISCLOSURE_TEXT not in mw.sent


def test_the_message_is_sent_once_even_when_two_messages_arrive_together(mw):
    async def both():
        import asyncio
        await asyncio.gather(mw.greet_and_send.get_raw_f()(NEW), mw.answer_and_send.get_raw_f()(NEW, "Swali"))
    _run(both())
    assert mw.sent.count(core.FIRST_CONTACT_TEXT) == 1, "the atomic claim holds: one message, whichever arrives first"


def test_with_the_disclosure_switched_off_a_greeting_gets_the_welcome_as_before(mw, monkeypatch):
    monkeypatch.setenv("DISCLOSURE", "off")
    _greet(mw)
    assert mw.sent == [core.WELCOME]


def test_a_clean_send_failure_falls_back_to_the_welcome_and_the_next_message_retries(mw, monkeypatch):
    state = {"fail": True}
    real = mw._send_once

    async def flaky(to, text):
        if text == core.FIRST_CONTACT_TEXT and state["fail"]:
            return False, "bridge unreachable"
        return await real(to, text)
    monkeypatch.setattr(mw, "_send_once", flaky)
    _greet(mw)
    assert mw.sent == [core.WELCOME], "the participant is not left in silence"
    assert core.sender_ids(NEW, "salt")[0] not in mw.DISCLOSURES, "the claim was released"
    state["fail"] = False
    mw.sent.clear()
    _greet(mw)
    assert mw.sent == [core.FIRST_CONTACT_TEXT], "and the next message is still treated as a first contact"


def test_a_new_number_with_a_question_already_pending_still_gets_the_pending_notice_after_the_message(mw):
    mw.REVIEW_QUEUE["r"] = {"review_id": "r", "status": "pending", "sender": NEW, "sender_hash": core.sender_ids(NEW, "salt")[0], "ts_held": "2026-11-26T10:00:00+00:00"}
    _greet(mw)
    assert mw.sent == [core.FIRST_CONTACT_TEXT, core.PENDING_NOTICE], "the notice carries separate information and is not swallowed"


def test_after_a_deletion_the_next_message_is_a_first_contact_again(mw):
    _greet(mw)
    mw.DISCLOSURES.pop(core.sender_ids(NEW, "salt")[0])                                          # exactly what FUTA does (tests/test_futa.py counts it)
    mw.sent.clear()
    _greet(mw)
    assert mw.sent == [core.FIRST_CONTACT_TEXT]


def test_the_greeting_path_and_the_question_path_never_call_the_model_for_the_message_itself(mw):
    _greet(mw)
    assert mw.model_calls == [], "the first-contact message is a fixed text"
