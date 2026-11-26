# -*- coding: utf-8 -*-
"""RENT FIX (founder, 2026-11-26): R44 strip + the conditional line "Ikiwa wewe ni wakala wa kuzuia: 10% × X = Y" + the amount-bearing variant is EXCLUDED from auto-send.
Every limb has a positive control; the exclusion is shown to be the ONLY thing holding the draft by removing it (plant)."""
import os
import sys

import pytest

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(_ROOT, "chike-whatsapp"))
import handler_core as hc  # noqa: E402

from chike.model_abstraction import FakeBackend
from chike.orchestrator import Orchestrator
from chike.rules_engine import rent_wht_statement
from chike.rules_engine import rent_wht as rw


def _line(q):
    return rent_wht_statement(rent_amount=rw.rent_amount(q)).working


@pytest.mark.parametrize("q,expect", [
    ("Nalipa kodi ya pango TZS 800,000 kwa mwezi, nikate withholding kiasi gani?", "10% × TZS 800,000 = TZS 80,000."),
    ("Pango la ofisi ni TZS 8,000,000, nikate kiasi gani?", "10% × TZS 8,000,000 = TZS 800,000."),       # a hard-coded sum fails one of these two
    ("Kodi ya pango ni milioni 3 kwa mwezi, nimkate mwenye nyumba kiasi gani?", "10% × TZS 3,000,000 = TZS 300,000."),
    ("Pango la TZS 850,001 nikate kiasi gani", "10% × TZS 850,001 = TZS 85,000.10."),
])
def test_one_rent_figure_gets_the_conditional_line_under_an_if(q, expect):
    w = _line(q)
    assert "Ikiwa wewe ni wakala wa kuzuia: " + expect in w
    assert w.index("Ikiwa wewe ni wakala wa kuzuia") > w.index("LAKINI kukata kodi hii ni WAJIBU WA WAKALA"), "the precondition is stated BEFORE the sum"


@pytest.mark.parametrize("q", [
    "Nikate kiasi gani kwenye pango?",                                            # no figure
    "Pango ni TZS 800,000 na TZS 500,000, nikate kiasi gani?",                    # two figures
    "Mauzo yangu ni TZS 50,000,000, nikate WHT ya pango?",                        # a lone figure that is NOT the rent (Guard B)
    "Mapato ya TZS 3,000,000 kwa mwezi, nalipa pango, nikate kiasi gani?",        # income figure
    "Nina deni TZS 4,000,000, nalipa pango, nikate kiasi gani?",
])
def test_no_line_without_exactly_one_RENT_figure(q):
    assert "×" not in _line(q) and rw.AMOUNT_BEARING_MARKER not in _line(q)


def test_the_unconditional_amount_field_stays_None_R19():
    assert rent_wht_statement(rent_amount=800000).amount is None


def test_R44_no_chapter_or_paragraph_number_in_the_served_text():
    for w in (_line("Pango TZS 800,000 nikate kiasi gani?"), rent_wht_statement().working):
        assert "4(b)(ii)" not in w and "Cap." not in w and "aya " not in w and "Sheria ya Kodi ya Mapato" in w
    assert "4(b)(ii)" in rent_wht_statement().note, "the paragraph survives in METADATA (R44 rule 3)"


def test_end_to_end_orchestrator_is_model_free_and_carries_the_line():
    fake = FakeBackend(scripted_reply="SHOULD NOT BE CALLED")
    r = Orchestrator(backend=fake, retriever=lambda q: []).answer("Nalipa kodi ya pango TZS 2,000,000 kwa mwezi, nikate withholding kiasi gani?")
    assert fake.call_count == 0 and "Ikiwa wewe ni wakala wa kuzuia: 10% × TZS 2,000,000 = TZS 200,000." in r.text


# ── auto-send exclusion ──────────────────────────────────────────────────────────────────────────
def _item(working, **kw):
    it = {"status": "pending", "answer_path": "engine:rent_wht", "model_calls": 0, "guards": [], "fallback": False, "engine_working": working,
          "draft": working, "facts": [], "question": "q"}
    it.update(kw)
    return it


def test_marker_is_identical_in_both_packages():
    assert hc.AMOUNT_BEARING_RENT_MARKERS[0] == rw.AMOUNT_BEARING_MARKER


def test_amount_bearing_rent_is_NOT_autosend_eligible_but_the_plain_statement_still_is():
    plain = rent_wht_statement().working
    bearing = _line("Nalipa kodi ya pango TZS 800,000 kwa mwezi, nikate kiasi gani?")
    ok_plain, _ = hc.engine_only_verdict(_item(plain))
    ok_bear, why = hc.engine_only_verdict(_item(bearing))
    assert ok_plain is True, "positive control: the no-amount rent statement still auto-sends"
    assert ok_bear is False and "amount-bearing rent" in why


def test_a_reworded_line_with_a_multiplication_sign_still_fails_closed():
    assert hc.engine_only_verdict(_item(rent_wht_statement().working + " Kiasi: 10% × 800,000."))[0] is False


def test_PLANT_without_the_exclusion_the_amount_bearing_reply_WOULD_auto_send(monkeypatch):
    monkeypatch.setattr(hc, "AMOUNT_BEARING_RENT_MARKERS", ())
    assert hc.engine_only_verdict(_item(_line("Pango TZS 800,000 nikate kiasi gani?")))[0] is True


def test_real_15_minute_sweep_holds_the_amount_bearing_draft_and_auto_sends_the_plain_one(monkeypatch):
    from test_review_timeout import _load_mw, _aged, _sweep, _is_holding
    mw, sent = _load_mw(monkeypatch)
    plain = rent_wht_statement().working
    bearing = _line("Nalipa kodi ya pango TZS 800,000 kwa mwezi, nikate kiasi gani?")
    a = _aged(mw, 16, review_id="2026-11-26T08:00:00+00:00-aaaaaaaa", sender="255700000011@s.whatsapp.net", sender_hash="a" * 12,
              answer_path="engine:rent_wht", engine_working=plain, draft=plain, model_calls=0)
    b = _aged(mw, 16, review_id="2026-11-26T08:00:00+00:00-bbbbbbbb", sender="255700000022@s.whatsapp.net", sender_hash="b" * 12,
              answer_path="engine:rent_wht", engine_working=bearing, draft=bearing, model_calls=0)
    _sweep(mw)
    assert mw.REVIEW_QUEUE[a["review_id"]]["status"] == "auto_sent", "positive control"
    assert mw.REVIEW_QUEUE[b["review_id"]]["status"] == "pending", "the amount-bearing draft stays in review"
    to_b = [t for to, t in sent if "255700000022" in str(to)]
    assert len(to_b) == 1 and _is_holding(to_b[0]), "participant b gets exactly ONE message and it is the holding message"
    assert not any(rw.AMOUNT_BEARING_MARKER in t for _, t in sent), "the amount-bearing line is never sent unreviewed (the marker is unique to it; the rate sentence is shared with the plain draft)"
    assert any("255700000011" in str(to) and not _is_holding(t) for to, t in sent), "positive control: participant a received the plain statement"
