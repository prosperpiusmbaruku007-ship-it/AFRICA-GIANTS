"""Phase D re-run items 3 and 4 — two correct answers that were scored as failures, and two
clarifications that asked the wrong question.

Neither change alters a VERDICT. eval_378 and eval_393 were both judge-confirmed CORRECT and
failed the regex scorer on shape alone: one never stated the figure a 'ni ngapi' question
asks for, the other opened 'Hapana.' after model text that had already opened 'Sawa kabisa',
putting two opposite polarity markers in one reply. eval_291 and eval_294 keep declining to
compute — only the question asked back changes.

THE ZERO BRANCH NEARLY SHIPPED A CONFIDENT WRONG NUMBER, TWICE. Its first draft read
parse_count directly and answered 'SDL ni TZS 0' for
  * gp_02, "vibarua 8 ... na 4 ..." — a TWELVE-person employer, and
  * "wafanyakazi 9 na ninaajiri mfanyakazi wa 10" — where SDL is in fact due.
Both were found by the 569-question sweep, not by these probes. Hence two guards:
sole_headcount (decline when a second count exists in any form) and the M4 count-transition
veto (a stated crossing means the static count is not the whole story). os_03 and os_04 pin
them; os_05 pins that a real computation is untouched.
"""

import json
import pathlib
from decimal import Decimal

import pytest

from chike import clarification, routing, rules_engine, swahili_numbers as swn
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES_PATH = (pathlib.Path(__file__).resolve().parents[1]
               / "eval" / "accuracy_gate" / "output_shape_probes_010.jsonl")
PROBES = [json.loads(line) for line in PROBES_PATH.open(encoding="utf-8") if line.strip()]


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def _orch():
    return Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[])


def test_probe_file_is_complete():
    assert len(PROBES) == 10
    assert all(p["in_scope"] and p["guards_against"].strip() for p in PROBES)


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_output_shape_probe(probe):
    q, guard, expect = probe["question"], probe["guards_against"], probe["expect"]
    if expect == "zero_amount":
        reply = _orch().answer(q)
        assert not reply.needs_clarification, guard
        assert "TZS 0" in reply.text, guard
    elif expect == "computed":
        reply = _orch().answer(q)
        assert not reply.needs_clarification, guard
        assert "TZS 175,000" in reply.text, guard
    elif expect == "clarify":
        assert _orch().answer(q).needs_clarification, guard
    elif expect == "clarify_monthly":
        reply = _orch().answer(q)
        assert reply.needs_clarification, guard
        assert "MWEZI" in reply.text, guard
        assert "kwa kila mfanyakazi au ni jumla ya wote" not in reply.text, guard
    elif expect == "agree_negated":
        assert routing.confirms_negated_premise(q) is True, guard
        assert _orch().answer(q).text.startswith("Ndiyo"), guard
    elif expect == "not_agree_negated":
        assert routing.confirms_negated_premise(q) is False, guard
    elif expect == "negated_but_unreachable":
        # The tag predicate fires; the SECOND gate is what keeps the lead correct.
        assert routing.confirms_negated_premise(q) is True, guard
        assert routing.detect_intent(q) == "none", guard
        assert not _orch().answer(q).text.startswith("Ndiyo"), guard
    else:                                                    # pragma: no cover
        raise AssertionError(f"unknown expectation {expect!r}")


# ── item 3a: the amount below the threshold is a FIGURE, not only a verdict ─────

def test_zero_below_threshold_states_the_figure():
    r = rules_engine.sdl_zero_below_threshold(8)
    assert r.applicable is False and r.amount == Decimal(0)
    assert "TZS 0" in r.working


def test_compute_sdl_below_threshold_states_the_same_figure():
    """compute_sdl delegates, so a caller that DOES have the payroll gets identical copy."""
    r = rules_engine.compute_sdl(Decimal("5000000"), 8)
    assert r.applicable is False and r.amount == Decimal(0)
    assert r.working == rules_engine.sdl_zero_below_threshold(8).working


def test_zero_answer_refuses_to_speak_for_an_employer_over_the_threshold():
    with pytest.raises(ValueError, match="at or above"):
        rules_engine.sdl_zero_below_threshold(10)


def test_sole_headcount_declines_when_a_second_count_exists():
    q = "vibarua 8 wanalipwa TZS 1,500 kwa kipande na 4 wanalipwa TZS 2,000 kwa kipande"
    assert swn.parse_count(q) == 8, "parse_count still returns the FIRST group — by design"
    assert swn.sole_headcount(q) is None, "8 of 12 must never stand as the whole headcount"
    assert swn.sole_headcount("Kampuni ina wafanyakazi 8 wenye mishahara TZS 5,000,000") == 8


def test_states_no_employees_requires_an_explicit_negation():
    assert swn.states_no_employees("sina wafanyakazi kabisa") is True
    assert swn.states_no_employees("Mimi ni mjasiriamali peke yangu") is True
    # The mere ABSENCE of a headcount is not a statement that there are none.
    assert swn.states_no_employees("SDL yangu ni ngapi?") is False


# ── item 3b: polarity ──────────────────────────────────────────────────────────

def test_agreement_relead_refuses_an_applicable_verdict():
    """A negated premise the verdict CONTRADICTS must still be denied, never agreed with."""
    with pytest.raises(ValueError, match="applicable=True"):
        rules_engine.agree_with_negated_premise(rules_engine.sdl_applies(12))


def test_only_two_corpus_questions_carry_a_negated_confirmation_tag():
    """17 confirmation-tag questions exist across the corpora; 15 state a POSITIVE premise
    that is false, and their correct lead really is 'Hapana.'."""
    false_premise_tags = [
        "Kiwango cha WCF ni asilimia 3.5 ya mishahara, sivyo?",
        "Kizingiti cha SDL ni wafanyakazi 4, sivyo?",
        "Kiwango cha juu kabisa cha PAYE ni asilimia 25, sivyo?",
        "Ada ya kuwasilisha annual return BRELA ni TZS 2,500, sivyo?",
    ]
    assert not any(routing.confirms_negated_premise(q) for q in false_premise_tags)
    assert routing.confirms_negated_premise("Kampuni yenye wafanyakazi 9 haitakiwi kulipa "
                                            "SDL, sivyo?")


def test_a_tag_is_required_not_merely_a_negation():
    assert routing.confirms_negated_premise("Kampuni yenye wafanyakazi 9 haitakiwi kulipa "
                                            "SDL?") is False


# ── item 4: the question asked back ────────────────────────────────────────────

def test_per_unit_pay_changes_the_question_not_the_verdict():
    reasons = ["gross_monthly_payroll: low (multiple figures ['320000', '2'] "
               "— role ambiguous)"]
    per_person = clarification.compute_clarification("nssf", reasons)
    per_unit = clarification.compute_clarification(
        "nssf", reasons, "Analipwa TZS 320,000 kila wiki mbili (bi-weekly), NSSF yake?")
    assert "kwa kila mfanyakazi au ni jumla ya wote" in per_person
    assert "MWEZI" in per_unit and "kwa kila mfanyakazi au ni jumla ya wote" not in per_unit


def test_sdl_per_unit_copy_also_asks_for_the_headcount():
    """SDL is charged on ALL employees above a 10-person threshold, so eval_294's driver
    cannot be answered from the trip rate alone however it is converted."""
    copy = clarification.compute_clarification(
        "sdl",
        ["gross_monthly_payroll: low (multiple figures ['80000', '15'] — role ambiguous)",
         "employee_count: missing"],
        "Dereva analipwa TZS 80,000 kwa safari, anafanya safari 15 kwa mwezi — SDL?")
    assert "MWEZI" in copy and "idadi ya wafanyakazi" in copy and "kizingiti" in copy


def test_question_argument_is_optional():
    """Existing callers pass two arguments; the copy must not depend on the third."""
    assert clarification.compute_clarification("paye", ["monthly_salary: missing"])
