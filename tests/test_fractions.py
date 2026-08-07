"""PREREQ-2 pattern C — fraction grammar: suppress the quantifier, resolve the split.

Swahili has TWO fraction constructions and _value_small implemented only one:
    additive        "<scale> <n> NA <frac>"    laki saba na nusu    = 750,000   (correct)
    multiplicative  "<frac> [<num>] YA <N>"    theluthi mbili ya 30 = 20        (was 2.333)
The numerator is a MULTIPLIER, not an addend. C-1 suppresses the quantifier (resolving it
needs the group it modifies — pattern B); C-2 exposes the resolved split for B to consume.

Probes: eval/accuracy_gate/extraction_fraction_probes_008.jsonl. The corpus contains ZERO
money-fraction cases ("nusu ya mshahara"), so probes are the only instrument covering the
over-breadth direction here.
"""

import json
import pathlib
from decimal import Decimal

import pytest

from chike import swahili_numbers as swn

PROBES_PATH = (pathlib.Path(__file__).resolve().parents[1]
               / "eval" / "accuracy_gate" / "extraction_fraction_probes_008.jsonl")
PROBES = [json.loads(line) for line in PROBES_PATH.open(encoding="utf-8") if line.strip()]


def test_probe_file_is_complete():
    assert len(PROBES) == 8
    assert all(p["in_scope"] and p["guards_against"].strip() for p in PROBES)


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_fraction_probe(probe):
    q, expect, guard = probe["question"], probe["expect"], probe["guards_against"]
    amounts = swn.parse_amounts(q)
    resolved = swn.parse_fraction_of_count(q)

    if expect.startswith("amount:"):
        wanted = Decimal(expect.split(":", 1)[1])
        assert wanted in amounts, f"{guard}\n  parsed: {[str(a) for a in amounts]}"
    elif expect == "no-fraction-count":
        assert resolved is None, guard
    elif expect == "fraction-declines":
        assert resolved is not None and resolved["groups"] is None, guard
    elif expect == "period-not-quantity":
        assert resolved is None, guard
        assert swn.detect_period(q)[1] == "quarter", guard
    elif expect == "no-junk":
        assert not any(a != a.to_integral_value() for a in amounts), \
            f"{guard}\n  parsed: {[str(a) for a in amounts]}"
    else:                                                  # pragma: no cover
        raise AssertionError(f"unknown expectation {expect!r}")


# ── the must-not-break case, pinned explicitly ──────────────────────────────────

def test_eval_274_additive_fraction_is_live_and_must_keep_computing():
    """eval_274 COMPUTES today on 'laki saba na nusu' = 750,000. It is the only live
    fraction-bearing compute question in the corpus; C must not touch it."""
    q = "Mfanyakazi analipwa laki saba na nusu tu, NSSF anayokatwa ni ngapi?"
    assert swn.parse_amounts(q) == [Decimal("750000")]


def test_the_nat_05_near_miss_a_regex_rule_would_have_broken():
    """A '\\b(nusu|robo|theluthi)\\s+ya' regex matches 'nusu ya' here and suppresses the 3.5 —
    but the RUN starts at 'tatu', so the construction is additive. Run-initial is the only
    formulation that separates the two."""
    q = ("nimenunua mashine za kiwanda za milioni 50 na nina wafanyakazi 12 hiyo ya mafunzo "
         "nitalipa asilimia tatu na nusu ya nini")
    assert Decimal("3.5") in swn.parse_amounts(q)


# ── C-1: the quantifier emits nothing ───────────────────────────────────────────

@pytest.mark.parametrize("text", [
    "theluthi mbili ya watu 30",
    "robo tatu ya wafanyakazi 16",
    "theluthi mbili wanapata laki tano",      # elliptical, no 'ya' — the general form
    "nusu milioni kwa mwezi",                 # fraction-initial money run
])
def test_fraction_initial_runs_emit_no_junk(text):
    """The junk signature is a NON-INTEGER (1/3 + 2 = 2.333, 1/4 + 3 = 3.25, 0.5) — not
    merely a small value: the base headcount ('watu 30' -> 30) is small and legitimate."""
    assert not [a for a in swn.parse_amounts(text) if a != a.to_integral_value()]


def test_no_fraction_initial_run_ever_yielded_a_correct_figure():
    """The evidence for the GENERAL form over the 'ya'-gated one: _value produces junk for
    every fraction-initial run, so suppressing them all loses nothing."""
    for run in (["nusu", "milioni"], ["robo", "milioni"], ["nusu", "laki"],
                ["robo", "tatu"], ["theluthi", "mbili"]):
        assert swn._value(run) < swn.MIN_PLAUSIBLE_AMOUNT


# ── C-2: the resolved split ─────────────────────────────────────────────────────

@pytest.mark.parametrize("text,base,groups", [
    ("Robo ya wafanyakazi 24 wanapata TZS 800,000, wengine wote TZS 350,000", 24, [6, 18]),
    ("Theluthi mbili ya watu 30 wanalipwa TZS 500,000, wengine wanalipwa TZS 900,000",
     30, [20, 10]),
    ("Robo tatu ya wafanyakazi 16 wanapata TZS 450,000, robo wanapata TZS 1,000,000",
     16, [12, 4]),
    ("Nusu ya wafanyakazi 14 wanapata TZS 620,000, nusu wanapata TZS 380,000", 14, [7, 7]),
])
def test_fraction_of_count_matches_the_gold_split(text, base, groups):
    assert swn.parse_fraction_of_count(text) == {"base": base, "groups": groups}


def test_numerator_multiplies_it_does_not_add():
    """'theluthi mbili' is TWO THIRDS (2/3), not 1/3 + 2. That addition is the original bug."""
    assert swn.parse_fraction_of_count("theluthi mbili ya watu 30")["groups"] == [20]
    assert swn.parse_fraction_of_count("robo tatu ya watu 16")["groups"] == [12]


def test_never_rounds_a_person():
    r = swn.parse_fraction_of_count("theluthi ya watu 10 wanapata laki tano")
    assert r["groups"] is None and "whole number" in r["reason"]


def test_requires_a_people_noun():
    assert swn.parse_fraction_of_count("nusu ya mshahara wake") is None
    assert swn.parse_fraction_of_count("robo tatu ya faida ya biashara") is None
    assert swn.parse_fraction_of_count("robo ya milioni 20") is None


def test_c2_is_unused_by_default():
    """C closes zero gate questions: all four instances still clarify, because their blocker
    is the multi-figure rule that pattern B owns. Nothing in the pipeline calls this yet."""
    import chike.extraction as extraction
    import chike.orchestrator as orchestrator
    for module in (extraction, orchestrator):
        source = pathlib.Path(module.__file__).read_text(encoding="utf-8")
        assert "parse_fraction_of_count" not in source
