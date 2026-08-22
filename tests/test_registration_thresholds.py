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


# --- EFD ---------------------------------------------------------------------

def test_vat_registration_short_circuits_efd_entirely():
    r = rules_engine.efd_required(vat_registered=True)
    assert r.applicable is True
    assert r.inputs["ground"] == "vat_registered"
    assert "turnover" not in r.inputs, "turnover must not be consulted when registration settles it"


def test_efd_below_threshold_leaves_vat_registration_open():
    r = rules_engine.efd_required(8_000_000)
    assert r.applicable is False
    assert r.inputs["condition_open"] == "vat_registration"


def test_efd_boundary_is_inclusive():
    assert rules_engine.efd_required(11_000_000).applicable is True
    assert rules_engine.efd_required(10_999_999).applicable is False


def test_efd_refuses_a_non_annual_period():
    with pytest.raises(ValueError, match="ANNUAL turnover test"):
        rules_engine.efd_required(500_000, period=rt.MONTHLY)


def test_efd_with_no_basis_at_all_raises_rather_than_guessing():
    with pytest.raises(ValueError, match="nothing to test"):
        rules_engine.efd_required()


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
    """
    for turnover, period in [(150_000_000, rt.ANNUAL), (95_000_000, rt.SIX_MONTH)]:
        r = rules_engine.vat_registration(turnover, period)
        assert r.applicable is False
        assert routing.reads_as_unconditional(r.working) is False, r.working[:80]

    below_efd = rules_engine.efd_required(8_000_000)
    assert routing.reads_as_unconditional(below_efd.working) is False

    # …and the positive control: a settled verdict must still READ as settled, otherwise this
    # test would pass on a build that had hedged every answer into mush.
    for r in (rules_engine.vat_registration(250_000_000, rt.ANNUAL),
              rules_engine.efd_required(15_000_000),
              rules_engine.efd_required(vat_registered=True)):
        assert r.applicable is True
        assert routing.reads_as_unconditional(r.working) is True, r.working[:80]


def test_no_threshold_clarification_reads_as_a_verdict():
    """Never-guess copy states thresholds; it must not state an ANSWER."""
    for copy in (clarification.VAT_PERIOD_IS_A_RATE, clarification.VAT_NO_PERIOD,
                 clarification.VAT_NO_TURNOVER, clarification.EFD_PERIOD_IS_A_RATE,
                 clarification.EFD_NO_BASIS):
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
    for pid in ("vf_05", "vf_11"):
        p = next(x for x in _probes() if x["id"] == pid)
        orch = Orchestrator(backend=FakeBackend(scripted_reply="X"), retriever=lambda q: [])
        reply = orch.answer(p["question_sw"])
        assert reply.sub_answers[0].needs_clarification is True, pid
        # the annualised figure must not appear anywhere in the reply
        assert "300,000,000" not in reply.text and "6,000,000" not in reply.text, pid
