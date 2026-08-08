"""eval_368 — the employment-type pair is a group split only when BOTH sides are named.

`wa muda` / `wa kudumu` entered _GROUP_MARKERS in pattern B to catch a genuine two-group
split. As bare alternatives they also fired on ONE group described as part-time, which is
how the Phase D re-run (030a5ff) produced its single NEW regression: eval_368 says
"wafanyakazi 12 lakini WOTE ni WA MUDA", has_multiple_groups returned True, parse_count
returned None, and the applicability route asked for a headcount that was in the question.

This is the nat_07 class the founder told us to expect and to stop-and-flag: every veto
narrowed in PREREQ-2 can expose a defect that was previously unreachable.

Blast radius of the fix is exactly 3 corpus rows out of 561, all three wrong before it.
et_05 and et_06 are the must-not-break cases and are pinned individually below.
"""

import json
import pathlib

import pytest

from chike import swahili_numbers as swn
from chike.model_abstraction import ModelBackend
from chike.orchestrator import Orchestrator

PROBES_PATH = (pathlib.Path(__file__).resolve().parents[1]
               / "eval" / "accuracy_gate" / "employment_type_probes_008.jsonl")
PROBES = [json.loads(line) for line in PROBES_PATH.open(encoding="utf-8") if line.strip()]


class _Silent(ModelBackend):
    def generate(self, prompt, params=None):
        return ""


def _orch():
    return Orchestrator(_Silent(), retriever=lambda q: [], ooc_phrases=[], in_scope_phrases=[])


def test_probe_file_is_complete():
    assert len(PROBES) == 8
    assert all(p["in_scope"] and p["guards_against"].strip() for p in PROBES)


@pytest.mark.parametrize("probe", PROBES, ids=[p["id"] for p in PROBES])
def test_employment_type_probe(probe):
    q, guard = probe["question"], probe["guards_against"]
    if probe["expect"] == "multi_group":
        assert swn.has_multiple_groups(q) is True, guard
    elif probe["expect"] == "single_group":
        assert swn.has_multiple_groups(q) is False, guard
        assert swn.parse_count(q) == probe["expect_count"], guard
    else:                                                    # pragma: no cover
        raise AssertionError(f"unknown expectation {probe['expect']!r}")


# ── the must-not-break pair, pinned by name ────────────────────────────────────

@pytest.mark.parametrize("question", [
    "tuko na vibarua 8 wa kudumu na wawili wa muda kwenye gereji yangu je ile tozo ya "
    "mafunzo kwa wafanyakazi inatugusa",                     # edge_p04
    "nina vibarua 6 wa kudumu na watatu wa muda, je SDL inanihusu",   # ex_10
])
def test_a_genuine_split_names_both_sides_and_must_keep_firing(question):
    assert swn.has_multiple_groups(question) is True
    assert swn.parse_count(question) is None, "a partial headcount must never be the whole"


def test_the_other_group_markers_are_untouched():
    """The fix narrowed ONLY the employment-type pair. 'kati yao' still splits, even when a
    single employment-type word also appears — this is the eval_327 shape, where anchoring on
    the first group's TZS 700,000 gave WCF 3,500 instead of the real 23,000."""
    q = ("Nina wafanyakazi 10 wa muda, kati yao 4 wanapata TZS 700,000 na 6 wanapata "
         "TZS 300,000 — WCF ni ngapi?")
    assert swn.has_multiple_groups(q) is True
    assert swn.select_anchored_amount(q, swn.parse_amounts(q)) == (None, None)


def test_eval_368_answers_instead_of_asking_for_what_it_was_told():
    q = "Nina wafanyakazi 12 lakini wote ni wa muda (part-time), je bado nafikia kizingiti cha SDL?"
    reply = _orch().answer(q)
    assert not reply.needs_clarification
    assert "Ndiyo" in reply.text and "12" in reply.text
