# -*- coding: utf-8 -*-
"""GUARD A — the answer contradicts a headcount the user stated in the same sentence.

THE LIVE CASE (2026-08-14). A user wrote *"Nina wafanyakazi 14 … nalipa shingapi"* and was
told *"bado una wafanyakazi chini ya 10, hivyo hakuna ulazima wa kulipa SDL"*. The rules
engine would have said TZS 210,000. It was never invoked — a `shingapi` routing miss — so
the fact path free-generated a claim contradicting a number in the same sentence.

⚠️ WHY THIS GUARD IS POSSIBLE AND ITS SIBLING IS NOT. Guard B was specified alongside it:
catch a fabricated AMOUNT by asking whether it is derivable from the user's figures. It is
impossible, and that was measured rather than argued — a fabricated figure and a legitimate
transformation are both just arithmetic relationships to the user's number. TZS 400,000 is
exactly half of the stated TZS 800,000, and halving is what correct per-person answers do;
enable the division allowance correctness requires and the true positive disappears.

This guard needs no derivation allowance at all, because it checks a COMPARISON, not a
quantity:

    A STATED 14 IS NOT "FEWER THAN 10" UNDER ANY TRANSFORMATION.

⚠️ DO NOT WIDEN THIS BACK TO "any headcount in the body differs from the stated one." That
version was written first and measured: **10 flags on 400 real rows, NINE false positives**,
every one a CORRECT answer citing the SDL threshold beside the user's count. `hc_05` and
`hc_09` are those shapes, kept as probes so the widened rule cannot come back quietly.

Evidence base, stated honestly: the precondition occurs in only **8 of 400** real rows and
the one true positive came from a live user message, not the corpus. That is why this file
holds AUTHORED probes — a sweep over 8 opportunities is not evidence (R17).
"""
import json
import os

import pytest

from chike import clarification, fidelity

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROBES = os.path.join(_ROOT, "eval", "accuracy_gate",
                       "headcount_contradiction_probes_010.jsonl")


def _probes():
    with open(_PROBES, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_the_probe_file_is_present_and_carries_both_polarities():
    probes = _probes()
    assert len(probes) == 10, len(probes)
    assert sum(p["expected_flag"] for p in probes) == 4
    assert sum(not p["expected_flag"] for p in probes) == 6, (
        "the negatives are the point — a guard with only positives cannot fail usefully")
    for p in probes:
        assert p["guards_against"], p["id"]


@pytest.mark.parametrize("probe", _probes(), ids=lambda p: p["id"])
def test_guard_a_decides_each_probe_correctly(probe):
    got = fidelity.body_contradicts_stated_headcount(probe["body"], probe["question"])
    assert got is probe["expected_flag"], (
        f"{probe['id']}: expected flag={probe['expected_flag']}, got {got}\n"
        f"  Q: {probe['question']}\n  A: {probe['body']}\n  guard: {probe['guards_against']}")


def test_stated_headcount_reads_the_largest_stated_count():
    assert fidelity.stated_headcount("Nina wafanyakazi 14 na mishahara milioni 6") == 14
    assert fidelity.stated_headcount("SDL ni asilimia ngapi") is None


def test_a_bare_threshold_statement_is_not_a_claim_about_the_user():
    """The subject-marker requirement, isolated. Removing it is how the 9 false positives
    came back the first time."""
    q = "Nina wafanyakazi 14 nalipa SDL kiasi gani"
    assert not fidelity.body_contradicts_stated_headcount(
        "kizingiti ni wafanyakazi chini ya 10 hawalipi", q)
    assert fidelity.body_contradicts_stated_headcount(
        "una wafanyakazi chini ya 10", q)


def test_the_clarification_quotes_the_users_own_count_back():
    """It must not read as though we ignored a number written in the same sentence."""
    copy = clarification.headcount_contradiction(14)
    assert "14" in copy
    assert "Samahani" in copy


def test_the_guard_does_not_fire_across_the_real_gate_corpus():
    """Blast radius, pinned. 0 flags over the newest 400-row orchestrator run."""
    import glob
    runs = sorted(glob.glob(os.path.join(_ROOT, "eval", "results",
                                         "gate_orchestrator_combined_*.json")),
                  key=os.path.getmtime)
    rows = json.load(open(runs[-1], encoding="utf-8"))["results"]
    flagged = [r["id"] for r in rows
               if r.get("generated")
               and fidelity.body_contradicts_stated_headcount(
                   r["generated"], r.get("question_sw", ""))]
    assert flagged == [], f"guard fires on real gate rows: {flagged}"
