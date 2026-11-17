# -*- coding: utf-8 -*-
"""R17 regression file for the founder's 2026-11-17 decision 1: the VAT engine reads an ANNUAL and a SIX-MONTH turnover figure given TOGETHER (no bound) and tests each against its OWN limb (eval_333 / eval_353 regressed
at 8ff677a and are the founding specimens, read from the committed gold files, not retyped). The clean half is every neighbour the reader must NOT touch: same period twice, three figures, a monthly figure, one figure, the two
statutory thresholds themselves, a bound plus one figure (the earlier path), figures with no period cue."""
import io
import json
from decimal import Decimal

import pytest

from chike import routing
from chike import rules_engine as re_
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator


def _gold(i):
    for f in ("eval_questions_001", "eval_questions_002_additions", "eval_questions_003"):
        for l in io.open(f"eval/accuracy_gate/{f}.jsonl", encoding="utf-8"):
            if l.strip():
                r = json.loads(l)
                if r["id"] == i:
                    return r
    raise KeyError(i)


Q333, Q353 = _gold("eval_333")["question_sw"], _gold("eval_353")["question_sw"]

# (question, expected (annual, six_month) or None)
PAIR = [
    (Q333, (190_000_000, 120_000_000)),
    (Q353, (199_000_000, 99_000_000)),
    ("Mauzo yangu ni TZS 250,000,000 kwa mwaka na TZS 150,000,000 kwa miezi 6. Nijisajili VAT?", (250_000_000, 150_000_000)),
    ("Nimeuza TZS 90,000,000 katika miezi 6 na TZS 200,000,000 kwa mwaka. Je VAT ni lazima?", (200_000_000, 90_000_000)),            # exactly at the annual threshold (inclusive) with the six-month under
    ("Mauzo ya miezi 6 ni milioni 100, na kwa mwaka milioni 150. Je VAT?", (150_000_000, 100_000_000)),                              # exactly at the six-month threshold, scale-first notation, order reversed
    ("Mauzo yangu kwa mwaka ni TZS 120,000,000 na kwa miezi 6 TZS 60,000,000, je nahitaji kusajili VAT?", (120_000_000, 60_000_000)),
]
NONE = [
    ("Mauzo yangu ni milioni 150 kwa mwaka na milioni 80 kwa mwaka. Je VAT?", "the same period twice"),
    ("Mauzo ni milioni 60 kwa miezi 6, milioni 150 kwa mwaka, na milioni 30 kwa miezi 6. Je VAT?", "three figures"),
    ("Mauzo ni milioni 20 kwa mwezi na milioni 150 kwa mwaka. Je VAT?", "a MONTHLY figure is a rate"),
    ("Mauzo yangu ni milioni 150 kwa mwaka. Je VAT?", "one figure"),
    ("Kizingiti cha VAT ni TZS 200,000,000 kwa mwaka au TZS 100,000,000 kwa miezi 6, sivyo? Je VAT?", "the pair IS the two statutory thresholds"),
    ("Mauzo yangu hayajafika milioni 200 lakini ndani ya miezi 6 nimeuza milioni 110. Je VAT?", "a bound plus one figure: the earlier path"),
    ("Mauzo yangu ni TZS 150,000,000 na TZS 90,000,000. Je VAT?", "no period cue on either figure"),
    ("Mauzo yangu ni TZS 150,000,000 kwa mwaka na TZS 90,000,000. Je VAT?", "only one figure has a period"),
    ("Mauzo ya miezi 6 ni milioni 100 na ya mwaka ni milioni 150. Je VAT?", "TIE: the genitive cue is equidistant from both figures, the safe outcome is to ask"),
]


@pytest.mark.parametrize("q,expect", PAIR)
def test_pair_is_read(q, expect):
    got = routing.turnover_pair_with_periods(q)
    assert got == (Decimal(expect[0]), Decimal(expect[1])), got


@pytest.mark.parametrize("q,why", NONE)
def test_everything_else_is_left_alone(q, why):
    assert routing.turnover_pair_with_periods(q) is None, why


class _S(ModelBackend):
    def __init__(self):
        self.calls = 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return "JIBU LA MODELI"


def _ans(q):
    b = _S()
    return Orchestrator(backend=b, retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q), b


def test_wired_eval_333_registers_and_names_the_six_month_limb_with_no_model_call():
    r, b = _ans(Q333)
    assert b.calls == 0 and r.sub_answers[0].needs_clarification is False
    assert r.text.startswith("Ndiyo, unatakiwa kujisajili VAT") and "TZS 120,000,000" in r.text and "miezi 6" in r.text and "Kigezo kimoja tu kinatosha" in r.text, r.text


def test_wired_eval_353_says_no_on_BOTH_limbs_conditionally_and_asks_nothing():
    r, b = _ans(Q353)
    assert b.calls == 0 and r.sub_answers[0].needs_clarification is False
    assert r.text.startswith("Hapana") and "vigezo vyote viwili" in r.text and "Ukivuka kimojawapo" in r.text and "niambie" not in r.text.lower(), r.text
    assert re_.vat_registration_both_limbs(199_000_000, 99_000_000).applicable is False


@pytest.mark.parametrize("a,s", [(0, 0), (199_999_999, 99_999_999), (200_000_000, 0), (0, 100_000_000), (200_000_000, 100_000_000), (1_000_000_000, 1)])
def test_either_limb_crossing_registers_and_it_is_inclusive(a, s):
    r = re_.vat_registration_both_limbs(a, s)
    assert r.applicable == (a >= 200_000_000 or s >= 100_000_000)


def test_the_negatives_that_reach_the_engine_still_ASK_with_no_model_call():
    # (the monthly + annual wording does not route to the engine at all: it stays on the model path, untouched by this change)
    for q in ("Mauzo yangu ni milioni 150 kwa mwaka na milioni 80 kwa mwaka. Je nijisajili VAT?",):
        assert routing.detect_intent(q) == "vat_registration", q
        r, b = _ans(q)
        assert b.calls == 0 and r.sub_answers[0].needs_clarification is True, q


def test_PLANTED_with_the_pair_reader_disabled_the_engine_asks_again(monkeypatch):
    monkeypatch.setattr(routing, "turnover_pair_with_periods", lambda t: None)
    r, _ = _ans(Q353)
    assert r.sub_answers[0].needs_clarification is True and "Ili nikwambie" in r.text


def test_the_earlier_paths_are_untouched():
    np22 = "Mimi nina biashara ya kuuza vifaa, mauzo yangu ya mwaka bado hayajafika milioni 200 lakini ndani ya miezi 6 nimeuza milioni 110. Sihitaji kujisajili VAT kwa sababu mwaka bado haujaisha, siyo?"
    r, b = _ans(np22)
    assert b.calls == 0 and "TZS 110,000,000 kwa miezi 6" in r.text
    r, b = _ans("Biashara yangu inauza kwa wastani wa milioni 18 kila mwezi. Je nijisajili VAT?")
    assert b.calls == 0 and "216,000,000" in r.text
