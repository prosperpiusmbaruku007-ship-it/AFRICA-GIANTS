# -*- coding: utf-8 -*-
"""R17/R19/R26 regression file for the founder's 2026-11-17 decision 4 (PROGRESS 4at):

  (a) the VAT engine ANNUALISES a STATED AVERAGE monthly figure ("kwa wastani wa X kila mwezi" -> X x 12, working shown, compared with the 12-month threshold), asking only when the period is genuinely ambiguous; a BARE
      monthly figure and competing monthly/annual cues keep the earlier never-guess block;
  (b) D-FIDELITY-19, comparison fidelity: "A ni chini ya B" when A > B (and "zaidi ya" when A < B), flipped so the sentence is true of its own figures. The founding specimen is the LIVE reply of build d644c71, read from the
      committed artifact, not retyped.
"""
import json
import re
from decimal import Decimal

import pytest

from chike import fidelity, routing
from chike import rules_engine as re_
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

LIVE = json.load(open("eval/results/batch3_deploy_live_2026_11_17.json", encoding="utf-8"))
SPECIMEN_Q = "Kama biashara yangu inauza kwa wastani wa milioni 18 kila mwezi, hiyo hela ipo chini ya milioni 200 kwa mwaka?"
SPECIMEN = next(r["reply"] for r in LIVE["rows"] if r["q"] == SPECIMEN_Q)


class _S(ModelBackend):
    def __init__(self, t):
        self.t, self.calls = t, 0

    def generate(self, prompt, params=None):
        self.calls += 1
        return self.t


def _ans(q, body="JIBU LA MODELI"):
    b = _S(body)
    return Orchestrator(backend=b, retriever=lambda *a, **k: ["x"], system_prompt="x").answer(q), b


# ---- (b) D-FIDELITY-19 --------------------------------------------------------------------------------------------------------------------------------------------------------
def test_the_founding_specimen_is_the_live_reply_and_it_is_backwards():
    assert "216,000,000" in SPECIMEN and "chini ya kiwango cha milioni 200" in SPECIMEN
    v = fidelity.comparison_violations(SPECIMEN)
    assert v == [(Decimal(216_000_000), Decimal(200_000_000), "chini ya")], v


def test_the_repair_makes_the_specimen_true_of_its_own_figures_and_is_idempotent():
    out = fidelity.repair_comparisons(SPECIMEN)
    assert "Hii ni zaidi ya kiwango cha milioni 200" in out and "chini ya kiwango cha milioni 200" not in out
    assert fidelity.comparison_violations(out) == [] and fidelity.repair_comparisons(out) == out


MUST_PASS = [
    "Mauzo yako ya TZS 150,000,000 ni chini ya kizingiti cha TZS 200,000,000.",
    "TZS 250,000,000 kwa mwaka. Hii ni zaidi ya kiwango cha milioni 200.",
    "TZS 270,001 hadi 520,000: 8%. Zaidi ya TZS 270,000 lakini chini ya TZS 520,000.",
    "Mshahara chini ya TZS 270,000 ni 0%.",
    "TZS 400,000 ni zaidi ya 270,000 lakini chini ya 520,000.",
    "Mauzo ya TZS 200,000,000 ni zaidi ya TZS 200,000,000.",                                   # equal figures are never flagged (the boundary is the statute's)
    "Mauzo yako ni TZS 250,000,000. Ukiwa chini ya TZS 200,000,000 hauhitaji kusajili.",       # a sentence break with no demonstrative bridge: the comparator is NOT about the earlier figure
    "Asilimia 30 ni chini ya 20.",                                                              # a percentage is not money
    "Kwa mwaka mmoja (TZS 216,000,000), zaidi ya TZS 200,000,000 -- lazima usajili.",           # no predicate between A and the comparator
    "Kiwango cha PAYE: TZS 520,001 hadi 760,000 ni 20%, na zaidi ya TZS 1,000,000 ni 30%.",
]


@pytest.mark.parametrize("t", MUST_PASS)
def test_correct_comparisons_ranges_and_bands_are_untouched(t):
    assert fidelity.comparison_violations(t) == [] and fidelity.repair_comparisons(t) == t


MUST_FLAG = [
    ("TZS 216,000,000 ni chini ya TZS 200,000,000.", "zaidi ya"),
    ("Mauzo yako ya TZS 150,000,000 ni zaidi ya kizingiti cha TZS 200,000,000.", "chini ya"),
    ("Mauzo ni TZS 600,000,000. Hii ni chini ya kiwango cha milioni 200.", "zaidi ya"),
    ("Mauzo yako ni 250 milioni, hiyo ipo chini ya TZS milioni 200 kinachohitajika.", "zaidi ya"),
    ("Mauzo ni TZS 600,000 ni chini ya 520,000.", "zaidi ya"),
    ("Your sales of TZS 216,000,000 are below TZS 200,000,000.", "above"),
]


@pytest.mark.parametrize("t,expect", MUST_FLAG)
def test_a_backwards_comparison_is_flagged_and_flipped(t, expect):
    assert fidelity.comparison_violations(t), t
    out = fidelity.repair_comparisons(t)
    assert expect in out and fidelity.comparison_violations(out) == [], out


def test_wired_the_specimen_reply_is_repaired_through_the_real_orchestrator():
    r, b = _ans(SPECIMEN_Q, SPECIMEN)
    assert b.calls == 1 and "Hii ni zaidi ya kiwango cha milioni 200" in r.text and "chini ya kiwango cha milioni 200" not in r.text, r.text
    assert "repaired" in [getattr(s, "guard", "") for s in r.sub_answers]


def test_PLANTED_the_comparison_guard_disabled_lets_the_backwards_sentence_through(monkeypatch):
    monkeypatch.setattr(fidelity, "repair_comparisons", lambda b: b)
    r, _ = _ans(SPECIMEN_Q, SPECIMEN)
    assert "chini ya kiwango cha milioni 200" in r.text


# ---- (a) the VAT engine annualises a STATED AVERAGE -------------------------------------------------------------------------------------------------------------------------
@pytest.mark.parametrize("monthly", [1, 5_000_000, 10_000_000, 16_666_666, 16_666_667, 18_000_000, 40_000_000])
def test_the_two_limbs_agree_for_a_uniform_monthly_rate(monthly):
    r = re_.vat_registration_monthly_average(monthly)
    assert r.applicable == (monthly * 12 >= 200_000_000) == (monthly * 6 >= 100_000_000)
    assert r.inputs["annualised"] is True and f"× 12 = " in r.working


def test_a_stated_average_is_answered_by_the_engine_with_the_working_and_no_model_call():
    for q, expect in (("Biashara yangu inauza kwa wastani wa milioni 18 kila mwezi. Je nijisajili VAT?", "TZS 216,000,000"),
                      ("Nauza kwa wastani wa milioni 18 kila mwezi, mauzo yangu ya mwaka bado hayajafika milioni 200. Je nijisajili VAT?", "TZS 216,000,000")):
        r, b = _ans(q)
        assert b.calls == 0 and r.text.startswith("Ndiyo, unatakiwa kujisajili VAT") and expect in r.text and "× 12" in r.text, r.text
        assert "inadhani wastani huo unadumu miezi 12" in r.text, "the assumption must be stated"


def test_a_stated_average_below_the_threshold_says_it_is_an_estimate_and_asks_for_the_actual_total():
    r, b = _ans("Biashara yangu inauza kwa wastani wa milioni 10 kwa mwezi. Je nahitaji kusajili VAT?")
    assert b.calls == 0 and "makadirio ya wastani" in r.text and "Niambie jumla halisi" in r.text and "LAZIMA" not in r.text.split("LAKINI")[0], r.text


def test_a_BARE_monthly_figure_still_gets_the_never_guess_exit():
    r, b = _ans("Nauza milioni 25 kila mwezi. Je nijisajili VAT?")
    assert b.calls == 0 and "Sitakisii mauzo ya mwaka" in r.text and r.sub_answers[0].needs_clarification is True


def test_competing_monthly_and_annual_cues_keep_the_earlier_block():
    # the average cue is present but a DIFFERENT period's cue is a near-tie with the monthly one (within 15 characters): ambiguous, the resolver returns None
    q = "Mauzo yangu hayajafika milioni 200, lakini kwa wastani wa milioni 18 kwa mwezi kwa mwaka."
    assert routing.turnover_with_local_period(q) is None, routing.turnover_with_local_period(q)
    # a single-amount text that also names a six-month / annual period anywhere is not a clean average
    assert routing.monthly_average_stated("Nauza kwa wastani wa milioni 18 kila mwezi, ndani ya mwaka mmoja. Je VAT?") is False
    assert routing.monthly_average_stated("Nauza milioni 18 kila mwezi. Je VAT?") is False             # no average cue at all
    assert routing.monthly_average_stated("Nauza kwa wastani wa milioni 18 kila mwezi. Je VAT?") is True


def test_the_resolver_returns_monthly_average_for_the_priced_specimen_and_np22_is_unchanged():
    assert routing.turnover_with_local_period(SPECIMEN_Q) == (Decimal(18_000_000), "monthly_average")
    np22 = "Mimi nina biashara ya kuuza vifaa, mauzo yangu ya mwaka bado hayajafika milioni 200 lakini ndani ya miezi 6 nimeuza milioni 110. Sihitaji kujisajili VAT kwa sababu mwaka bado haujaisha, siyo?"
    assert routing.turnover_with_local_period(np22) == (Decimal(110_000_000), "six_month")


def test_PLANTED_without_the_average_cue_a_monthly_amount_is_not_annualised(monkeypatch):
    monkeypatch.setattr(routing, "_AVERAGE_CUE", re.compile(r"(?!x)x"))
    assert routing.turnover_with_local_period(SPECIMEN_Q) is None
    r, _ = _ans("Biashara yangu inauza kwa wastani wa milioni 18 kila mwezi. Je nijisajili VAT?")
    assert "Sitakisii mauzo ya mwaka" in r.text


def test_no_control_characters_in_the_new_patterns_R39():
    for pat in (routing._AVERAGE_CUE.pattern, fidelity._D19_CMP.pattern, fidelity._D19_PREDICATE.pattern, fidelity._D19_BRIDGE.pattern, fidelity._D19_LEAD_TOKEN.pattern):
        assert not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", pat), repr(pat)
    for _, pat in routing._LOCAL_PERIOD_CUES:
        assert not re.search(r"[\x00-\x08\x0b\x0c\x0e-\x1f]", pat), repr(pat)
