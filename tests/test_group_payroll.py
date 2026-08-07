"""PREREQ-2 pattern B — multi-group payroll, and the eval_399 individual shape.

WHY THIS PARSER IS ALL-OR-NOTHING. A prototype of the obvious structural template
("<count> <pay-verb> <amount>") was swept over 524 questions: it matched 12 and MIS-PARSED
SIX, two of them catastrophically — eval_304 became a TZS 1 BILLION payroll (mtaji is
capital), nat_18 became 2 x 400,000 instead of 400,000 + 1,100,000, and eval_285/287/288/289
took the fraction BASE (24, 30, 16, 14) as the group count. Every one of those replaces an
honest clarification with a confident wrong number, which is the failure never-guess exists
to prevent. Four validations must all pass or the parser declines.

Magnitude cannot be the count-vs-salary discriminator: MIN_PLAUSIBLE_AMOUNT is 10,000, but
real rates here are 1,500/piece and 18,000/day. Roles are assigned STRUCTURALLY.
"""

import json
import pathlib
from decimal import Decimal

import pytest

from chike import rules_engine, routing, swahili_numbers as swn
from chike.extraction import REQUIRED_FIELDS, SlotExtractor
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES_PATH = (pathlib.Path(__file__).resolve().parents[1]
               / "eval" / "accuracy_gate" / "group_payroll_probes_008.jsonl")
PROBES = [json.loads(line) for line in PROBES_PATH.open(encoding="utf-8") if line.strip()]


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def _orch():
    return Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[])


def test_probe_file_is_complete():
    assert len(PROBES) == 9
    assert all(p["in_scope"] and p["guards_against"].strip() for p in PROBES)


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_group_probe(probe):
    result = swn.parse_payroll_groups(probe["question"])
    guard = probe["guards_against"]
    if probe["expect"] == "decline":
        assert result is None or result.get("groups") is None, guard
    elif probe["expect"] == "not-a-group":
        assert result is None or result.get("groups") is None, guard
        assert swn.parse_individual_salaries(probe["question"]), guard
    elif probe["expect"] == "group":
        assert result and result.get("groups"), guard
        assert result["payroll"] == Decimal(probe["expect_payroll"]), guard
    else:                                                    # pragma: no cover
        raise AssertionError(f"unknown expectation {probe['expect']!r}")


# ── the nine instances, end to end ──────────────────────────────────────────────

_NINE = [
    ("Robo ya wafanyakazi 24 wanapata TZS 800,000, wengine wote TZS 350,000 — SDL ya jumla?",
     "TZS 388,500"),
    ("Watu 5 wanapata 700,000, watu 4 wanapata 550,000, watu 6 wanapata 300,000 — "
     "NSSF ya jumla ni ngapi?", "TZS 1,500,000"),
    ("Theluthi mbili ya watu 30 wanalipwa TZS 500,000, wengine wanalipwa TZS 900,000 — SDL?",
     "TZS 665,000"),
    ("Robo tatu ya wafanyakazi 16 wanapata TZS 450,000, robo wanapata TZS 1,000,000 — "
     "WCF ya jumla?", "TZS 47,000"),
    ("Nusu ya wafanyakazi 14 wanapata TZS 620,000, nusu wanapata TZS 380,000 — "
     "sehemu ya mwajiri ya NSSF?", "TZS 700,000"),
    ("Watu 3 wa kwanza wanapata TZS 1,200,000, wanne wanaofuata TZS 800,000, watano wa "
     "mwisho TZS 500,000 — SDL?", "TZS 325,500"),
    ("Swali refu: tuna tawi la Arusha lenye watu 6 wa TZS 400,000 na tawi la Mwanza lenye "
     "watu 9 wa TZS 500,000, jumla ya NSSF ya makampuni yote ni ngapi?", "TZS 1,380,000"),
    ("Nina wafanyakazi 10, kati yao 4 wana mishahara ya TZS 700,000 na 6 wana TZS 300,000, "
     "nataka WCF na SDL — zote mbili.", "TZS 23,000"),
    ("Watu wawili: mmoja anapata TZS 400,000 na mwingine TZS 1,200,000 — "
     "PAYE ya kila mmoja ni ngapi?", "TZS 188,000"),
]


@pytest.mark.parametrize("question,expected", _NINE)
def test_the_nine_instances_answer_with_the_gold_figure(question, expected):
    reply = _orch().answer(question)
    assert not reply.needs_clarification
    assert expected in reply.text


# ── eval_399: an output SHAPE, decided separately from the group parse ──────────

def test_paye_individuals_are_never_summed_into_one_payroll():
    """PAYE bands are progressive, so summing is not a presentation choice but an arithmetic
    error: one salary of 1,600,000 gives TZS 308,000; the true answer is 10,400 + 188,000."""
    each = rules_engine.compute_paye_each([Decimal("400000"), Decimal("1200000")])
    assert each.amount == Decimal("198400")
    assert rules_engine.compute_paye(Decimal("1600000")).amount == Decimal("308000")
    assert "TZS 10,400" in each.working and "TZS 188,000" in each.working


def test_individual_shape_does_not_capture_a_group_question():
    assert swn.parse_individual_salaries(
        "Watu 5 wanapata 700,000, watu 4 wanapata 550,000") is None
    # eval_326 (mixed residency) stays on its deferred D-PAYE-1 path.
    assert swn.parse_individual_salaries(
        "Mfanyakazi ni mkazi analipwa TZS 1,100,000 na mwenzake si mkazi analipwa "
        "TZS 1,100,000") is None


# ── eval_289: party resolution must reach the GROUP path ───────────────────────

def test_group_path_passes_nssf_party_through():
    """eval_289 asks the EMPLOYER share of a group total. routing.nssf_party already resolves
    'sehemu ya mwajiri'; this pins that the group path applies it, as the single-figure path
    does — 10% of 7,000,000, not the 20% default."""
    q = ("Nusu ya wafanyakazi 14 wanapata TZS 620,000, nusu wanapata TZS 380,000 — "
         "sehemu ya mwajiri ya NSSF?")
    assert routing.nssf_party(q) == "employer"
    assert "TZS 700,000" in _orch().answer(q).text


# ── the gate: never divert a question that already computes ────────────────────

@pytest.mark.parametrize("question", [
    "Wafanyakazi 5 kila mmoja anapata TZS 400,000 kwa mwezi — mwajiri anachangia kiasi gani "
    "NSSF kwa mwezi?",                                        # eval_092, computes today
    "Tuna wafanyakazi 15 wenye mshahara wa TZS 600,000 kila mmoja, je tunahitaji kusajili "
    "VAT?",                                                   # eval_302, fact-routed
])
def test_questions_that_already_work_are_untouched(question):
    assert swn.parse_payroll_groups(question) is None


def test_group_parse_runs_only_after_extraction_fails():
    """The gate is positional: parse_payroll_groups is consulted inside the
    `not extraction.usable(...)` branch, so a computable question can never reach it."""
    source = pathlib.Path(Orchestrator.__module__.replace(".", "/") + ".py").read_text(
        encoding="utf-8")
    gate = source.index("if not extraction.usable(required):")
    assert source.index("parse_payroll_groups") > gate
    assert source.index("parse_individual_salaries") > gate


# ── the four validations ───────────────────────────────────────────────────────

def test_validation_every_money_figure_must_be_assigned():
    r = swn.parse_payroll_groups(
        "watu 5 wanapata TZS 700,000 na watu 4 wanapata TZS 550,000 na TZS 900,000 nyingine")
    assert r is None or r.get("groups") is None


def test_validation_stated_total_must_match_the_groups():
    r = swn.parse_payroll_groups(
        "Nina wafanyakazi 10, kati yao 4 wana mishahara TZS 700,000 na 7 wana TZS 300,000")
    assert r["groups"] is None and "sum to 11" in r["reason"]


def test_validation_fraction_counts_come_from_c2_not_the_adjacent_number():
    r = swn.parse_payroll_groups(
        "Robo ya wafanyakazi 24 wanapata TZS 800,000, wengine wote TZS 350,000")
    assert r["groups"][0][0] == 6, "the group is 6, not the fraction base 24"


def test_validation_wrong_base_disqualifies_the_whole_parse():
    assert swn.parse_payroll_groups(
        "Nina wafanyakazi 20 na mtaji wa TZS 50,000,000 na wafanyakazi 5 wa TZS 300,000"
    ) in (None, {"groups": None, "reason": "non-payroll figure present (wrong base)"})
