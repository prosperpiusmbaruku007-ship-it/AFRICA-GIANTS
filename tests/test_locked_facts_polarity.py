# -*- coding: utf-8 -*-
"""THE FACT-GUARDIAN'S POLARITY NARROWINGS, PINNED BOTH DIRECTIONS (2026-10-08).

WHY THIS FILE EXISTS, AND IT IS THE BIGGER HALF OF THE FINDING. `check_locked_facts.py`
flagged five rows whose purpose is to DENY the wrong value -- four of which had already
been QUARANTINED on that basis, and one (`b008_paye_adv_001`) was LIVE AT HEAD still
carrying the false positive. But the defect in the matcher is not the interesting part.

⛔ THE GATE WAS NEVER MECHANICALLY RUN. Measured 2026-10-08:
  * `.githooks/` contains ONLY `pre-push`. There is NO pre-commit hook at all.
  * `pre-push` runs `scan_for_keys.py` and `pytest` -- not this gate.
  * `validate_dataset.py` IS enforced, because tests/test_validate_dataset_gate.py asserts
    THE REAL CORPUS PASSES IT, and pre-push runs pytest. Its corpus is clean: 1714/0.
  * `check_locked_facts.py` is imported by two tests, and NEITHER runs it over the corpus.
    48 flag lines were live at HEAD across three committed files.
  * `check_sources.py` and `check_eval_split.py` have ZERO test references.

  The skill says "Do NOT save if exit code 1" and "Only commit if all 4 return 0". Those
  are instructions to a reader, enforced by nothing. THE DIFFERENCE BETWEEN THE CLEAN GATE
  AND THE DIRTY ONE IS WIRING, NOT DILIGENCE -- R26's shape, arriving from the direction of
  a gate that always fires rather than one that never does. A gate nobody runs before
  saving is a gate in name only, and a gate that fails continuously stops carrying
  information, so people route around it and are right to.

WHAT THIS FILE DOES ABOUT IT:
  1. pins the narrowings in BOTH directions against committed probes (R17 step 3), so a
     future widening cannot silently restore the false positives and a future narrowing
     cannot silently delete the true positives;
  2. RATCHETS the real corpus. Not "the corpus passes" -- it does not, and asserting that
     would be a test that instructs maintainers to ignore real defects (R17's corollary).
     A shrink-only ceiling makes the number visible and makes any INCREASE fail, which is
     the enforcement that was missing entirely.
"""
import importlib.util
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
PROBES = os.path.join(REPO, "eval", "fidelity", "locked_facts_polarity_probes.jsonl")


def _gate():
    spec = importlib.util.spec_from_file_location(
        "check_locked_facts", os.path.join(REPO, "scripts", "check_locked_facts.py"))
    mod = importlib.util.module_from_spec(spec)
    sys.modules["check_locked_facts"] = mod
    cwd = os.getcwd()
    try:
        os.chdir(REPO)
        spec.loader.exec_module(mod)
    finally:
        os.chdir(cwd)
    return mod


GATE = _gate()
FACTS = GATE.load_locked_facts(os.path.join(REPO, "scripts", "locked_facts.json"))


def _rows():
    out = []
    with open(PROBES, encoding="utf-8") as fh:
        for line in fh:
            if line.strip():
                out.append(json.loads(line))
    return out


ROWS = _rows()


def test_the_probe_set_covers_both_directions():
    """R17/R26: positive-only certifies a rule that flags everything; negative-only is what
    the secret scan had. Four of these probes are rows that must come back CLEAN and they
    are the half that does the work -- every one is a real row this gate actually flagged."""
    must_flag = [r for r in ROWS if r["must_flag"]]
    must_not = [r for r in ROWS if not r["must_flag"]]
    assert len(must_flag) >= 3, "no true positives: a narrowing could gut the gate unnoticed"
    assert len(must_not) >= 3, "no clean cases: the gate could flag everything and pass"
    for r in ROWS:
        assert len(r.get("guards_against", "")) > 80, (
            f"{r['id']} has no stated reason. A probe without one decays into a magic "
            f"string nobody dares touch.")


@pytest.mark.parametrize("row", ROWS, ids=[r["id"] for r in ROWS])
def test_each_probe_behaves_as_specified(row):
    flags, demoted = GATE.check_pair(row, FACTS, include_demoted=True)
    keys = {f["fact_key"] for f in flags}
    if row["must_flag"]:
        assert row["fact_key"] in keys, (
            f"{row['id']} MUST flag on {row['fact_key']} and did not. A narrowing has "
            f"deleted a true positive -- the dangerous direction, because a shorter finding "
            f"list reads as progress.\n  guards_against: {row['guards_against']}\n"
            f"  demoted instead: {[d.get('demoted') for d in demoted]}")
    else:
        assert row["fact_key"] not in keys, (
            f"{row['id']} must NOT flag on {row['fact_key']} but did.\n"
            f"  guards_against: {row['guards_against']}")


def test_both_narrowings_are_still_present_and_bounded():
    """Either narrowing alone is insufficient: b008_paye_adv_002 needs the span cap (604
    characters) AND rows like it need the backward negation window. And the bounds are the
    safety: an unbounded window, or a negation alternative without word boundaries, is how
    a demotion rule starts deleting findings -- a bare `si` matches inside `kiasi`."""
    assert GATE.MAX_MATCH_SPAN <= 200, "the span cap has been widened past usefulness"
    assert GATE.NEGATION_WINDOW <= 60, "the negation window has been widened"
    for alt in ("si", "no", "not", "wrong"):
        assert rf"\b{alt}\b" in GATE.NEGATION, (
            f"the {alt!r} negation alternative lost its word boundaries")


def test_demoted_matches_are_recorded_rather_than_dropped():
    """A demotion that leaves no trace is indistinguishable from the pattern not matching,
    which is how an over-narrowed rule hides. b008_paye_adv_002 must appear in `demoted`
    with a reason, not simply be absent."""
    row = next(r for r in ROWS if r["id"] == "lfp_02")
    flags, demoted = GATE.check_pair(row, FACTS, include_demoted=True)
    assert demoted, "the known false positive was dropped silently, not demoted with a reason"
    assert any("span_too_wide" in d["demoted"] or "mention_under_negation" in d["demoted"]
               for d in demoted), [d.get("demoted") for d in demoted]


# ── THE RATCHET ───────────────────────────────────────────────────────────────────
# Measured 2026-10-08 AFTER the narrowings and the \brent\b fix. These are flagged PAIRS
# per file, the number the gate prints. They are NOT zero and this test does not pretend
# they are: the survivors are OSHA/WCF threshold-conflation candidates that need
# adjudicating on their own merits, which is corpus work and a separate decision.
#
# ⛔ SHRINK-ONLY. An increase fails. That is the enforcement this gate has never had, and
# it is deliberately a ceiling rather than an equality: equality would fail on every
# legitimate fix and train people to bump the number, which is how an expiry date decays
# (R35). Lower it when the corpus improves.
#   batch_004: 19 at HEAD -> 6     batch_006: 10 -> 2     batch_008: 4 -> 0
# The 6 and 2 that remain are OSHA/WCF threshold-conflation candidates (e.g.
# tier1a_osha_001 gives OSHA registration a 10-employee floor, which is SDL's threshold,
# not OSHA's). Those are real and are left for adjudication on their own merits; they are
# NOT false positives and must not be narrowed away.
RATCHET = {
    "datasets/tier1a/cleaned_pairs/batch_004_cleaned.jsonl": 6,
    "datasets/tier1a/cleaned_pairs/batch_006_cleaned.jsonl": 2,
    "datasets/tier1a/cleaned_pairs/batch_008_cleaned.jsonl": 0,
}


@pytest.mark.parametrize("rel,ceiling", sorted(RATCHET.items()))
def test_the_real_corpus_does_not_get_worse(rel, ceiling):
    path = os.path.join(REPO, *rel.split("/"))
    flagged = 0
    with open(path, encoding="utf-8") as fh:
        for line in fh:
            if not line.strip():
                continue
            if GATE.check_pair(json.loads(line), FACTS):
                flagged += 1
    assert flagged <= ceiling, (
        f"{rel}: {flagged} pairs now flag against a ceiling of {ceiling}. A new locked-fact "
        f"violation entered the corpus. This gate is NOT run by any hook -- `.githooks/` "
        f"holds only pre-push, and pre-push runs scan_for_keys and pytest -- so this test is "
        f"the only thing standing between a defect and a commit.")
    if flagged < ceiling:
        pytest.fail(
            f"{rel}: {flagged} < ceiling {ceiling}. Good news, and the ratchet must move: "
            f"lower RATCHET[{rel!r}] to {flagged} so the gain is locked in. A ceiling left "
            f"above the real number is slack that the next regression hides inside.")
