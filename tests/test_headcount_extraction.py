"""Headcount extraction (C1-C4) — the item that exists because pattern F's reach was MEASURED.

Pattern F was assumed to close the multi-part clarifications. It does not: multi-levy
decomposition already worked (eval_319 emitted 2 clarifications, eval_320 emitted 4, one per
levy). What blocked those rows was parse_count returning None where a headcount is written in
plain Swahili — and the dominant gap was that _PEOPLE_NOUN carries only PLURAL forms plus
'kibarua', so 'mfanyakazi mmoja' was invisible.

  C1  singular person + 'mmoja' -> 1                          closes eval_320
  C2  digit + pay verb ('18 wenye', '14 wanaopata')           closes nothing alone; needs C4
  C3  count_transition_ordinal also sees 'kufikia N'          closes nothing; SAFETY for C1/C2
  C4  'kila mmoja' governs the SALARY, 'jumla/wote' the ASK   closes eval_275's copy

C4 IS THE SUBSTANTIVE ONE. Treating the two markers as contradictory is a scope error: they
govern different clauses. When the headcount is known there is exactly one arithmetic reading,
so the veto is resolved rather than fired. Fixing it at source is what makes eval_275's
clarification correct without rewording anything.

C3 CLOSES NOTHING AND SHIPS ANYWAY. C1 and C2 make more questions yield a static headcount;
count_transition_ordinal is the veto that stops a static count being treated as the whole
story at the consumer. Widening the parser while leaving its safety net at one surface form is
how a nat_07 gets made — this cycle has produced three already.

MEASURED: 587-question deterministic sweep, 13 rows change a predicate, 4 change an ANSWER
(eval_275, eval_280, eval_319, eval_320), all four matching gold exactly, zero regressions.
The other 9 were checked individually for newly reachable defects and none exists: eval_260 is
held by the wrong-base rejection, and WCF/NSSF applicability take no employee_count at all, so
a recovered count of 1 cannot make a threshold-free levy 'not applicable'.

hc_07 IS A PROBE I GOT WRONG AND REWROTE. See its guards_against note.
"""

import json
import pathlib

import pytest

from chike import routing, swahili_numbers as swn
from chike.extraction import SlotExtractor, REQUIRED_FIELDS
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES_PATH = (pathlib.Path(__file__).resolve().parents[1]
               / "eval" / "accuracy_gate" / "headcount_extraction_probes_012.jsonl")
PROBES = [json.loads(line) for line in PROBES_PATH.open(encoding="utf-8") if line.strip()]
BY_ID = {p["id"]: p for p in PROBES}


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def _answer(question):
    orch = Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[])
    return orch.answer(question)


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_probe_headcount_expectation(probe):
    assert swn.parse_count(probe["question"]) == probe["expect_count"]


@pytest.mark.parametrize(
    "probe", [p for p in PROBES if "expect_transition" in p],
    ids=[p["id"] for p in PROBES if "expect_transition" in p])
def test_probe_transition_expectation(probe):
    assert routing.count_transition_ordinal(probe["question"]) == probe["expect_transition"]


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_every_probe_carries_a_guards_against_note(probe):
    assert probe["guards_against"].strip()
    assert probe["in_scope"] is True


# --- C1: the singular people-nouns -----------------------------------------

def test_c1_singular_forms_all_resolve_to_one():
    for noun in ("mfanyakazi", "mfanyikazi", "mtumishi", "mwajiriwa", "kibarua", "mtu"):
        assert swn.parse_count(f"Nina {noun} mmoja tu — SDL yangu ni ngapi?") == 1, noun


def test_c1_is_appended_last_so_a_stated_plural_always_wins():
    # hc_01: the ordering guarantee, stated as a property rather than a single example.
    assert swn.parse_count(BY_ID["hc_01"]["question"]) == 15
    assert swn.parse_count("Nina watu 30 na mfanyakazi mmoja ni meneja — SDL?") == 30


def test_c1_one_employee_sdl_amount_states_zero():
    text = _answer(BY_ID["hc_02"]["question"]).text
    assert "TZS 0" in text and "chini ya 10" in text
    assert "31,500" not in text                      # 3.5% of 900,000 must never appear


# --- C2: digit + pay verb ---------------------------------------------------

def test_c2_pay_verb_surfaces():
    assert swn.parse_count("hasa ni 18 wenye mshahara wa TZS 480,000") == 18
    assert swn.parse_count("wafanyakazi wangu, ambao ni 14 wanaopata TZS 500,000") == 14


def test_c2_does_not_read_a_money_figure_as_a_count():
    assert swn.parse_count(BY_ID["hc_05"]["question"]) is None


# --- C3: the transition veto, widened --------------------------------------

def test_c3_new_surfaces_are_detected():
    assert routing.count_transition_ordinal("nikaongeza mmoja kufikia 10") == 10
    assert routing.count_transition_ordinal("Machi nikafikia watu 12") == 12
    assert routing.count_transition_ordinal("hadi kufikia wafanyakazi 11") == 11


def test_c3_keeps_the_original_surface():
    assert routing.count_transition_ordinal("ninaajiri mfanyakazi wa 10 mwezi huu") == 10


def test_c3_does_not_fire_on_a_vat_threshold_question():
    assert routing.count_transition_ordinal(BY_ID["hc_11"]["question"]) is None


def test_c3_and_c1_together_keep_the_crossing_visible():
    # hc_07: a static 9 AND a transition to 10. Neither alone is the answer.
    q = BY_ID["hc_07"]["question"]
    assert swn.parse_count(q) == 9
    assert routing.count_transition_ordinal(q) == 10
    assert "TZS 0" not in _answer(q).text            # never 'no SDL' for a crossing employer


# --- C4: per-person vs aggregate is SCOPE, not conflict ---------------------

def _payroll(question, computation_type):
    # NOTE the signature order: _deterministic(text, required, computation_type). Getting
    # these two the wrong way round makes `required` a STRING, so `next(f for f in required
    # if f in _AMOUNT_FIELDS)` iterates characters, finds nothing, and the amount field is
    # silently never computed — a passing-looking helper that measures nothing. It cost a
    # false failure here before the argument order was checked.
    se = SlotExtractor.__new__(SlotExtractor)
    det, _veto = se._deterministic(question, REQUIRED_FIELDS[computation_type],
                                   computation_type)
    return det.get("gross_monthly_payroll")


def test_c4_resolves_per_person_times_headcount():
    field = _payroll(BY_ID["hc_06"]["question"], "nssf")
    assert field is not None and field[0] == 7200000  # 12 x 600,000


def test_c4_veto_stands_when_the_headcount_is_unknown():
    field = _payroll("Kila mfanyakazi anapata TZS 500,000, jumla ya NSSF ni ngapi?", "nssf")
    assert field is None or field[1].name == "LOW"


def test_c4_veto_stands_when_several_figures_are_in_play():
    assert swn.parse_count(BY_ID["hc_10"]["question"]) is None
    reply = _answer(BY_ID["hc_10"]["question"])
    assert "= TZS" not in reply.text                  # no computed amount


def test_c4_does_not_disturb_a_plain_aggregate_question():
    text = _answer("Nina wafanyakazi 14 wenye jumla ya mishahara TZS 7,000,000 — SDL ni ngapi?").text
    assert "245,000" in text


# --- the four rows the item exists to fix ----------------------------------

def test_eval_280_computes_the_gold_figure():
    text = _answer("Tuna wafanyakazi wengi sana karibu, lakini hasa ni 18 wenye mshahara wa "
                   "TZS 480,000 kila mmoja — NSSF ya wote?").text
    assert "1,728,000" in text                       # 20% of 18 x 480,000


def test_eval_319_computes_both_levies():
    text = _answer("Kama nikizingatia kwamba wafanyakazi wangu, ambao ni 14 wanaopata kila "
                   "mmoja TZS 500,000, wanastahili NSSF, je jumla ni ngapi na SDL yao pia?").text
    assert "245,000" in text and "1,400,000" in text


def test_eval_320_computes_all_four_with_sdl_nil():
    text = _answer("Nilipe SDL, NSSF, PAYE na WCF kwa mfanyakazi mmoja mwenye TZS 800,000 — "
                   "nionyeshe vyote.").text
    assert "TZS 0" in text                            # SDL: one employee, below threshold
    assert "78,000" in text                           # PAYE band 4
    assert "80,000" in text                           # NSSF employee share
    assert "4,000" in text                            # WCF 0.5%


def test_eval_275_asks_the_FX_question_not_the_per_person_one():
    text = _answer("Nina wafanyakazi 12 kila mmoja analipwa dola 300, jumla ya NSSF ya wote "
                   "ni ngapi?").text
    assert "sarafu ya kigeni" in text
    assert "kwa kila mfanyakazi au ni jumla ya wote" not in text
