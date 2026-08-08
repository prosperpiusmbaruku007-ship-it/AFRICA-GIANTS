"""Two clarifications that were CORRECT to decline but asked the wrong question.

Neither change alters a verdict. eval_264 and eval_270 both keep refusing to compute; only
the reply changes — from a question the user cannot usefully answer to the one that names
the real gap.

  eval_264  "risiti 780 kwa mwezi, SDL ... ni ngapi?"   -> asked "how many employees?"
            A receipt COUNT is not a payroll base at all, which is exactly what
            detect_rejectable_base('object_count') exists to say. 'risiti' was simply absent
            from _OBJECT_COUNT alongside invoice/ankara.
  eval_270  "zamu 3 kwa siku ..., NSSF ya JUMLA ..."    -> asked about ONE worker's month
            The ask is aggregate; the answer needs the whole payroll, not one salary.

THE RISK IN cc_01 IS cc_02. Adding a noun to _OBJECT_COUNT is precisely the kind of widening
that over-fires, so the adversarial probe is the one where a receipt count sits NEXT TO a
real payroll figure and the base must NOT be rejected (the _PAYROLL_WORD guard). Per R17 a
clean corpus sweep is not evidence on its own — cc_02, cc_04, cc_05 and cc_08 are the rows
that can actually fail if either change is too broad.

eval_275 and eval_305 were adjudicated in the same group and are deliberately NOT fixed here:
  * eval_275's wrong question ("per person or total?" when both are stated and the real gap
    is the FX rate) is a symptom of the per-person/aggregate conflict veto, which the
    headcount-extraction item removes at source. Rewording it here would be dead code.
  * eval_305 ("Kiwango cha SDL ni ngapi kwa mtu mwenye mshahara wa TZS 480,000?") needs an
    answer that states the 3.5% RATE and that it is not per-person. That is a new answer
    shape, not copy, and it is logged rather than smuggled into a copy commit.
"""

import json
import pathlib

import pytest

from chike import clarification, swahili_numbers as swn
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES_PATH = (pathlib.Path(__file__).resolve().parents[1]
               / "eval" / "accuracy_gate" / "clarification_copy_probes_008.jsonl")
PROBES = [json.loads(line) for line in PROBES_PATH.open(encoding="utf-8") if line.strip()]
BY_ID = {p["id"]: p for p in PROBES}


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def _answer(question):
    orch = Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[])
    return orch.answer(question)


# --- the object-count base rejection ---------------------------------------

def test_cc01_receipt_count_is_not_a_payroll_base():
    q = BY_ID["cc_01"]["question"]
    assert swn.detect_rejectable_base(q, "sdl") == "object_count"
    text = _answer(q).text
    assert "mishahara" in text                       # names the real base
    assert "idadi ya wafanyakazi walio kwenye orodha" not in text   # not the old wrong ask


def test_cc02_a_receipt_count_beside_a_real_payroll_does_NOT_reject_the_base():
    # The guard that makes cc_01 safe. _PAYROLL_WORD is present, so the base stands.
    q = BY_ID["cc_02"]["question"]
    assert swn.detect_rejectable_base(q, "sdl") is None


def test_cc05_preexisting_object_counts_are_unchanged():
    assert swn.detect_rejectable_base(BY_ID["cc_05"]["question"], "sdl") == "object_count"


def test_cc07_idadi_ya_risiti_without_a_digit_never_computes():
    text = _answer(BY_ID["cc_07"]["question"]).text
    assert "TZS" not in text or "asilimia" in text   # no fabricated figure


def test_cc08_object_count_plus_headcount_but_no_payroll_still_declines():
    reply = _answer(BY_ID["cc_08"]["question"])
    assert reply.text.strip()                        # something is said
    assert "= TZS" not in reply.text                 # but never a computed amount


# --- the aggregate per-unit clarification ----------------------------------

def test_cc03_aggregate_per_unit_asks_for_the_WHOLE_payroll():
    copy = clarification.compute_clarification(
        "nssf", ["gross_monthly_payroll: low (period=daily needs days/weeks worked)"],
        BY_ID["cc_03"]["question"])
    assert "JUMLA ya mishahara ya wafanyakazi wote" in copy
    assert "idadi ya wafanyakazi" in copy


def test_cc04_single_worker_per_unit_keeps_the_original_wording():
    copy = clarification.compute_clarification(
        "nssf", ["gross_monthly_payroll: low (period=daily needs days/weeks worked)"],
        BY_ID["cc_04"]["question"])
    assert "JUMLA ya mishahara ya wafanyakazi wote" not in copy
    assert "siku/wiki ngapi kwa mwezi" in copy


def test_aggregate_copy_needs_the_question_to_opt_in():
    # No question text -> the original wording, exactly as before this change.
    copy = clarification.compute_clarification(
        "nssf", ["gross_monthly_payroll: low (period=daily needs days/weeks worked)"])
    assert "siku/wiki ngapi kwa mwezi" in copy


def test_cc06_a_computable_aggregate_question_is_still_computed():
    text = _answer(BY_ID["cc_06"]["question"]).text
    assert "245,000" in text                          # 3.5% of 7,000,000


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_every_probe_carries_a_guards_against_note(probe):
    assert probe["guards_against"].strip()
    assert probe["in_scope"] is True
