# -*- coding: utf-8 -*-
"""VAT registration / EFD threshold route — engine, routing, copy polarity.

The defect this route exists to remove is SAFETY-3's: the threshold recited correctly in the
sentence where it was misapplied. So the tests that matter are not "does it know 200,000,000"
(it is a constant) but: does the right LIMB get tested, does the untested limb come back as an
open condition, and does that condition read as a condition rather than as a verdict.
"""
import json

import pytest

from chike import clarification, routing
from chike import rules_engine
from chike.rules_engine import registration_thresholds as rt
from chike.model_abstraction import FakeBackend
from chike.orchestrator import Orchestrator

PROBES = "eval/accuracy_gate/vat_efd_probes_019.jsonl"


def _probes():
    rows = [json.loads(line) for line in open(PROBES, encoding="utf-8") if line.strip()]
    # NON-EMPTY ASSERTION (2026-08-22, dead-anchor census) — see test_minimum_wage._probes.
    assert rows, f"{PROBES} is empty — the tests looping over it would pass vacuously"
    return rows


# --- the limbs ---------------------------------------------------------------

def test_annual_limb_over_is_unconditional():
    r = rules_engine.vat_registration(250_000_000, rt.ANNUAL)
    assert r.applicable is True
    assert r.inputs["limb_untested"] is None, "a crossed limb settles it; no condition remains"
    assert "miezi 6" not in r.working


def test_annual_limb_under_carries_the_six_month_limb_as_an_open_condition():
    """The whole argument for Option 1. 150M/year is below limb A and says NOTHING about
    limb B — 120M in one half-year is registrable — so a flat 'hapana' would be wrong."""
    r = rules_engine.vat_registration(150_000_000, rt.ANNUAL)
    assert r.applicable is False
    assert r.inputs["limb_untested"] == rt.SIX_MONTH
    assert "miezi 6 mfululizo" in r.working
    assert "100,000,000" in r.working


def test_six_month_limb_under_carries_the_annual_limb():
    """The conditional must name the limb that was NOT tested — the direction flips here.
    A hand-authored clause would drift; this one is derived from `limb_tested`."""
    r = rules_engine.vat_registration(95_000_000, rt.SIX_MONTH)
    assert r.applicable is False
    assert r.inputs["limb_untested"] == rt.ANNUAL
    assert "miezi 12" in r.working and "200,000,000" in r.working


def test_six_month_limb_can_trigger_on_its_own():
    """120M in six months is registrable although it is far below the 200M annual figure.
    An implementation that tests only the annual limb answers 'no' to a trader who must
    register."""
    assert rules_engine.vat_registration(120_000_000, rt.SIX_MONTH).applicable is True


@pytest.mark.parametrize("turnover,period,expected", [
    (200_000_000, rt.ANNUAL, True),        # eval_351 — exactly at the figure
    (199_999_999, rt.ANNUAL, False),
    (100_000_000, rt.SIX_MONTH, True),
    (99_999_999, rt.SIX_MONTH, False),
])
def test_both_boundaries_are_inclusive(turnover, period, expected):
    """Written strict (`>`) first; eval_351's gold corrected it — 'Kufikia TZS 200,000,000
    kwa mwaka (SIYO TU KUZIDI) kunalazimisha usajili'. The row is tagged
    `_why_hard: exactly at 200M — inclusive boundary`, so it exists to catch this."""
    assert rules_engine.vat_registration(turnover, period).applicable is expected


def test_a_monthly_rate_is_refused_not_annualised():
    """25M/month x 12 = 300M looks decisive and is a guess about the trader's future."""
    with pytest.raises(ValueError, match="neither statutory limb"):
        rules_engine.vat_registration(25_000_000, rt.MONTHLY)


# --- EFD -----------------------------------------------------------------------
# Corrected 2026-08-29: TAA Cap.438 s.44 (renumbered from s.36 by Finance Act 2023 s.54) sets no
# turnover threshold at all -- fiscal-receipt issuance is the default for everyone, exemption is
# only by a Commissioner-General public notice this engine cannot evaluate. The old tests below
# asserted the fabricated TZS 11,000,000 threshold as ground truth; replaced with tests for the
# one-ground contract: `efd_required()` always returns `applicable is True`, whatever a trader's
# turnover is or isn't, and `vat_registered` changes only the wording, never the outcome.

def test_efd_is_always_required_regardless_of_vat_registration():
    r_vat = rules_engine.efd_required(vat_registered=True)
    r_no_vat = rules_engine.efd_required(vat_registered=False)
    assert r_vat.applicable is True
    assert r_no_vat.applicable is True
    assert r_vat.inputs["ground"] == "vat_registered_and_default"
    assert r_no_vat.inputs["ground"] == "default_requirement"


def test_efd_takes_no_turnover_argument():
    """The fabricated threshold is gone; so is the parameter that fed it. A caller cannot pass
    a turnover figure back in by accident -- there is no comparison left for it to feed."""
    import inspect
    params = inspect.signature(rules_engine.efd_required).parameters
    assert "turnover" not in params
    assert "period" not in params


def test_efd_never_states_a_turnover_threshold():
    """Neither branch may reintroduce a TZS figure as if it were the EFD threshold -- that is
    exactly the defect this correction removed. (TZS figures from an unrelated presumptive-tax
    example elsewhere are not this function's concern; this checks EFD's own working text.)"""
    for r in (rules_engine.efd_required(vat_registered=True),
              rules_engine.efd_required(vat_registered=False)):
        assert "11,000,000" not in r.working and "14,000,000" not in r.working
        assert "kizingiti cha mauzo" not in r.working or "hakuna kizingiti" in r.working


# --- routing -----------------------------------------------------------------

@pytest.mark.parametrize("text,expected", [
    ("mauzo yangu ni milioni 150 kwa mwaka", "annual"),
    ("nimeuza milioni 95 katika miezi 6", "six_month"),
    ("mzunguko wangu wa nusu mwaka", "six_month"),
    ("inaingiza milioni 25 kila mwezi", "monthly"),
    ("nimeuza bidhaa za milioni 180", None),
])
def test_turnover_period(text, expected):
    assert routing.turnover_period(text) == expected


def test_every_probe_routes_where_it_says():
    for p in _probes():
        assert routing.detect_intent(p["question_sw"]) == p["expect"], p["id"]


def test_threshold_lookups_and_confirmations_keep_their_fact_route():
    """The first version of this arm required only {obligation cue + magnitude} and the sweep
    diverted 18 corpus rows, most of them wrong. These are the shapes that forced the
    own-turnover narrowing and the ask veto; each keeps VAT registration vocabulary."""
    for q in [
        "Kizingiti cha mauzo cha miezi 12 cha kusajilisha VAT kwa lazima ni TZS ngapi?",
        "Vizingiti viwili vya usajili wa VAT ni TZS ngapi kwa mwaka na kwa miezi sita?",
        "Kizingiti cha usajili wa VAT kwa mwaka mzima ni TZS 100,000,000, sivyo?",
        "Biashara inaingiza TZS milioni 25 kwa mwezi — baada ya miezi mingapi inafika "
        "kizingiti cha VAT cha TZS milioni 200?",
        "Biashara yangu ina mauzo ya TZS milioni 180 mwaka huu — ninahitaji mauzo ya ziada "
        "ya TZS ngapi kabla ya usajilishaji wa VAT wa lazima?",
        "Biashara yangu ilipata shilingi za Kenya 1,200,000 kama mapato, nimefika kizingiti "
        "cha VAT?",
    ]:
        assert routing.detect_intent(q) not in ("vat_registration", "efd_requirement"), q


def test_efd_wins_when_the_ask_is_efd():
    """th_09/th_10 name VAT registration only to say they do NOT have it. First-version
    precedence gave those rows to VAT and answered the wrong obligation."""
    q = "Mauzo yangu ni TZS 15,000,000 kwa mwaka na sina usajili wa VAT — je nahitaji EFD?"
    assert routing.detect_intent(q) == "efd_requirement"


# --- the polarity pin --------------------------------------------------------

def test_a_conditional_answer_must_not_read_as_a_flat_verdict():
    """The minimum-wage `ni halali` lesson, applied BEFORE shipping this time.

    "hutakiwi kusajili ... LAKINI kama ..." must not scan as an unconditional no to a scorer
    reading first-paragraph polarity. `reads_as_unconditional` is that reader; running it over
    our own copy is the scorer's own view of it.

    EFD has no negative/conditional case to test here since 2026-08-29 -- it is always
    unconditionally required (see test_efd_is_always_required_regardless_of_vat_registration) --
    so only VAT registration exercises the conditional-negative branch below. EFD still needs
    its own positive-control check, since a build that hedged its now-always-True answer into
    mush would still deserve to fail this test.
    """
    for turnover, period in [(150_000_000, rt.ANNUAL), (95_000_000, rt.SIX_MONTH)]:
        r = rules_engine.vat_registration(turnover, period)
        assert r.applicable is False
        assert routing.reads_as_unconditional(r.working) is False, r.working[:80]

    # …and the positive control: a settled verdict must still READ as settled, otherwise this
    # test would pass on a build that had hedged every answer into mush.
    for r in (rules_engine.vat_registration(250_000_000, rt.ANNUAL),
              rules_engine.efd_required(vat_registered=False),
              rules_engine.efd_required(vat_registered=True)):
        assert r.applicable is True
        assert routing.reads_as_unconditional(r.working) is True, r.working[:80]


def test_no_threshold_clarification_reads_as_a_verdict():
    """Never-guess copy states thresholds; it must not state an ANSWER.

    EFD_PERIOD_IS_A_RATE and EFD_NO_BASIS were removed 2026-08-29 along with the fabricated
    threshold they asked about -- there is no EFD clarification left to check here."""
    for copy in (clarification.VAT_PERIOD_IS_A_RATE, clarification.VAT_NO_PERIOD,
                 clarification.VAT_NO_TURNOVER):
        assert routing.reads_as_unconditional(copy) is False, copy[:70]
        assert copy.strip() and copy.strip()[-1] in ".?"


# --- end to end, no model ----------------------------------------------------

def test_the_threshold_path_never_calls_the_model():
    """The defect being removed is a GENERATION defect, so a single model call on this path
    means it is back."""
    for p in _probes():
        if p["expect"] not in ("vat_registration", "efd_requirement"):
            continue
        fake = FakeBackend(scripted_reply="MODEL TEXT THAT MUST NOT APPEAR")
        orch = Orchestrator(backend=fake, retriever=lambda q: [])
        reply = orch.answer(p["question_sw"])
        assert fake.call_count == 0, p["id"]
        assert "MODEL TEXT THAT MUST NOT APPEAR" not in reply.text, p["id"]


def test_monthly_rate_probes_clarify_rather_than_annualise():
    """vf_11 (EFD, monthly rate) is EXCLUDED here since 2026-08-29: EFD no longer has a period
    test to decline on (TAA Cap.438 s.44 sets no turnover threshold at all), so a monthly
    figure no longer triggers a clarification -- see test_efd_never_clarifies_on_a_monthly_rate
    below for what vf_11 is now expected to do instead. VAT (vf_05) is unaffected; its period
    logic (vat_registration's MONTHLY -> VAT_PERIOD_IS_A_RATE) was never part of this defect."""
    for pid in ("vf_05",):
        p = next(x for x in _probes() if x["id"] == pid)
        orch = Orchestrator(backend=FakeBackend(scripted_reply="X"), retriever=lambda q: [])
        reply = orch.answer(p["question_sw"])
        assert reply.sub_answers[0].needs_clarification is True, pid


def test_efd_never_clarifies_on_a_monthly_rate():
    """The replacement for vf_11's half of the test above: a monthly-rate EFD question gets an
    immediate unconditional answer now, not a clarification request, because no turnover or
    period figure can change the verdict."""
    p = next(x for x in _probes() if x["id"] == "vf_11")
    orch = Orchestrator(backend=FakeBackend(scripted_reply="X"), retriever=lambda q: [])
    reply = orch.answer(p["question_sw"])
    assert reply.sub_answers[0].needs_clarification is False, p["id"]
    assert "6,000,000" not in reply.text and "500,000" not in reply.text, (
        "no turnover figure of any kind should be echoed back -- it isn't consulted")
