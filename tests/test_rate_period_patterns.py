"""Patterns D and F1/F2, and the rate-question family — the last four known items.

  D    per-unit rate x per-MONTH quantity          eval_293, eval_296
  F1   per-levy payroll-label genitive             eval_323
  F2   headcount stated per NAMED MONTH            eval_329
  rate 'kiwango cha <levy> ni asilimia ngapi'      eval_305, eval_314

WHAT THE PROBES CAUGHT THAT THE SWEEP COULD NOT (R17). A clean corpus sweep is weak evidence
here because the corpus does not contain the dangerous shapes:
  * dv_01 — TWO rate groups. The naive D asserts 600,000 as the payroll for a TWELVE-person
    employer: gp_02's failure mode with a monthly quantity bolted on.
  * dv_06 — TWO quantities (3 shifts/day AND 26 days/month). The naive D returns 650,000 where
    the truth is 1,950,000.
  * fv_01 — eval_327. Anchoring each levy to its NEAREST amount gets eval_323 right and pins
    both WCF and SDL to 300,000 when the base is the 4,600,000 group payroll. This row answers
    correctly today and is pinned by name.
Hence: D declines on a second group, a second rate or a second quantity; F1 requires a resolved
group parse to be ABSENT and the amount to be a payroll-label genitive, never mere proximity.

TWO DEFECTS OF MY OWN, BOTH FOUND HERE RATHER THAN IN REVIEW:
  1. F2 was first nested INSIDE the crossing veto, so it could never fire on eval_329 — the one
     row it was written for. A multi-period question inherently HAS a crossing; the branch reads
     both counts rather than assuming one, so it belongs outside the veto.
  2. _CROSSING written as `(?:{_PEOPLE_NOUN}\\s+)?` binds loosely: only the LAST alternative
     carries the \\s+, so 'nikafikia WATU 12' silently stopped matching when the surface moved
     out of routing.py. ex_09 changing behaviour is what exposed it.

D'S HARD CONSTRAINT, tested directly rather than trusted to the required-fields contract:
what D returns is ONE PERSON'S monthly pay, never a payroll. dv_03/eval_294 is a single driver
on TZS 80,000 x 15 trips and must keep clarifying — its gold explicitly refuses
'SDL = 3.5% x 1,200,000'.
"""

import json
import pathlib
from decimal import Decimal

import pytest

from chike import routing, swahili_numbers as swn, rules_engine
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES_PATH = (pathlib.Path(__file__).resolve().parents[1]
               / "eval" / "accuracy_gate" / "rate_period_probes_016.jsonl")
PROBES = [json.loads(line) for line in PROBES_PATH.open(encoding="utf-8") if line.strip()]
BY_ID = {p["id"]: p for p in PROBES}


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def _answer(question):
    orch = Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[])
    return orch.answer(question)


def _q(pid):
    return BY_ID[pid]["question"]


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_every_probe_carries_a_guards_against_note(probe):
    assert probe["guards_against"].strip()
    assert probe["in_scope"] is True
    assert probe["pattern"] in {"D", "F1", "F2", "rate"}


# --- pattern D --------------------------------------------------------------

@pytest.mark.parametrize("pid,expected", [
    ("dv_01", None),          # two rate groups
    ("dv_05", None),          # no quantity
    ("dv_06", None),          # two quantities
    ("dv_07", None),          # bi-weekly, no monthly quantity
    ("dv_08", None),          # shifts per day, not per month
    ("dv_04", 468000),
])
def test_D_parser(pid, expected):
    got = swn.monthly_from_unit_rate(_q(pid))
    assert (None if got is None else int(got)) == expected


def test_D_never_returns_a_payroll_for_sdl_without_a_headcount():
    # eval_294 / dv_03. The gold refuses "SDL = 3.5% x 1,200,000" for a single driver.
    reply = _answer(_q("dv_03"))
    assert "1,200,000" not in reply.text
    assert "42,000" not in reply.text                 # 3.5% of 1.2M
    assert "Ili nihesabu SDL" in reply.text           # still a clarification


def test_D_per_person_times_headcount_for_a_real_payroll():
    # dv_02: 12 employees x 468,000 = 5,616,000 -> SDL 196,560.
    assert "196,560" in _answer(_q("dv_02")).text


def test_D_closes_eval_293_and_eval_296():
    assert "36,000" in _answer(
        "Fundi analipwa TZS 1,500 kwa kipande, anatengeneza vipande 400 kwa mwezi — PAYE yake?").text
    assert "46,800" in _answer(_q("dv_04")).text


def test_D_skips_the_period_divisor():
    # Without this the daily period would demand the days it was just given.
    assert "siku/wiki ngapi" not in _answer(_q("dv_04")).text


# --- pattern F1 -------------------------------------------------------------

def test_F1_claims_only_a_payroll_label_genitive():
    assert swn.levy_labelled_payroll(_q("fv_02")) == {"sdl": Decimal("7600000")}


@pytest.mark.parametrize("pid", ["fv_01", "fv_03", "fv_04"])
def test_F1_does_not_fire_on_the_must_not_break_rows(pid):
    assert swn.levy_labelled_payroll(_q(pid)) == {}


def test_F1_eval_327_still_uses_the_group_payroll():
    text = _answer(_q("fv_01")).text
    assert "161,000" in text and "23,000" in text     # 3.5% and 0.5% of 4,600,000
    assert "10,500" not in text                       # 3.5% of 300,000 — the unsafe answer


def test_F1_eval_323_computes_both_levies():
    text = _answer(_q("fv_02")).text
    assert "266,000" in text and "68,000" in text


def test_F1_eval_318_never_treats_turnover_as_a_payroll():
    text = _answer(_q("fv_04")).text
    assert "192,500" in text                          # 3.5% of 5,500,000
    assert "7,175,000" not in text                    # 3.5% of 205,000,000


# --- pattern F2 -------------------------------------------------------------

def test_F2_parses_a_headcount_per_named_month():
    assert swn.parse_month_headcounts(_q("fv_05")) == [("januari", 9), ("februari", 10)]
    assert swn.parse_month_headcounts(_q("fv_06")) == [("januari", 8), ("machi", 12)]


def test_F2_ignores_a_date_range():
    assert swn.parse_month_headcounts(_q("fv_07")) is None


def test_F2_answers_per_month_across_the_threshold():
    text = _answer(_q("fv_05")).text
    assert "Januari" in text and "TZS 0" in text
    assert "Februari" in text and "105,000" in text


def test_F2_is_reached_despite_the_crossing_veto():
    # The regression this pins: nested inside the veto, F2 could never fire on eval_329.
    assert routing.count_transition_ordinal(_q("fv_05")) == 10
    assert "Februari" in _answer(_q("fv_05")).text


def test_F2_when_nothing_crosses_the_threshold():
    text = _answer(_q("fv_08")).text
    assert text.count("245,000") >= 2                 # both months owe
    assert "490,000" in text                          # and the two-month total


def test_F2_declines_a_single_period():
    with pytest.raises(ValueError):
        rules_engine.sdl_by_month([("januari", 12)], Decimal("3000000"))


def test_crossing_headcount_matches_the_people_noun_form():
    # The precedence bug: 'nikafikia WATU 12' must match, not only 'nikafikia 12'.
    assert swn.crossing_headcount("Machi nikafikia watu 12") == 12
    assert swn.crossing_headcount("nikafikia 12") == 12
    assert swn.crossing_headcount("ninaajiri mfanyakazi wa 10") == 10


def test_routing_delegates_to_the_single_crossing_owner():
    assert routing._COUNT_TRANSITION is swn._CROSSING


# --- rate questions ---------------------------------------------------------

def test_rate_sdl_states_the_rate_and_applies_it_to_nothing():
    text = _answer(_q("rq_01")).text
    assert "asilimia 3.5" in text
    assert "16,800" not in text                       # 3.5% of 480,000 — the wrong answer
    assert "10 au zaidi" in text


def test_rate_nssf_states_the_rate_and_the_figure():
    text = _answer(_q("rq_02")).text
    assert "asilimia 20" in text and "190,000" in text


@pytest.mark.parametrize("pid", ["rq_03", "rq_04"])
def test_rate_branch_needs_a_figure_to_engage(pid):
    # eval_111 / eval_112 stay on the fact path, which is where their richer golds live.
    assert swn.sole_plausible_amount(_q(pid)) is None


def test_a_plain_amount_question_is_not_a_rate_question():
    assert routing.asks_rate(_q("rq_05")) is False
    assert "245,000" in _answer(_q("rq_05")).text


def test_paye_has_no_flat_rate_statement():
    assert rules_engine.rate_statement_supports("paye") is False
    with pytest.raises(ValueError):
        rules_engine.levy_rate_statement("paye", Decimal("800000"))
