# -*- coding: utf-8 -*-
"""SAFETY-2 / D-RESIDENCY-1 — the engine must not compute a PAYE figure it cannot justify.

THE DEFECT (tracked 2026-08-06, `nat_16`). *"nimemleta engineer kutoka india hana residence
permit ya kudumu nampa milioni 4 kwa mwezi"* returned **TZS 1,028,000** — the resident
progressive bands — rendered as the authoritative deterministic *working*. D-FIDELITY-1
cannot catch it: body and working agreed, because both derived from the same mis-resolved
input. The defect is upstream of every fidelity guard.

WHY THE PROPOSED FIX WAS NOT BUILT. The 2026-08-06 entry proposed extending
`_PAYE_NONRESIDENT_CUES` with permit and foreignness phrasings. Three measurements killed it,
and the entry's own warning — *"do not close this by fixing the cue list"* — turned out to be
literally correct:

  1. CITIZENSHIP IS NOT RESIDENCY. Tanzanian tax residency is decided by PRESENCE, not
     nationality or permit class. `si raia wa tanzania` / `mfanyakazi wa kigeni` / `mgeni` /
     `expatriate` are not evidence of non-residency; they are a category error.
  2. WE DO NOT OWN THE TEST. locked_facts.json has the non-resident RATE and no definition of
     who is one. Zero corpus occurrences of the 183-day test.
  3. THE TRADE IS 3-FOR-1 AGAINST. Of 144 PAYE-routing corpus rows, 8 mention foreignness:
     three already resolve correctly, one is the deferred mixed case, one is nat_16 — and
     THREE would be broken by the proposed cues (rs_08, rs_10, rs_11).

AND THE COST IS ASYMMETRIC THE WRONG WAY. A false non-resident detection at TZS 300,000
charges 45,000 instead of 2,400 — **18.75x**. The bug it would fix overcharges one high
earner by 1.7x. The obvious fix is worse than the defect at the salaries our users have.

SO THE FIX DECLINES. It detects *ambiguity* and asks, naming the day-count test so the user
can answer in one message. It does not state either figure — offering both would hand over
two numbers with our authority attached and invite the user to pick the smaller.

⚠️ THE PROBES ARE AUTHORED, AND THAT IS FORCED, NOT PREFERRED. `wakazi` (26 train / 0 eval),
`resident` (8/0), `uraia` (9/0): the eval corpus cannot pose a question whose answer depends
on residency. **There is no sweep to run here, and a clean one would prove nothing.** This is
R17 arriving from the opposite direction — the corpus statistics told us the instrument was
blind BEFORE the work, rather than 15 adversarial probes telling us after.
"""
import json
import os

import pytest

from chike import clarification, routing

_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_PROBES = os.path.join(_ROOT, "eval", "accuracy_gate", "residency_unclear_probes_014.jsonl")


def _probes():
    with open(_PROBES, encoding="utf-8") as fh:
        return [json.loads(line) for line in fh if line.strip()]


def test_the_probe_file_is_present_and_carries_both_polarities():
    probes = _probes()
    assert len(probes) == 14, len(probes)
    assert sum(1 for p in probes if p["expected_unclear"]) == 4
    assert sum(1 for p in probes if not p["expected_unclear"]) == 10, (
        "the negatives outnumber the positives 10:4 on purpose — the measured danger here "
        "is over-triggering, not under-triggering")
    for p in probes:
        assert p["guards_against"], p["id"]


@pytest.mark.parametrize("probe", _probes(), ids=lambda p: p["id"])
def test_residency_ambiguity_is_detected_exactly(probe):
    got = routing.paye_residency_unclear(probe["question"])
    assert got is probe["expected_unclear"], (
        f"{probe['id']}: expected unclear={probe['expected_unclear']}, got {got}\n"
        f"  Q: {probe['question']}\n  guards: {probe['guards_against']}")


def test_an_explicit_residency_statement_suppresses_the_question():
    """Both directions. If the user already said it, asking again is a worse answer than
    computing — this is the difference between a clarification and a nag."""
    assert not routing.paye_residency_unclear(
        "mfanyakazi asiye mkazi hana residence permit analipwa TZS 900,000 PAYE ni ngapi")
    assert not routing.paye_residency_unclear(
        "mfanyakazi wangu hana residence permit lakini ni mkazi analipwa TZS 900,000")


def test_citizenship_language_never_triggers_it():
    """The category error, pinned. Nationality is not residency under the Income Tax Act, and
    7 corpus rows use `si raia wa Tanzania` on GN 487A business-licensing questions."""
    for q in ("mimi si raia wa Tanzania nina kampuni ya usafi je GN 487A inanihusu",
              "mfanyakazi wa kigeni analipwa TZS 900,000 PAYE ni kiasi gani",
              "mfanyakazi mgeni (expatriate) analipwa milioni 2 PAYE ni ngapi"):
        assert not routing.paye_residency_unclear(q), q


def test_bare_kibali_is_not_a_permit_signal():
    """`kibali` means BRACKET in a PAYE question and PERMIT in an immigration one. The single
    clearest argument in this codebase for context-qualified cues over bare words."""
    assert not routing.paye_residency_unclear(
        "Mshahara wa mfanyakazi wangu unapoingia kwenye kibali kikubwa cha PAYE, hapo juu "
        "ya 1,000,000, ninalipa kiasi gani")
    assert routing.paye_residency_unclear(
        "mfanyakazi wangu hana kibali cha ukaazi analipwa TZS 900,000 PAYE ni ngapi")


def test_the_copy_names_the_day_test_and_states_no_figure():
    """It must be answerable in one message, and it must not hand over both numbers.

    Naming the 183-day test is what stops the reply "he's Indian" — the exact confusion that
    produced this defect. Stating either figure would be the fabrication risk wearing a
    clarification costume."""
    copy = clarification.PAYE_RESIDENCY_UNCLEAR
    assert "183" in copy
    assert "uraia" in copy                      # explicitly says nationality does not decide
    assert "1,028,000" not in copy and "600,000" not in copy
    assert "tra.go.tz" in copy


def test_the_guard_does_not_fire_across_the_real_gate_corpus():
    """Blast radius, pinned. The clarification must be silent on every gate row — nat_16
    lives in a probe file, not the 400."""
    import glob
    runs = sorted(glob.glob(os.path.join(_ROOT, "eval", "results",
                                         "gate_orchestrator_combined_*.json")),
                  key=os.path.getmtime)
    rows = json.load(open(runs[-1], encoding="utf-8"))["results"]
    fired = [r["id"] for r in rows
             if routing.paye_residency_unclear(r.get("question_sw", ""))]
    assert fired == [], f"residency clarification fires on real gate rows: {fired}"
