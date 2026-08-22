"""PREREQ-1 regression tests — applicability routing and base rejection.

The load-bearing file here is eval/accuracy_gate/applicability_adversarial_in_scope_017.jsonl:
17 IN-SCOPE questions authored to CONTAIN the risky vocabulary of these rules, per R17. A
clean sweep of the 483-question corpora was NOT evidence of safety — the first version of the
wrong-base guard ("wrong_base AND exactly one plausible figure") passed all 483 and was still
over-broad: ap_07..ap_10 state a legitimate payroll while a wrong-base WORD sits nearby, and
all four were wrongly rejected. Only authored probes found that.

If a future cue/pattern addition trips one of these, THIS TEST FAILS — which is the point.
Do not relax a probe to make a new phrase fit; narrow the phrase instead.
"""

import json
import pathlib

import pytest

from chike import routing, rules_engine, swahili_numbers as swn
from chike.extraction import REQUIRED_FIELDS, SlotExtractor
from chike.model_abstraction import ModelBackend
from chike.rules_engine import rates

PROBES_PATH = (pathlib.Path(__file__).resolve().parents[1]
               / "eval" / "accuracy_gate" / "applicability_adversarial_in_scope_017.jsonl")


class _Silent(ModelBackend):
    """No model opinion — the deterministic layer decides these cases on its own."""

    def generate(self, prompt, params=None):
        return ""


def _branch(question):
    """The routing/compute branch a question lands on, without a model or network.

    Mirrors Orchestrator._answer_compute's order of decisions. Kept as a small local
    reimplementation on purpose: it fails loudly if that order changes, which is exactly the
    drift these probes exist to catch.
    """
    ct = routing.detect_intent(question)
    if ct not in REQUIRED_FIELDS:
        return "ambiguous_multi" if ct == "ambiguous_multi" else "fact"

    if ct == "sdl" and routing.asks_applicability(question):
        ordinal = routing.count_transition_ordinal(question)
        if ordinal is not None and ordinal >= rates.SDL_MIN_EMPLOYEES:
            return "count_transition"
    if rules_engine.supports_applicability(ct) and routing.is_applicability_question(question):
        return "applicability"

    required = REQUIRED_FIELDS[ct]
    extraction = SlotExtractor(_Silent()).extract(question, required, ct)
    if extraction.usable(required):
        return "compute"
    if swn.detect_rejectable_base(question, ct):
        return "base_rejection"
    return "compute_clarify"


def _load():
    with PROBES_PATH.open(encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


PROBES = _load()

# What each declared expectation permits. 'compute_or_clarify' is the key one: the probe is
# NOT asserting the question computes today (several are blocked by PREREQ-2 extraction gaps)
# — it asserts only that the base is never rejected out from under a stated payroll.
_ALLOWED = {
    "compute_or_clarify": {"compute", "compute_clarify"},
    "compute": {"compute"},
    "applicability": {"applicability"},
    "applicability_any": {"applicability", "compute", "compute_clarify"},
    "not_asserted": {"compute_clarify", "compute", "applicability"},
}


def test_probe_file_is_complete():
    assert len(PROBES) == 17
    assert all(p["in_scope"] for p in PROBES)
    assert all(p["guards_against"].strip() for p in PROBES), "every probe states its guard"


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_adversarial_in_scope_probe_keeps_its_branch(probe):
    branch = _branch(probe["question"])
    allowed = _ALLOWED[probe["expected_branch"]]
    assert branch in allowed, (
        f"{probe['id']} landed on {branch!r}, expected one of {sorted(allowed)}. "
        f"Guard: {probe['guards_against']}")


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_no_probe_ever_gets_a_base_rejection(probe):
    """The single most important invariant: not one of these 17 in-scope questions may be
    told its figure is not a payroll base. ap_07..ap_10 failed this against the first guard."""
    assert _branch(probe["question"]) != "base_rejection", probe["guards_against"]


# ── the cases the rules are FOR (the positive side of the same boundary) ──────────

def test_wrong_base_is_rejected_when_it_is_the_only_figure():
    q = "Nimechukua deni la benki TZS 6,700,000 kwa ajili ya biashara, hii inaongeza SDL yangu kiasi gani?"
    assert swn.detect_rejectable_base(q, "sdl") == "wrong_base"
    assert _branch(q) == "base_rejection"


def test_object_count_is_rejected_as_a_base():
    q = "Nimefunga mashine 9 mpya za uzalishaji, SDL yangu itapanda kwa kiasi gani?"
    assert swn.detect_rejectable_base(q, "sdl") == "object_count"


def test_rejection_names_the_correct_base_and_never_only_asks_for_a_salary():
    working = rules_engine.reject_base("wcf", 25_000_000).working
    assert "asilimia 0.5" in working and "mishahara" in working   # names the real base
    assert "TZS 25,000,000" in working and "si mshahara" in working  # rejects the figure
    assert working.startswith("Hapana.")


def test_rejection_invitation_is_optional_and_follows_the_correction():
    """Correction mandatory, invitation optional — the failure mode is demanding a salary
    IN PLACE OF the correction, not offering it after."""
    with_invite = rules_engine.reject_base("sdl", 850_000).working
    without = rules_engine.reject_base("sdl", 850_000, invite=False).working
    assert "Nipe jumla ya mishahara" in with_invite
    assert "Nipe" not in without
    assert without.startswith("Hapana. SDL inatozwa kwa")


def test_wrong_base_word_beside_a_real_payroll_is_not_rejected():
    """The exact class the R17 probes exposed (ap_07)."""
    q = "pamoja na kodi ya pango, nalipa mishahara TZS 3,600,000 kwa wafanyakazi 11"
    assert swn.detect_rejectable_base(q, "sdl") is None


def test_multiple_figures_stay_with_prereq2_not_the_rejection_path():
    """eval_324 / nat_21: a real payroll figure IS present among several, merely unparsed."""
    q = ("Biashara yangu ina mishahara TZS 4,800,000 kwa watu 13, na madeni TZS 2,000,000, "
         "na faida TZS 1,000,000 - SDL yangu ni ngapi?")
    assert swn.detect_rejectable_base(q, "sdl") is None


# ── the count-transition veto is NOT loosened ────────────────────────────────────

def test_threshold_crossing_is_answered_at_or_above_the_threshold():
    q = ("Biashara yangu ina wafanyakazi 9 na ninaajiri mfanyakazi wa 10 katikati ya mwezi "
         "- je, SDL inatakiwa kulipwa mwezi huo huo?")
    assert routing.count_transition_ordinal(q) == 10
    assert routing.is_applicability_question(q) is False    # the veto still fires
    assert routing.asks_applicability(q) is True            # but the intent is recognised
    assert _branch(q) == "count_transition"
    assert rules_engine.sdl_crosses_threshold(10).working.startswith("Ndiyo.")


def test_threshold_crossing_below_the_threshold_still_declines():
    q = "nina wafanyakazi 4 na ninaajiri mfanyakazi wa 5 mwezi huu, je SDL inatakiwa kulipwa"
    assert routing.count_transition_ordinal(q) == 5
    assert _branch(q) != "count_transition"
    with pytest.raises(ValueError):
        rules_engine.sdl_crosses_threshold(5)


# ── the dropped cue, kept as a regression ────────────────────────────────────────

def test_nahusika_na_is_not_an_applicability_cue():
    """'nahusika na' substring-matches 'i-nahusika na' in eval_100 ("je, NSSF inahusika na
    mshahara wote?"), a base-SCOPE question that passes today; routing it to nssf_applies()
    would answer a different question. Dropped deliberately — do not re-add."""
    assert "nahusika na" not in routing._APPLICABILITY_CUES
    q = ("Mfanyakazi anapata mshahara wa jumla wa TZS milioni 2 kwa mwezi - je, NSSF "
         "inahusika na mshahara wote?")
    assert routing.is_applicability_question(q) is False


def test_path_2b_can_never_reach_the_production_fabrication_guard():
    """chike/pipeline_v15.py IS production, and it imports routing for exactly one predicate:
    is_uncomputable_payroll_amount. PREREQ-1 edits routing, so the isolation must be proven,
    not assumed.

    It holds structurally: path 2b requires is_applicability_question, which requires NO money
    'how-much' ask, while is_uncomputable_payroll_amount requires one. The two are therefore
    disjoint by construction. Verified empirically over 500 questions (483 corpora + these 17)
    with zero differences against HEAD before the change; this test pins the invariant so a
    future widening of path 2b cannot silently alter production behaviour."""
    assert PROBES, "PROBES is empty -- this loop would assert nothing (dead-anchor census, 2026-08-22)"
    for probe in PROBES:
        q = probe["question"]
        if routing.is_uncomputable_payroll_amount(q):
            assert not routing.asks_applicability(q), (
                f"{probe['id']}: a question cannot be both an applicability ask and an "
                "uncomputable-payroll-amount fabrication case")


def test_natural_applicability_requires_a_number():
    """Narrowest form: adv_06 ("...je bima ya ajali inatosha au nachangia WCF") has no number
    and stays on the fact path, where the insurance half of the question can be answered."""
    assert routing.detect_intent(
        "mfanyakazi wangu ameumia je bima ya ajali inatosha au nachangia WCF") == "none"
    assert routing.detect_intent(
        "tuko na vibarua 8 wa kudumu na wawili wa muda kwenye gereji yangu je ile tozo ya "
        "mafunzo kwa waajiri inanihusu") == "sdl"
