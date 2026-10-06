# -*- coding: utf-8 -*-
"""THE ANCHOR-PROVENANCE CHECK MUST BLOCK ALL THREE HISTORICAL STALE ANCHORS -- and pass the
corrected ones.

R26 both directions. A check for a defect class that has already occurred three times has an
unusual advantage: the three specimens are KNOWN, so "does it fire?" can be answered against
the actual history rather than against invented examples. Each is planted verbatim below.

  2026-10-05  act_section_12.wrong_patterns      rejected the CORRECT "Part XII" citation
  2026-10-05  check_facts_index_sync.PINNED      required 'ifikapo tarehe 10'
  2026-10-06  regenerate_rag_e5 critical_queries required 'milioni kumi na moja' (the
                                                 fabricated 11M EFD threshold)

⚠️ THE THIRD ONE IS THE REASON THE SWAHILI WORD-FORM LIMB EXISTS, and a digits-only check would
report clean on it. Its fact's wrong_pattern holds `(11|14),?000,?000` in DIGITS while the
anchor said 'milioni kumi na moja' in WORDS. If that limb is ever removed, this test is what
fails.
"""
import importlib.util
import json
import os
import sys

import pytest

REPO = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_spec = importlib.util.spec_from_file_location(
    "check_anchor_provenance", os.path.join(REPO, "scripts", "check_anchor_provenance.py"))
cap = importlib.util.module_from_spec(_spec)
sys.modules["check_anchor_provenance"] = cap
_spec.loader.exec_module(cap)

FACTS = json.load(open(os.path.join(REPO, "scripts", "locked_facts.json"), encoding="utf-8"))


# --- the CLEAN case first: a gate that blocks everything passes every planted test ---------

def test_the_live_repo_has_no_stale_valued_anchor_or_pin():
    faults = cap.check()
    assert not faults, (
        f"{len(faults)} anchor(s)/pin(s) contain their own fact's superseded value: "
        f"{faults}. Draw them from the CORRECTED value in locked_facts.json.")


def test_the_check_is_not_vacuous_it_has_a_real_population():
    """A check over an empty population always passes. These are the numbers it ran on."""
    corrected = [k for k, v in FACTS.items()
                 if isinstance(v, dict) and "correction_note" in v and not k.startswith("_")]
    assert len(corrected) >= 50, f"only {len(corrected)} corrected facts found"
    assert len(cap._parse_anchors()) >= 40, "parsed too few committed anchors"
    assert len(cap._parse_pins()) >= 30, "parsed too few committed pins"


# --- the three historical specimens, planted verbatim --------------------------------------

@pytest.mark.parametrize("fact_key,stale_anchor,why", [
    ("efd_threshold_tzs_11m", "milioni kumi na moja",
     "2026-10-06: the regen's 'EFD threshold' critical query required this -- the WORD form of "
     "the fabricated 11,000,000 -- so the gate DEMANDED the fabrication be retrievable. Only "
     "the Swahili word-form limb catches it; the fact's wrong_pattern holds digits."),
    ("nssf_payment_deadline", "ifikapo tarehe 10",
     "2026-10-05: check_facts_index_sync.PINNED required the 10th, which s.14(1) contradicts "
     "and the fact's own verified_by says appears in no source. So the gate did not merely "
     "miss the stale row -- it REQUIRED it."),
    # ⚠️ THE SPECIMEN FOR THIS ONE IS THE SECTION RANGE, NOT 'Part XIII', AND THE REASON IS A
    # FINDING RATHER THAN A CONVENIENCE. The fact's CURRENT text legitimately contains
    # "Part XIII" -- it carries the disambiguation clause "Part XIII is 'General Provisions as
    # to Registration'", which is correct and is the same clause a 2026-10-05 bare-substring
    # check misread as a surviving reversal (CLAUDE.md R34, instance 4). So 'Part XIII' cannot
    # be a stale-value specimen for this fact: the fact asserts that string on purpose.
    # 'ss.320-328' is the unambiguous one -- a section range that corresponds to nothing in any
    # edition of Cap.212 and that the fact asserts nowhere.
    ("act_section_12", "ss.320-328",
     "2026-10-05: wrong_patterns rejected the CORRECT Part XII citation after the reversal was "
     "itself reversed. The range ss.320-328 is winding-up machinery in Part VIII and "
     "corresponds to the foreign-company regime in no edition."),
])
def test_each_historical_stale_anchor_IS_CAUGHT(fact_key, stale_anchor, why):
    assert fact_key in FACTS, f"{fact_key} no longer exists; re-point this specimen"
    faults = cap.check(facts=FACTS,
                       anchors=[("planted guard", stale_anchor)],
                       pins=[(fact_key, stale_anchor)])
    assert faults, (
        f"the check did NOT catch a known-historical stale anchor {stale_anchor!r} for "
        f"{fact_key}.\n{why}\nIf the extraction limbs were narrowed, this is the regression.")
    assert any(f["fact"] == fact_key for f in faults), (
        f"caught {stale_anchor!r} but attributed it to the wrong fact: {faults}")


# --- and the corrected replacements must NOT be caught -------------------------------------

@pytest.mark.parametrize("fact_key,good_anchor", [
    ("efd_threshold_tzs_11m", "EFD haina kizingiti cha mauzo"),
    ("nssf_payment_deadline", "ndani ya MWEZI MMOJA baada ya mwisho wa mwezi"),
    ("act_section_12", "Part XII, ss.437-447"),
    ("fine_limit", "Faini ya juu kabisa kwa kosa la NSSF"),
])
def test_the_corrected_anchors_are_NOT_flagged(fact_key, good_anchor):
    """Positive-only certifies a check that blocks everything. These are the anchors actually
    shipped, and flagging one would block the next regen for being correct -- the expensive
    direction (R21)."""
    faults = cap.check(facts=FACTS,
                       anchors=[("planted guard", good_anchor)],
                       pins=[(fact_key, good_anchor)])
    assert not faults, (
        f"the CORRECTED anchor {good_anchor!r} for {fact_key} was flagged as stale: {faults}. "
        f"An over-broad extractor blocks regens for being right.")


def test_a_figure_correct_in_one_period_is_not_flagged_in_another():
    """⛔ THE FALSE POSITIVE THIS CHECK ALREADY PRODUCED ONCE, pinned.

    `200,000` is a superseded minimum-wage figure. It matched inside `200,000,000 kwa miezi 12`
    -- the VAT-threshold anchor -- under plain substring matching, attributing a wage fact's
    stale value to a VAT guard. Money in this corpus is comma-grouped, so every magnitude is a
    prefix of a larger one and plain substring matching on figures is never right.

    Same trap as `100,000` inside `100,000,000`, which CLAUDE.md records three times in the OOC
    lists and which bit the NSSF-fine propagation sweep on the same day.
    """
    assert cap._contains("200,000,000 kwa miezi 12", "200,000,000")
    assert not cap._contains("200,000,000 kwa miezi 12", "200,000"), (
        "numeric boundary matching was removed -- a smaller magnitude now matches inside a "
        "larger one, which is the exact false positive this guards")
    # and phrases must still match as substrings, or the true positives stop firing
    assert cap._contains("ifikapo tarehe 10 ya mwezi unaofuata", "tarehe 10")


def test_vat_threshold_200m_keeps_its_legitimate_6_month_figure():
    """A fact may legitimately ASSERT a figure its own wrong_patterns target in a different
    context. vat_threshold_200m states TZS 100,000,000 correctly as the 6-MONTH threshold while
    its wrong_pattern targets 100,000,000 'kwa mwaka'. The extractor must not treat a
    currently-asserted value as superseded, or it flags the fact's own correct text."""
    f = FACTS.get("vat_threshold_200m_july2024_increase")
    assert f, "fact renamed; re-point this test"
    vals = cap.superseded_values(f)
    assert "100,000,000" not in vals, (
        f"100,000,000 was extracted as superseded for this fact, but it ASSERTS that figure as "
        f"the 6-month threshold. Extracted: {sorted(vals)[:8]}")
