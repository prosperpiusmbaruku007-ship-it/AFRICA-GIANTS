"""PREREQ-2 Tiers 1-2 regression tests — narrowed false vetoes + anchored figure selection.

The load-bearing file is eval/accuracy_gate/extraction_adversarial_in_scope_016.jsonl. Per R17,
these are IN-SCOPE questions authored to CONTAIN the vocabulary each narrowing touches, because
extraction widening is where a too-permissive parse turns an honest clarification into a
confident wrong number.

The 500-question sweep already caught three such defects in the first version of this patch —
the most serious being eval_327, where anchoring on a multi-group question would have computed
WCF on ONE group's salary (TZS 3,500) instead of the real payroll (TZS 23,000). ex_07/08/09
pin that class. Do not relax a probe to make a future widening fit; narrow the widening.
"""

import json
import pathlib

import pytest

from chike import routing, rules_engine, swahili_numbers as swn
from chike.extraction import (SlotExtractor, REQUIRED_FIELDS,
                              APPLICABILITY_REQUIRED_FIELDS)
from chike.model_abstraction import ModelBackend

PROBES_PATH = (pathlib.Path(__file__).resolve().parents[1]
               / "eval" / "accuracy_gate" / "extraction_adversarial_in_scope_016.jsonl")


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


_EX = SlotExtractor(_Silent())


def _branch(question):
    """Branch + the deterministic working, mirroring Orchestrator._answer_compute."""
    ct = routing.detect_intent(question)
    if ct not in REQUIRED_FIELDS:
        return "fact", None
    if ct == "sdl" and routing.asks_applicability(question):
        ordinal = routing.count_transition_ordinal(question)
        if ordinal is not None and ordinal >= rules_engine.rates.SDL_MIN_EMPLOYEES:
            return "count_transition", None
    if rules_engine.supports_applicability(ct) and routing.is_applicability_question(question):
        required = APPLICABILITY_REQUIRED_FIELDS[ct]
        if required:
            extraction = _EX.extract(question, required, ct)
            if not extraction.usable(required):
                return "clarify", None
            inputs = {n: extraction.fields[n].value for n in required}
        else:
            inputs = {}
        return "applicability", rules_engine.applicability(ct, **inputs).working
    required = REQUIRED_FIELDS[ct]
    extraction = _EX.extract(question, required, ct)
    if extraction.usable(required):
        inputs = {n: extraction.fields[n].value for n in required}
        if ct == "nssf":
            inputs["party"] = routing.nssf_party(question)
        if ct == "paye":
            inputs["resident"] = routing.paye_resident(question)
        return "compute", rules_engine.compute(ct, **inputs).working
    if swn.detect_rejectable_base(question, ct):
        return "base_rejection", None
    return "clarify", None


PROBES = [json.loads(line) for line in PROBES_PATH.open(encoding="utf-8") if line.strip()]


def test_probe_file_is_complete():
    assert len(PROBES) == 16
    assert all(p["in_scope"] and p["guards_against"].strip() for p in PROBES)


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_adversarial_extraction_probe(probe):
    branch, _ = _branch(probe["question"])
    assert branch == probe["expected_branch"], probe["guards_against"]


# ── the guard that matters most: multi-group must never anchor ───────────────────

def test_multi_group_never_anchors_on_one_groups_salary():
    """eval_327. Anchoring here would compute WCF = 0.5% x 700,000 = TZS 3,500 in place of
    0.5% x 4,600,000 = TZS 23,000 — a confident wrong number replacing a clarification."""
    q = ("Nina wafanyakazi 10, kati yao 4 wana mishahara ya TZS 700,000 na 6 wana "
         "TZS 300,000, nataka WCF na SDL")
    assert swn.has_multiple_groups(q) is True
    assert swn.select_anchored_amount(q, [swn.Decimal("700000"), swn.Decimal("300000")]) \
        == (None, None)
    assert _branch(q)[0] == "clarify"


def test_multi_period_never_answers_for_one_period():
    q = ("Mwezi Januari nilikuwa na watu 9, Februari nikaongeza mmoja kufikia 10, mishahara "
         "ni TZS 3,000,000 kila mwezi - SDL ya Januari na Februari?")
    assert swn.has_multiple_groups(q) is True
    assert swn.parse_count(q) is None
    assert _branch(q)[0] == "clarify"


def test_compound_headcount_declines_rather_than_asserting_a_partial_count():
    """edge_p04: 8 permanent + 2 temporary = 10, so SDL APPLIES. Returning 8 would answer
    'Hapana' — worse than the clarification it replaced. Aggregation is pattern B."""
    assert swn.parse_count("tuko na vibarua 8 wa kudumu na wawili wa muda") is None


# ── the narrowings still fire where they should ──────────────────────────────────

def test_vague_and_approximation_still_veto_without_a_precision_marker():
    assert swn.detect_vague_quantity("nina wafanyakazi wachache") is True
    assert swn.detect_approximation("analipwa kama TZS 500,000 hivi") is True
    assert swn.has_precision_override("Mshahara wake unafika TZS 920,000 hivi") is False


def test_kiasi_cha_is_exempt_but_bare_kiasi_is_not():
    assert swn.detect_vague_quantity("zinabadilisha kiasi cha SDL ninachodaiwa") is False
    assert swn.detect_vague_quantity("mishahara yetu ni mingi kiasi") is True


def test_kama_narrowed_to_the_approximative_sense():
    assert swn.detect_approximation("Kama kawaida mishahara inabadilika") is False
    assert swn.detect_approximation("mimi kama mwajiri nachangia") is False
    assert swn.detect_approximation("anapata kama laki sita") is True


def test_antecedent_narrowing_keeps_the_rc2_case():
    assert swn.detect_missing_antecedent("je ile tozo ya mafunzo inanihusu") is False
    assert swn.detect_missing_antecedent("Ile hesabu ya wiki iliyopita ya PAYE") is True
    assert swn.detect_missing_antecedent("wale wawili waliobaki") is True


def test_pamoja_na_only_fires_on_a_real_pay_component():
    assert swn.detect_allowance_ambiguity("mwajiri pamoja na mfanyakazi") is False
    assert swn.detect_allowance_ambiguity("mshahara pamoja na posho ya usafiri") is True


def test_precision_override_needs_an_explicit_marker():
    assert swn.has_precision_override("lakini jumla hasa ni TZS 3,750,000") is True
    assert swn.has_precision_override("sawa TZS 610,000 kamili") is True
    assert swn.has_precision_override("unafika TZS 920,000 hivi") is False


def test_payroll_anchor_beats_a_wrong_base_figure():
    """eval_324: the user LABELLED the payroll, so 'faida' elsewhere must not veto it."""
    q = ("Biashara yangu ina mishahara TZS 4,800,000 kwa watu 13, na madeni TZS 2,000,000, "
         "na faida TZS 1,000,000 - SDL yangu ni ngapi?")
    branch, working = _branch(q)
    assert branch == "compute"
    assert "TZS 168,000" in working


def test_first_person_employer_phrasing_gives_the_employer_share():
    """Latent until the 'kama' narrowing made nat_07 computable; the 20% default would have
    asserted TZS 160,000 where the employer share is TZS 80,000."""
    q = ("mfanyakazi wangu analipwa laki nane kwa mwezi mimi kama mwajiri nachangia kiasi "
         "gani kwa ile ya uzeeni")
    assert routing.nssf_party(q) == "employer"
    assert "TZS 80,000" in _branch(q)[1]
